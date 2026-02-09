from pydantic import BaseModel, Field
from uuid import UUID


class DocumentCreate(BaseModel):
    document_id: UUID
    shipment_id: str = Field(..., min_length=1, max_length=64)
    document_type: str = Field(..., pattern="^(BOL|POD)$")
