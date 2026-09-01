from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.enums import DocumentType


class TenderRequirement(BaseModel):
    id: str
    tender_id: str
    code: str  # e.g., "REQ-GST-001"
    name: str  # e.g., "GST Registration Compliance"
    document_type: DocumentType
    rule_code: str  # e.g., "GST-001"
    is_mandatory: bool = True
    weight: float = 15.0
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
