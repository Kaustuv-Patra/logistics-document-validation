from sqlalchemy import text
from db import engine


WEIGHT_TOLERANCE = 0.02  # 2% variance allowed


def reconcile_shipment(shipment_id: str):

    with engine.connect() as connection:

        # --------------------------------------------------
        # Fetch VALIDATED BOL
        # --------------------------------------------------
        bol = connection.execute(
            text("""
                SELECT document_id
                FROM documents
                WHERE shipment_id = :shipment_id
                AND document_type = 'BOL'
                AND document_state = 'VALIDATED_PASS'
                LIMIT 1
            """),
            {"shipment_id": shipment_id},
        ).fetchone()

        # --------------------------------------------------
        # Fetch VALIDATED POD
        # --------------------------------------------------
        pod = connection.execute(
            text("""
                SELECT document_id
                FROM documents
                WHERE shipment_id = :shipment_id
                AND document_type = 'POD'
                AND document_state = 'VALIDATED_PASS'
                LIMIT 1
            """),
            {"shipment_id": shipment_id},
        ).fetchone()

        if not bol or not pod:
            raise Exception(
                "Both VALIDATED_PASS BOL and POD required for reconciliation"
            )

        # --------------------------------------------------
        # Fetch KV for BOL
        # --------------------------------------------------
        bol_kv = connection.execute(
            text("""
                SELECT field_key, doc_value
                FROM document_kv
                WHERE document_id = :doc_id
            """),
            {"doc_id": bol.document_id},
        ).fetchall()

        # --------------------------------------------------
        # Fetch KV for POD
        # --------------------------------------------------
        pod_kv = connection.execute(
            text("""
                SELECT field_key, doc_value
                FROM document_kv
                WHERE document_id = :doc_id
            """),
            {"doc_id": pod.document_id},
        ).fetchall()

    # Convert to dictionary
    bol_data = {row.field_key: row.doc_value for row in bol_kv}
    pod_data = {row.field_key: row.doc_value for row in pod_kv}

    errors = []
    warnings = []

    # ==================================================
    # Identity Validation
    # ==================================================

    if bol_data.get("Carrier SCAC") != pod_data.get("Carrier SCAC"):
        errors.append("CARRIER_SCAC_MISMATCH")

    if bol_data.get("Shipment ID") != pod_data.get("Shipment ID"):
        errors.append("SHIPMENT_ID_MISMATCH")

    # ==================================================
    # Weight Reconciliation
    # ==================================================

    try:
        bol_weight = float(bol_data.get("Total Weight (KG)", 0) or 0)
        pod_weight = float(pod_data.get("Total Weight Received (KG)", 0) or 0)

        if bol_weight > 0:
            variance = abs(bol_weight - pod_weight) / bol_weight
            if variance > WEIGHT_TOLERANCE:
                errors.append("WEIGHT_VARIANCE_EXCEEDED")

    except Exception:
        errors.append("WEIGHT_RECONCILIATION_ERROR")

    # ==================================================
    # Package Reconciliation
    # ==================================================

    bol_packages = 0
    pod_shipped = 0
    pod_received = 0
    total_damaged = 0

    # Count BOL cargo quantities
    for key, value in bol_data.items():
        if key.startswith("cargo_line_") and key.endswith("_quantity"):
            try:
                bol_packages += int(value)
            except Exception:
                errors.append("BOL_PACKAGE_PARSE_ERROR")

    # Count POD receipt quantities
    for key, value in pod_data.items():
        if key.startswith("receipt_line_") and key.endswith("_packages_shipped"):
            try:
                pod_shipped += int(value)
            except Exception:
                errors.append("POD_SHIPPED_PARSE_ERROR")

        if key.startswith("receipt_line_") and key.endswith("_packages_received"):
            try:
                pod_received += int(value)
            except Exception:
                errors.append("POD_RECEIVED_PARSE_ERROR")

        if key.startswith("receipt_line_") and key.endswith("_damaged"):
            try:
                total_damaged += int(value)
            except Exception:
                errors.append("POD_DAMAGE_PARSE_ERROR")

    if bol_packages != pod_shipped:
        errors.append("PACKAGE_SHIPPED_MISMATCH")

    if pod_received > pod_shipped:
        errors.append("RECEIVED_EXCEEDS_SHIPPED")

    if total_damaged > 0:
        warnings.append("DAMAGE_REPORTED")

    # ==================================================
    # Final Result
    # ==================================================

    is_reconciled = len(errors) == 0

    return {
        "shipment_id": shipment_id,
        "is_reconciled": is_reconciled,
        "errors": errors,
        "warnings": warnings,
        "bol_document_id": str(bol.document_id),
        "pod_document_id": str(pod.document_id),
    }
