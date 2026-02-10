from sqlalchemy import text
from uuid import UUID, uuid4
from typing import Optional, Dict, Any

from db import engine


def write_audit_event(
    *,
    document_id: UUID,
    event_type: str,
    actor_role: str,
    actor_id: str,
    before_state: Optional[Dict[str, Any]],
    after_state: Optional[Dict[str, Any]],
):
    query = text("""
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
            :event_type,
            :actor_role,
            :actor_id,
            :before_state::jsonb,
            :after_state::jsonb
        )
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "audit_id": uuid4(),
                "document_id": document_id,
                "event_type": event_type,
                "actor_role": actor_role,
                "actor_id": actor_id,
                "before_state": before_state,
                "after_state": after_state,
            },
        )
