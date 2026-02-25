from sqlalchemy import text
from db import engine
from uuid import uuid4
from datetime import datetime
import json


WEIGHT_TOLERANCE = 0.02  # 2%


def reconcile_shipment(shipment_id: str):

    with engine.begin() as connection:

        # --------------------------------------------------
        # Ensure shipment exists
        # --------------------------------------------------
        connection.execute(
            text("""
                INSERT INTO shipments (shipment_id)
                VALUES (:shipment_id)
                ON CONFLICT (shipment_id) DO NOTHING
            """),
            {"shipment_id": shipment_id},
        )

        # --------------------------------------------------
        # Fetch VALIDATED BOL
        # --------------------------------------------------
        bol = connection.execute(
            text("""
                SELECT document_id
                FROM documents
                WHERE shipment_id = :shipment_id
                AND document_type = 'BOL'
                AND document_state IN (
                    'VALIDATED_PASS',
                    'RECONCILED_PASS',
                    'RECONCILED_FAIL'
                )
                ORDER BY document_id DESC
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
                AND document_state IN (
                    'VALIDATED_PASS',
                    'RECONCILED_PASS',
                    'RECONCILED_FAIL'
                )
                ORDER BY document_id DESC
                LIMIT 1
            """),
            {"shipment_id": shipment_id},
        ).fetchone()

        if not bol or not pod:
            raise Exception(
                "Both VALIDATED_PASS BOL and POD required for reconciliation"
            )

        # --------------------------------------------------
        # Fetch KV Data
        # --------------------------------------------------
        bol_kv = connection.execute(
            text("""
                SELECT field_key, doc_value
                FROM document_kv
                WHERE document_id = :doc_id
            """),
            {"doc_id": bol.document_id},
        ).fetchall()

        pod_kv = connection.execute(
            text("""
                SELECT field_key, doc_value
                FROM document_kv
                WHERE document_id = :doc_id
            """),
            {"doc_id": pod.document_id},
        ).fetchall()

        bol_data = {row.field_key: row.doc_value for row in bol_kv}
        pod_data = {row.field_key: row.doc_value for row in pod_kv}

        errors = []
        warnings = []

        # ==================================================
        # Identity Checks
        # ==================================================
        if bol_data.get("Carrier SCAC") != pod_data.get("Carrier SCAC"):
            errors.append("CARRIER_SCAC_MISMATCH")

        if bol_data.get("Shipment ID") != pod_data.get("Shipment ID"):
            errors.append("SHIPMENT_ID_MISMATCH")

        # ==================================================
        # Weight Reconciliation
        # ==================================================
        weight_variance_percent = 0

        try:
            bol_weight = float(bol_data.get("Total Weight (KG)", 0) or 0)
            pod_weight = float(pod_data.get("Total Weight Received (KG)", 0) or 0)

            if bol_weight > 0:
                variance = abs(bol_weight - pod_weight) / bol_weight
                weight_variance_percent = round(variance * 100, 2)

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

        for key, value in bol_data.items():
            if key.startswith("cargo_line_") and key.endswith("_quantity"):
                try:
                    bol_packages += int(value)
                except Exception:
                    errors.append("BOL_PACKAGE_PARSE_ERROR")

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

        package_delta = bol_packages - pod_shipped

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
        new_state = "RECONCILED_PASS" if is_reconciled else "RECONCILED_FAIL"

        # --------------------------------------------------
        # Insert historical reconciliation record
        # --------------------------------------------------
        connection.execute(
            text("""
                INSERT INTO shipment_reconciliation (
                    reconciliation_id,
                    shipment_id,
                    bol_document_id,
                    pod_document_id,
                    reconciliation_result,
                    errors,
                    warnings,
                    weight_variance_percent,
                    package_delta,
                    reconciled_at
                )
                VALUES (
                    :reconciliation_id,
                    :shipment_id,
                    :bol_document_id,
                    :pod_document_id,
                    :reconciliation_result,
                    :errors,
                    :warnings,
                    :weight_variance_percent,
                    :package_delta,
                    :reconciled_at
                )
            """),
            {
                "reconciliation_id": str(uuid4()),
                "shipment_id": shipment_id,
                "bol_document_id": bol.document_id,
                "pod_document_id": pod.document_id,
                "reconciliation_result": new_state,
                "errors": json.dumps(errors),
                "warnings": json.dumps(warnings),
                "weight_variance_percent": weight_variance_percent,
                "package_delta": package_delta,
                "reconciled_at": datetime.utcnow(),
            },
        )

        # --------------------------------------------------
        # Update shipment state
        # --------------------------------------------------
        connection.execute(
            text("""
                UPDATE shipments
                SET shipment_state = :new_state
                WHERE shipment_id = :shipment_id
            """),
            {
                "shipment_id": shipment_id,
                "new_state": new_state,
            },
        )

    return {
        "shipment_id": shipment_id,
        "is_reconciled": is_reconciled,
        "errors": errors,
        "warnings": warnings,
        "weight_variance_percent": weight_variance_percent,
        "package_delta": package_delta,
        "bol_document_id": str(bol.document_id),
        "pod_document_id": str(pod.document_id),
        "new_state": new_state,
    }