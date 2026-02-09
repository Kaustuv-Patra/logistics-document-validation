from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from uuid import UUID

from db import engine
from schemas import DocumentCreate
from repository import insert_document

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
        insert_document(
            document_id=payload.document_id,
            shipment_id=payload.shipment_id,
            document_type=payload.document_type,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "document_id": payload.document_id,
        "status": "INGESTED",
    }
