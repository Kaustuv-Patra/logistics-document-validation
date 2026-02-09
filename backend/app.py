from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from db import engine
from schemas import DocumentCreate
from repository import insert_document_with_audit

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
