import re


ALLOWED_CLASSES = {"50", "55", "60", "70", "85"}


ERROR_CATALOG = {
    "INVALID_SHIPMENT_ID_FORMAT": {
        "severity": "HARD",
        "category": "FORMAT",
        "message": "Shipment ID does not match required format SHIP-####",
        "blocking": True,
    },
    "PACKAGE_COUNT_MISMATCH": {
        "severity": "HARD",
        "category": "INTEGRITY",
        "message": "Declared package count does not match cargo sum",
        "blocking": True,
    },
    "PACKAGE_COUNT_INVALID": {
        "severity": "SOFT",
        "category": "DATA",
        "message": "Package count field is invalid or unreadable",
        "blocking": False,
    },
    "WEIGHT_MISMATCH": {
        "severity": "HARD",
        "category": "INTEGRITY",
        "message": "Declared total weight does not match cargo weight sum",
        "blocking": True,
    },
    "WEIGHT_INVALID": {
        "severity": "SOFT",
        "category": "DATA",
        "message": "Weight field is invalid or unreadable",
        "blocking": False,
    },
    "INVALID_NMFC_CODE": {
        "severity": "HARD",
        "category": "COMPLIANCE",
        "message": "One or more cargo rows contain invalid NMFC code",
        "blocking": True,
    },
    "INVALID_FREIGHT_CLASS": {
        "severity": "HARD",
        "category": "COMPLIANCE",
        "message": "One or more cargo rows contain invalid freight class",
        "blocking": True,
    },
    "HAZMAT_DECLARATION_MISMATCH": {
        "severity": "HARD",
        "category": "COMPLIANCE",
        "message": "Hazmat cargo detected but header declaration is inconsistent",
        "blocking": True,
    },
    "SEAL_REQUIRED_FOR_PREPAID": {
        "severity": "SOFT",
        "category": "BUSINESS_RULE",
        "message": "Seal number missing for prepaid freight terms",
        "blocking": False,
    },
}


def build_error_object(code):
    meta = ERROR_CATALOG.get(code, {})
    return {
        "code": code,
        "severity": meta.get("severity"),
        "category": meta.get("category"),
        "message": meta.get("message"),
        "blocking": meta.get("blocking"),
    }


def validate_bol(parsed):

    raw_errors = []
    fields = parsed["fields"]
    cargo = parsed["cargo_table"]

    # Rule 1 — Shipment ID format
    shipment_id = fields.get("Shipment ID")
    if not shipment_id or not re.fullmatch(r"SHIP-\d{4}", shipment_id):
        raw_errors.append("INVALID_SHIPMENT_ID_FORMAT")

    # Rule 2 — Package count validation
    try:
        declared_packages = int(fields.get("Total Packages", 0))
        calculated_packages = sum(int(row["quantity"]) for row in cargo)

        if declared_packages != calculated_packages:
            raw_errors.append("PACKAGE_COUNT_MISMATCH")
    except:
        raw_errors.append("PACKAGE_COUNT_INVALID")

    # Rule 3 — Weight validation
    try:
        declared_weight = float(fields.get("Total Weight (KG)", 0))
        calculated_weight = sum(float(row["weight"]) for row in cargo)

        if abs(declared_weight - calculated_weight) > 0.5:
            raw_errors.append("WEIGHT_MISMATCH")
    except:
        raw_errors.append("WEIGHT_INVALID")

    # Rule 4 — NMFC validation
    for row in cargo:
        if not re.fullmatch(r"\d{5}", row["nmfc"]):
            raw_errors.append("INVALID_NMFC_CODE")
            break

    # Rule 5 — Freight class validation
    for row in cargo:
        if row["class"] not in ALLOWED_CLASSES:
            raw_errors.append("INVALID_FREIGHT_CLASS")
            break

    # Rule 6 — Hazmat consistency
    any_hazmat = any(row["hazmat"] == "Y" for row in cargo)
    declared_hazmat = fields.get("Hazardous Materials", "").upper()

    if any_hazmat and declared_hazmat not in {"YES", "Y"}:
        raw_errors.append("HAZMAT_DECLARATION_MISMATCH")

    # Rule 7 — Seal rule
    freight_terms = fields.get("Freight Terms", "")
    seal_number = fields.get("Seal Number")

    if freight_terms == "PREPAID" and not seal_number:
        raw_errors.append("SEAL_REQUIRED_FOR_PREPAID")

    # Build structured error objects
    structured_errors = [build_error_object(code) for code in raw_errors]

    blocking_errors = [e for e in structured_errors if e["blocking"]]

    return {
        "is_valid": len(blocking_errors) == 0,
        "error_count": len(structured_errors),
        "blocking_error_count": len(blocking_errors),
        "errors": structured_errors,
    }
