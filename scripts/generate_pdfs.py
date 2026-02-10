from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from faker import Faker
import random
import os

fake = Faker()
random.seed(42)

BASE_DIR = os.path.abspath("data/pdf_corpus")

NUM_BOL = 20
NUM_POD = 20


# ------------------ Drawing Helpers ------------------

def draw_section(c, title, y):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30, y, title)
    return y - 15


def draw_kv(c, y, key, value):
    c.setFont("Helvetica-Bold", 9)
    c.drawString(30, y, f"{key}:")
    c.setFont("Helvetica", 9)
    c.drawString(230, y, str(value))
    return y - 12


def draw_grid(c, x_positions, y_start, row_height, rows):
    for i in range(rows + 1):
        c.line(x_positions[0], y_start - i * row_height,
               x_positions[-1], y_start - i * row_height)
    for x in x_positions:
        c.line(x, y_start, x, y_start - rows * row_height)


def draw_table_header(c, x_positions, y, headers):
    c.setFont("Helvetica-Bold", 8)
    for i, header in enumerate(headers):
        c.drawString(x_positions[i] + 3, y, header)


def draw_table_row(c, x_positions, y, row):
    c.setFont("Helvetica", 8)
    for i, cell in enumerate(row):
        c.drawString(x_positions[i] + 3, y, str(cell))


# ------------------ BOL ------------------

def generate_bol(index, shipment_id, carrier_name, carrier_scac):
    path = os.path.join(BASE_DIR, "bol", f"bol_{index}.pdf")
    c = canvas.Canvas(path, pagesize=A4)

    y = 800
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, y, "BILL OF LADING (BOL)")
    y -= 30

    # Shipment Info
    y = draw_section(c, "Shipment Information", y)
    y = draw_kv(c, y, "Document Type", "BOL")
    y = draw_kv(c, y, "BOL Number", f"BOL-{100000 + index}")
    y = draw_kv(c, y, "Shipment ID", shipment_id)
    y = draw_kv(c, y, "Purchase Order Number", f"PO-{50000 + index}")
    y = draw_kv(c, y, "Carrier Name", carrier_name)
    y = draw_kv(c, y, "Carrier SCAC", carrier_scac)
    y = draw_kv(c, y, "NMFC Freight Class", random.choice(["50", "55", "60", "70", "85"]))
    y -= 10

    # Parties
    y = draw_section(c, "Parties", y)
    y = draw_kv(c, y, "Shipper Name", fake.company())
    y = draw_kv(c, y, "Shipper Address", fake.address().replace("\n", ", "))
    y = draw_kv(c, y, "Shipper Phone", fake.phone_number())
    y = draw_kv(c, y, "Consignee Name", fake.company())
    y = draw_kv(c, y, "Consignee Address", fake.address().replace("\n", ", "))
    y = draw_kv(c, y, "Consignee Phone", fake.phone_number())
    y -= 10

    # Cargo & Compliance
    hazmat = random.choice(["YES", "NO"])
    y = draw_section(c, "Cargo & Compliance", y)
    y = draw_kv(c, y, "Hazardous Materials", hazmat)
    if hazmat == "YES":
        y = draw_kv(c, y, "UN/NA Number", f"UN{random.randint(1000, 3500)}")

    y = draw_kv(c, y, "Special Handling Instructions",
                random.choice(["NONE", "FRAGILE", "KEEP FROM FREEZING", "LIFTGATE REQUIRED"]))
    y = draw_kv(c, y, "Declared Value (USD)", round(random.uniform(5000, 50000), 2))
    y = draw_kv(c, y, "Seal Number", fake.bothify("SEAL-#####"))
    y = draw_kv(c, y, "Total Packages", random.randint(5, 40))
    y = draw_kv(c, y, "Total Weight (KG)", round(random.uniform(500, 20000), 2))
    y = draw_kv(c, y, "Freight Terms", random.choice(["PREPAID", "COLLECT"]))

    # Cargo Table
    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30, y, "Cargo Details")
    y -= 15

    headers = [
        "Line",
        "Description",
        "NMFC",
        "Class",
        "Pkg Type",
        "Qty",
        "Weight (KG)",
        "Hazmat"
    ]

    x_positions = [30, 70, 200, 250, 300, 360, 420, 500]
    row_height = 14
    rows = 6

    draw_grid(c, x_positions, y, row_height, rows + 1)
    draw_table_header(c, x_positions, y - 10, headers)

    for i in range(rows):
        row = [
            i + 1,
            fake.word().upper(),
            random.randint(10000, 99999),
            random.choice(["50", "55", "60", "70", "85"]),
            random.choice(["PALLET", "CARTON", "CRATE"]),
            random.randint(1, 10),
            round(random.uniform(50, 500), 2),
            random.choice(["Y", "N"]),
        ]
        draw_table_row(c, x_positions, y - row_height * (i + 2) + 4, row)

    c.showPage()
    c.save()


