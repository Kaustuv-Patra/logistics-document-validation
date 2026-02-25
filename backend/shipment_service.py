from sqlalchemy import text
from db import engine


def get_reconciliation_history(shipment_id: str):

    with engine.connect() as connection:

        rows = connection.execute(
            text("""
                SELECT
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
                FROM shipment_reconciliation
                WHERE shipment_id = :shipment_id
                ORDER BY reconciled_at DESC
            """),
            {"shipment_id": shipment_id},
        ).fetchall()

    history = []

    for row in rows:
        history.append({
            "reconciliation_id": str(row.reconciliation_id),
            "shipment_id": row.shipment_id,
            "bol_document_id": str(row.bol_document_id),
            "pod_document_id": str(row.pod_document_id),
            "reconciliation_result": row.reconciliation_result,
            "errors": row.errors,
            "warnings": row.warnings,
            "weight_variance_percent": float(row.weight_variance_percent or 0),
            "package_delta": row.package_delta,
            "reconciled_at": row.reconciled_at.isoformat(),
        })

    return history


def get_shipment_dashboard(shipment_id: str):

    with engine.connect() as connection:

        shipment = connection.execute(
            text("""
                SELECT shipment_state, created_at
                FROM shipments
                WHERE shipment_id = :shipment_id
            """),
            {"shipment_id": shipment_id},
        ).fetchone()

        if not shipment:
            raise Exception("Shipment not found")

        latest_recon = connection.execute(
            text("""
                SELECT
                    reconciliation_result,
                    weight_variance_percent,
                    package_delta,
                    reconciled_at
                FROM shipment_reconciliation
                WHERE shipment_id = :shipment_id
                ORDER BY reconciled_at DESC
                LIMIT 1
            """),
            {"shipment_id": shipment_id},
        ).fetchone()

        total_runs = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM shipment_reconciliation
                WHERE shipment_id = :shipment_id
            """),
            {"shipment_id": shipment_id},
        ).scalar()

    return {
        "shipment_id": shipment_id,
        "shipment_state": shipment.shipment_state,
        "created_at": shipment.created_at.isoformat(),
        "total_reconciliation_runs": total_runs,
        "latest_reconciliation": {
            "result": latest_recon.reconciliation_result if latest_recon else None,
            "weight_variance_percent": float(latest_recon.weight_variance_percent or 0) if latest_recon else None,
            "package_delta": latest_recon.package_delta if latest_recon else None,
            "reconciled_at": latest_recon.reconciled_at.isoformat() if latest_recon else None,
        }
    }