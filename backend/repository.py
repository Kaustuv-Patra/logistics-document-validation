from sqlalchemy import text
from uuid import UUID, uuid4
from psycopg2.extras import Json

from db import engine


def insert_document_with_audit(
    *,
    document_id: UUID,
    shipment_id: str,
    document_type: str,
    actor_role: str,
    actor_id: str,
):
    before_state = None

    after_state = {
        "document_id": str(document_id),
        "shipment_id": shipment_id,
        "document_type": document_type,
        "document_state": "INGESTED",
    }

    insert_document_query = text("""
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

    insert_audit_query = text("""
        INSERT INTO document_audit_log (
            audit_id,
            document_id,
            event_type,
            actor_role,
            actor_id,
            before_state,
            after_state
        )
        VALUES (
            :audit_id,
            :document_id,
            'document_ingested',
            :actor_role,
            :actor_id,
            :before_state,
            :after_state
        )
    """)

    # 🔒 SINGLE ATOMIC TRANSACTION
    with engine.begin() as connection:
        connection.execute(
            insert_document_query,
            {
                "document_id": document_id,
                "shipment_id": shipment_id,
                "document_type": document_type,
            },
        )

        connection.execute(
            insert_audit_query,
            {
                "audit_id": uuid4(),
                "document_id": document_id,
                "actor_role": actor_role,
                "actor_id": actor_id,
                # psycopg2 Json adapter (CRITICAL)
                "before_state": Json(before_state),
                "after_state": Json(after_state),
            },
        )
