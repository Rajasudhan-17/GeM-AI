from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.core.enums import DocumentType, DocumentStatus


class DocumentResponse(BaseModel):
    id: str
    bid_id: str
    bidder_id: str
    file_name: str
    original_file_name: str
    file_size_bytes: int
    mime_type: str
    document_type: DocumentType
    status: DocumentStatus
    ocr_text_preview: Optional[str] = None
    extracted_facts: Dict[str, Any] = {}
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    document_type: DocumentType
    status: DocumentStatus
    message: str