# ------------------ POD ------------------

def generate_pod(index, shipment_id, carrier_name, carrier_scac):
    path = os.path.join(BASE_DIR, "pod", f"pod_{index}.pdf")
    c = canvas.Canvas(path, pagesize=A4)

    y = 800
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, y, "PROOF OF DELIVERY (POD)")
    y -= 30

    # Delivery Info
    y = draw_section(c, "Delivery Information", y)
    y = draw_kv(c, y, "Document Type", "POD")
    y = draw_kv(c, y, "POD Number", f"POD-{700000 + index}")
    y = draw_kv(c, y, "Shipment ID", shipment_id)
    y = draw_kv(c, y, "Carrier Name", carrier_name)
    y = draw_kv(c, y, "Carrier SCAC", carrier_scac)
    y = draw_kv(c, y, "Carrier Tracking (PRO) Number", fake.bothify("PRO########"))
    y -= 10

    # Receipt Details
    y = draw_section(c, "Receipt Details", y)
    y = draw_kv(c, y, "Actual Delivery Date", fake.date())
    y = draw_kv(c, y, "Delivery Time", fake.time())
    y = draw_kv(c, y, "Received By (Signature)", fake.name())
    y = draw_kv(c, y, "Signatory Printed Name", fake.name())
    y = draw_kv(c, y, "Total Weight Received (KG)", round(random.uniform(500, 20000), 2))
    y = draw_kv(c, y, "OS&D Flag", random.choice(["YES", "NO"]))
    y = draw_kv(c, y, "Delivery Status", random.choice(["DELIVERED", "PARTIAL"]))
    y = draw_kv(c, y, "Exception Code", random.choice(["NONE", "LATE", "DAMAGED"]))
    y -= 10

    # Receipt Summary Table
    y -= 15
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30, y, "Receipt Summary")
    y -= 15

    headers = [
        "Line",
        "Packages Shipped",
        "Packages Received",
        "Damaged"
    ]

    x_positions = [30, 150, 300, 450]
    row_height = 14
    rows = 4

    draw_grid(c, x_positions, y, row_height, rows + 1)
    draw_table_header(c, x_positions, y - 10, headers)

    for i in range(rows):
        shipped = random.randint(5, 15)
        received = shipped if random.choice([True, False]) else shipped - 1
        damaged = 0 if shipped == received else 1

        row = [i + 1, shipped, received, damaged]
        draw_table_row(c, x_positions, y - row_height * (i + 2) + 4, row)

    # Proof & Location
    y -= row_height * (rows + 2)
    y = draw_section(c, "Proof & Location", y)
    y = draw_kv(c, y, "GPS Latitude", round(random.uniform(-90, 90), 6))
    y = draw_kv(c, y, "GPS Longitude", round(random.uniform(-180, 180), 6))
    y = draw_kv(c, y, "Photo Proof Reference", f"PHOTO_{shipment_id}.jpg")

    c.showPage()
    c.save()


# ------------------ Main ------------------

def main():
    os.makedirs(os.path.join(BASE_DIR, "bol"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "pod"), exist_ok=True)

    for i in range(NUM_BOL):
        shipment_id = f"SHIP-{3000 + i}"
        carrier_name = random.choice(["Maersk", "DHL", "FedEx Freight", "Blue Dart"])
        carrier_scac = fake.lexify("????")

        generate_bol(i, shipment_id, carrier_name, carrier_scac)
        generate_pod(i, shipment_id, carrier_name, carrier_scac)

    print("High-fidelity BOL & POD PDF corpus generated with tables.")


if __name__ == "__main__":
    main()
