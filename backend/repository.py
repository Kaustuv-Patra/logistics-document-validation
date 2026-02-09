from sqlalchemy import text
from uuid import UUID

from db import engine


def insert_document(
    document_id: UUID,
    shipment_id: str,
    document_type: str,
):
    query = text("""
        INSERT INTO documents (
            document_id,
            shipment_id,
            document_type,
            document_state
        )
        VALUES (
            :document_id,
            :shipment_id,
            :document_type,
            'INGESTED'
        )
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "document_id": document_id,
                "shipment_id": shipment_id,
                "document_type": document_type,
            },
        )
