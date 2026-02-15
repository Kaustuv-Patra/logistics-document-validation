from sqlalchemy import text
from db import engine


ALLOWED_TRANSITIONS = {
    "INGESTED": {"FILE_UPLOADED"},
    "FILE_UPLOADED": {"PARSED"},
    "PARSED": {"VALIDATED_PASS", "VALIDATED_FAIL"},
    "VALIDATED_FAIL": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"APPROVED", "REJECTED"},
    "VALIDATED_PASS": {"APPROVED"},
}


def transition_document_state(document_id, new_state):

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
            raise Exception("Document not found")

        current_state = result.document_state

        allowed_next = ALLOWED_TRANSITIONS.get(current_state, set())

        if new_state not in allowed_next:
            raise Exception(
                f"Invalid state transition: {current_state} → {new_state}"
            )

        connection.execute(
            text("""
                UPDATE documents
                SET document_state = :new_state
                WHERE document_id = :document_id
            """),
            {
                "new_state": new_state,
                "document_id": document_id,
            },
        )

        return {
            "previous_state": current_state,
            "new_state": new_state
        }
