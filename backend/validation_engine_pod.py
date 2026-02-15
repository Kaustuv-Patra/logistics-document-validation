def validate_pod(parsed_output: dict) -> dict:
    """
    Performs business validation on parsed POD document.
    Returns structured validation result.
    """

    errors = []
    warnings = []

    fields = parsed_output.get("fields", {})
    receipt_table = parsed_output.get("receipt_table", [])

    # ---------------------------------------------------
    # 1️⃣ Required Fields Check
    # ---------------------------------------------------

    required_fields = [
        "POD Number",
        "Shipment ID",
        "Carrier SCAC",
        "Carrier Tracking (PRO) Number",
        "Actual Delivery Date",
        "Delivery Time",
        "Received By (Signature)",
        "Signatory Printed Name",
        "Total Weight Received (KG)",
        "OS&D Flag",
        "Delivery Status",
    ]

    for field in required_fields:
        if not fields.get(field):
            errors.append(f"MISSING_FIELD_{field.upper().replace(' ', '_')}")

    # ---------------------------------------------------
    # 2️⃣ Receipt Table Validation
    # ---------------------------------------------------

    total_damaged = 0

    for row in receipt_table:
        try:
            shipped = int(row.get("packages_shipped", 0))
            received = int(row.get("packages_received", 0))
            damaged = int(row.get("damaged", 0))
        except ValueError:
            errors.append("INVALID_RECEIPT_NUMERIC_VALUE")
            continue

        if received > shipped:
            errors.append("RECEIVED_EXCEEDS_SHIPPED")

        if damaged > received:
            errors.append("DAMAGED_EXCEEDS_RECEIVED")

        total_damaged += damaged

    # ---------------------------------------------------
    # 3️⃣ OS&D Consistency
    # ---------------------------------------------------

    osd_flag = fields.get("OS&D Flag", "").upper()
    delivery_status = fields.get("Delivery Status", "").upper()

    if total_damaged > 0 and osd_flag != "YES":
        errors.append("OSD_FLAG_MISMATCH")

    if osd_flag == "YES" and delivery_status == "COMPLETE":
        errors.append("INVALID_COMPLETE_STATUS_WITH_OSD")

    # ---------------------------------------------------
    # 4️⃣ Weight Validation
    # ---------------------------------------------------

    try:
        total_weight = float(fields.get("Total Weight Received (KG)", 0))
        if total_weight <= 0:
            errors.append("INVALID_TOTAL_WEIGHT")
    except ValueError:
        errors.append("INVALID_TOTAL_WEIGHT_FORMAT")

    # ---------------------------------------------------
    # 5️⃣ GPS Validation
    # ---------------------------------------------------

    try:
        lat = float(fields.get("GPS Latitude", 0))
        lon = float(fields.get("GPS Longitude", 0))

        if not (-90 <= lat <= 90):
            errors.append("INVALID_GPS_LATITUDE")

        if not (-180 <= lon <= 180):
            errors.append("INVALID_GPS_LONGITUDE")

    except ValueError:
        warnings.append("GPS_FORMAT_INVALID")

    # ---------------------------------------------------
    # 6️⃣ Photo Proof Required
    # ---------------------------------------------------

    if not fields.get("Photo Proof Reference"):
        warnings.append("PHOTO_PROOF_MISSING")

    # ---------------------------------------------------
    # Final Result
    # ---------------------------------------------------

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "errors": list(set(errors)),
        "warnings": list(set(warnings)),
    }
