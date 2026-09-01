from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.core.enums import DocumentType


class TenderRequirementResponse(BaseModel):
    id: str
    tender_id: str
    code: str
    name: str
    document_type: DocumentType
    rule_code: str
    is_mandatory: bool
    weight: float
    description: str


class TenderResponse(BaseModel):
    id: str
    tender_number: str
    title: str
    category: str
    description: str
    organization: str
    estimated_value_inr: float
    closing_date: Optional[datetime] = None
    requirements: List[TenderRequirementResponse] = []
    created_at: datetime
