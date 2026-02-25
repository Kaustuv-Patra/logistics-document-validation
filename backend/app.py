from fastapi import FastAPI, HTTPException, UploadFile, File
from sqlalchemy import text
from uuid import UUID
import os

from db import engine
from schemas import DocumentCreate
from repository import insert_document_with_audit
from ocr_service import extract_text_from_pdf
from kv_parser import parse_kv_from_lines
from validation_engine import validate_bol
from validation_engine_pod import validate_pod
from reconciliation_engine import reconcile_shipment
from shipment_service import (
    get_reconciliation_history,
    get_shipment_dashboard
)

# ------------------------------------------------------------------
# Storage Configuration
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "storage", "raw"))

app = FastAPI(title="Logistics Document Validation API")


# ------------------------------------------------------------------
# Health Endpoints
# ------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db/health")
def db_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar_one()
    return {"db": "ok", "result": value}


# ------------------------------------------------------------------
# Document Creation
# ------------------------------------------------------------------

@app.post("/documents")
def create_document(payload: DocumentCreate):

    try:
        insert_document_with_audit(
            document_id=payload.document_id,
            shipment_id=payload.shipment_id,
            document_type=payload.document_type,
            actor_role="System",
            actor_id="ingestion_api",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "document_id": str(payload.document_id),
        "status": "INGESTED",
    }


# ------------------------------------------------------------------
# File Upload
# ------------------------------------------------------------------

@app.post("/documents/{document_id}/file")
def upload_document_file(document_id: UUID, file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    os.makedirs(STORAGE_ROOT, exist_ok=True)
    file_path = os.path.join(STORAGE_ROOT, f"{document_id}.pdf")

    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists for document")

    with engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT document_state
                FROM documents
                WHERE document_id = :document_id
            """),
            {"document_id": document_id},
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Document not found")

        if result.document_state != "INGESTED":
            raise HTTPException(status_code=400, detail="File upload only allowed in INGESTED state")

        # Save file
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Update raw file path
        connection.execute(
            text("""
                UPDATE documents
                SET raw_file_path = :path
                WHERE document_id = :document_id
            """),
            {"path": file_path, "document_id": document_id},
        )

    return {
        "document_id": str(document_id),
        "file_path": file_path,
    }


# ------------------------------------------------------------------
# OCR + Parsing
# ------------------------------------------------------------------

@app.post("/documents/{document_id}/ocr")
def run_ocr(document_id: UUID):

    with engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT raw_file_path
                FROM documents
                WHERE document_id = :document_id
            """),
            {"document_id": document_id},
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Document not found")

        if not result.raw_file_path:
            raise HTTPException(status_code=404, detail="Document file not uploaded")

        if not os.path.exists(result.raw_file_path):
            raise HTTPException(status_code=404, detail="Stored file not found on disk")

        # ---------------------------------------------
        # Extract + Parse
        # ---------------------------------------------

        raw_lines = extract_text_from_pdf(result.raw_file_path)

        if not raw_lines:
            raise HTTPException(status_code=400, detail="No text extracted from PDF")

        parsed_output = parse_kv_from_lines(raw_lines)

        # ---------------------------------------------
        # Clear existing KV rows (idempotent)
        # ---------------------------------------------

        connection.execute(
            text("""
                DELETE FROM document_kv
                WHERE document_id = :document_id
            """),
            {"document_id": document_id},
        )

        # ---------------------------------------------
        # Insert Top-Level Fields
        # ---------------------------------------------

        fields = parsed_output.get("fields", {})

        for key, value in fields.items():
            connection.execute(
                text("""
                    INSERT INTO document_kv (
                        document_id,
                        field_key,
                        doc_value,
                        status,
                        confidence
                    )
                    VALUES (
                        :document_id,
                        :field_key,
                        :doc_value,
                        'PRESENT',
                        1.00
                    )
                """),
                {
                    "document_id": document_id,
                    "field_key": key,
                    "doc_value": value,
                },
            )

        # ---------------------------------------------
        # Insert Cargo Table
        # ---------------------------------------------

        cargo_rows = parsed_output.get("cargo_table", [])

        for idx, row in enumerate(cargo_rows, start=1):
            for col_key, col_value in row.items():
                field_key = f"cargo_line_{idx}_{col_key}"
                connection.execute(
                    text("""
                        INSERT INTO document_kv (
                            document_id,
                            field_key,
                            doc_value,
                            status,
                            confidence
                        )
                        VALUES (
                            :document_id,
                            :field_key,
                            :doc_value,
                            'PRESENT',
                            1.00
                        )
                    """),
                    {
                        "document_id": document_id,
                        "field_key": field_key,
                        "doc_value": col_value,
                    },
                )

        # ---------------------------------------------
        # Insert Receipt Table
        # ---------------------------------------------

        receipt_rows = parsed_output.get("receipt_table", [])

        for idx, row in enumerate(receipt_rows, start=1):
            for col_key, col_value in row.items():
                field_key = f"receipt_line_{idx}_{col_key}"
                connection.execute(
                    text("""
                        INSERT INTO document_kv (
                            document_id,
                            field_key,
                            doc_value,
                            status,
                            confidence
                        )
                        VALUES (
                            :document_id,
                            :field_key,
                            :doc_value,
                            'PRESENT',
                            1.00
                        )
                    """),
                    {
                        "document_id": document_id,
                        "field_key": field_key,
                        "doc_value": col_value,
                    },
                )

        # ---------------------------------------------
        # Move state → PARSED
        # ---------------------------------------------

        connection.execute(
            text("""
                UPDATE documents
                SET document_state = 'PARSED'
                WHERE document_id = :document_id
            """),
            {"document_id": document_id},
        )

    return {
        "document_id": str(document_id),
        "raw_lines_count": len(raw_lines),
        "parsed": parsed_output
    }


