from sqlalchemy import text
from db import engine


def validate_bol(document_id):

    with engine.connect() as connection:
        rows = connection.execute(
            text("""
                SELECT field_key, doc_value
                FROM document_kv
                WHERE document_id = :document_id
            """),
            {"document_id": document_id},
        ).fetchall()

    if not rows:
        raise Exception("No parsed KV data found for BOL document")

    fields = {row.field_key: row.doc_value for row in rows}

    errors = []
    warnings = []

    # -----------------------------
    # Required Fields
    # -----------------------------

    required_fields = [
        "BOL Number",
        "Shipment ID",
        "Carrier Name",
        "Carrier SCAC",
        "Total Packages",
        "Total Weight (KG)",
    ]

    for field in required_fields:
        if not fields.get(field):
            errors.append(f"MISSING_{field.upper().replace(' ', '_')}")

    # -----------------------------
    # Numeric Checks
    # -----------------------------

    try:
        total_packages = int(fields.get("Total Packages", 0))
        if total_packages <= 0:
            errors.append("INVALID_TOTAL_PACKAGES")
    except:
        errors.append("INVALID_TOTAL_PACKAGES_FORMAT")

    try:
        total_weight = float(fields.get("Total Weight (KG)", 0))
        if total_weight <= 0:
            errors.append("INVALID_TOTAL_WEIGHT")
    except:
        errors.append("INVALID_TOTAL_WEIGHT_FORMAT")

    # -----------------------------
    # Hazmat Check
    # -----------------------------

    hazmat = (fields.get("Hazardous Materials") or "").upper()
    if hazmat not in ["YES", "NO", "Y", "N"]:
        warnings.append("HAZMAT_FORMAT_UNRECOGNIZED")

    is_valid = len(errors) == 0

    return {
        "document_id": str(document_id),
        "document_type": "BOL",
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
    }
