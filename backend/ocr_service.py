from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


ROW_TOLERANCE = 3.0


def extract_text_from_pdf(file_path):

    elements = []

    for page_layout in extract_pages(file_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    text = text_line.get_text().strip()
                    if text:
                        elements.append({
                            "text": text,
                            "x": text_line.x0,
                            "y": text_line.y0
                        })

    # Sort by Y descending (top to bottom)
    elements.sort(key=lambda e: (-e["y"], e["x"]))

    # Cluster into rows
    rows = []
    current_row = []
    current_y = None

    for element in elements:

        if current_y is None:
            current_row.append(element)
            current_y = element["y"]
            continue

        if abs(element["y"] - current_y) <= ROW_TOLERANCE:
            current_row.append(element)
        else:
            rows.append(current_row)
            current_row = [element]
            current_y = element["y"]

    if current_row:
        rows.append(current_row)

    # Sort each row by X coordinate
    structured_rows = []

    for row in rows:
        row.sort(key=lambda e: e["x"])
        structured_rows.append([e["text"] for e in row])

    return structured_rows
