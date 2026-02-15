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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "storage", "raw"))

app = FastAPI(title="Logistics Document Validation API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db/health")
def db_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar_one()
    return {"db": "ok", "result": value}


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
        "document_id": payload.document_id,
        "status": "INGESTED",
    }


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
            raise HTTPException(status_code=400, detail="File upload not allowed in this state")

        with open(file_path, "wb") as f:
            f.write(file.file.read())

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


@app.post("/documents/{document_id}/ocr")
def run_ocr(document_id: UUID):

    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT raw_file_path
                FROM documents
                WHERE document_id = :document_id
            """),
            {"document_id": document_id},
        ).fetchone()

    if not result or not result.raw_file_path:
        raise HTTPException(status_code=404, detail="Document file not found")

    if not os.path.exists(result.raw_file_path):
        raise HTTPException(status_code=404, detail="Stored file not found on disk")

    raw_lines = extract_text_from_pdf(result.raw_file_path)

    if not raw_lines:
        raise HTTPException(status_code=400, detail="No text extracted from PDF")

    parsed_output = parse_kv_from_lines(raw_lines)

    validation_result = None
    new_state = "PARSED"

    if parsed_output["document_type"] == "BOL":
        validation_result = validate_bol(parsed_output)
        new_state = "VALIDATED_PASS" if validation_result["is_valid"] else "VALIDATED_FAIL"

    elif parsed_output["document_type"] == "POD":
        validation_result = validate_pod(parsed_output)
        new_state = "VALIDATED_PASS" if validation_result["is_valid"] else "VALIDATED_FAIL"

    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE documents
                SET document_state = :state
                WHERE document_id = :document_id
            """),
            {"state": new_state, "document_id": document_id},
        )

    return {
        "document_id": str(document_id),
        "parsed": parsed_output,
        "validation": validation_result,
        "new_state": new_state
    }