# ------------------------------------------------------------------
# Validation Endpoint
# ------------------------------------------------------------------

@app.post("/documents/{document_id}/validate")
def validate_document(document_id: UUID):

    with engine.begin() as connection:

        doc = connection.execute(
            text("""
                SELECT document_type, document_state
                FROM documents
                WHERE document_id = :document_id
            """),
            {"document_id": document_id},
        ).fetchone()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.document_state != "PARSED":
            raise HTTPException(status_code=400, detail="Document must be PARSED before validation")

        if doc.document_type == "BOL":
            result = validate_bol(document_id)
        elif doc.document_type == "POD":
            result = validate_pod(document_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported document type")

        new_state = "VALIDATED_PASS" if result["is_valid"] else "VALIDATED_FAIL"

        connection.execute(
            text("""
                UPDATE documents
                SET document_state = :state
                WHERE document_id = :document_id
            """),
            {"state": new_state, "document_id": document_id},
        )

    result["new_state"] = new_state
    return result


# ------------------------------------------------------------------
# Shipment Reconciliation
# ------------------------------------------------------------------

@app.post("/shipments/{shipment_id}/reconcile")
def reconcile(shipment_id: str):

    try:
        result = reconcile_shipment(shipment_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    new_state = "RECONCILED_PASS" if result["is_reconciled"] else "RECONCILED_FAIL"

    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE documents
                SET document_state = :state
                WHERE shipment_id = :shipment_id
                AND document_state = 'VALIDATED_PASS'
            """),
            {"state": new_state, "shipment_id": shipment_id},
        )

    result["new_state"] = new_state
    return result

@app.get("/shipments/{shipment_id}/reconciliation-history")
def reconciliation_history(shipment_id: str):

    try:
        history = get_reconciliation_history(shipment_id)
        return {
            "shipment_id": shipment_id,
            "reconciliation_runs": history
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/shipments/{shipment_id}")
def shipment_dashboard(shipment_id: str):

    try:
        dashboard = get_shipment_dashboard(shipment_id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))