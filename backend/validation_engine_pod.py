from sqlalchemy import text
from db import engine


def validate_pod(document_id):

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
        raise Exception("No parsed KV data found for POD document")

    fields = {row.field_key: row.doc_value for row in rows}

    errors = []
    warnings = []

    # -----------------------------
    # Required Fields
    # -----------------------------

    required_fields = [
        "POD Number",
        "Shipment ID",
        "Carrier Name",
        "Carrier SCAC",
        "Actual Delivery Date",
        "Total Weight Received (KG)",
    ]

    for field in required_fields:
        if not fields.get(field):
            errors.append(f"MISSING_{field.upper().replace(' ', '_')}")

    # -----------------------------
    # Weight Check
    # -----------------------------

    try:
        total_weight = float(fields.get("Total Weight Received (KG)", 0))
        if total_weight <= 0:
            errors.append("INVALID_TOTAL_WEIGHT_RECEIVED")
    except:
        errors.append("INVALID_WEIGHT_FORMAT")

    # -----------------------------
    # Delivery Status
    # -----------------------------

    delivery_status = (fields.get("Delivery Status") or "").upper()
    if delivery_status not in ["COMPLETE", "PARTIAL"]:
        warnings.append("DELIVERY_STATUS_UNRECOGNIZED")

    # -----------------------------
    # OS&D Flag
    # -----------------------------

    osd_flag = (fields.get("OS&D Flag") or "").upper()
    if osd_flag not in ["YES", "NO", "Y", "N"]:
        warnings.append("OSD_FLAG_FORMAT_UNRECOGNIZED")

    is_valid = len(errors) == 0

    return {
        "document_id": str(document_id),
        "document_type": "POD",
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
    }
