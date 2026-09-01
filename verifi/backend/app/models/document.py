from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.enums import DocumentType, DocumentStatus


class Document(BaseModel):
    id: str  # e.g., "DOC-001"
    bid_id: str
    bidder_id: str
    file_name: str
    original_file_name: str
    file_path: str
    file_size_bytes: int
    mime_type: str = "application/pdf"
    document_type: DocumentType = DocumentType.UNKNOWN
    status: DocumentStatus = DocumentStatus.UPLOADED
    ocr_text: Optional[str] = None
    extracted_facts: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
