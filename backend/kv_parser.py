def parse_kv_from_lines(rows):

    parsed = {
        "document_type": None,
        "fields": {},
        "cargo_table": [],
        "receipt_table": []
    }

    for row in rows:

        # --------------------------------
        # Detect document type
        # --------------------------------
        if len(row) == 1:
            if "BILL OF LADING" in row[0]:
                parsed["document_type"] = "BOL"
            if "PROOF OF DELIVERY" in row[0]:
                parsed["document_type"] = "POD"

        # --------------------------------
        # KV rows (2-column format)
        # --------------------------------
        if len(row) == 2 and row[0].endswith(":"):
            key = row[0][:-1].strip()
            value = row[1].strip()
            parsed["fields"][key] = value

        # --------------------------------
        # Cargo table rows (8 columns)
        # --------------------------------
        if parsed["document_type"] == "BOL" and len(row) == 8:
            if row[0].isdigit():
                parsed["cargo_table"].append({
                    "line": row[0],
                    "description": row[1],
                    "nmfc": row[2],
                    "class": row[3],
                    "package_type": row[4],
                    "quantity": row[5],
                    "weight": row[6],
                    "hazmat": row[7]
                })

        # --------------------------------
        # Receipt table rows (4 columns)
        # --------------------------------
        if parsed["document_type"] == "POD" and len(row) == 4:
            if row[0].isdigit():
                parsed["receipt_table"].append({
                    "line": row[0],
                    "packages_shipped": row[1],
                    "packages_received": row[2],
                    "damaged": row[3]
                })

    return parsed
