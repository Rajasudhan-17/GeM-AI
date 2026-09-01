from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.core.enums import DocumentType
from app.schemas.document import DocumentUploadResponse
from app.services.document_service import DocumentService
from app.dependencies import get_document_service

router = APIRouter(tags=["Documents"])


@router.post("/bids/{bid_id}/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    bid_id: str,
    file: UploadFile = File(...),
    document_type: Optional[DocumentType] = Form(None),
    document_service: DocumentService = Depends(get_document_service),
):
    doc = await document_service.upload_document(
        bid_id=bid_id,
        file=file,
        document_type_hint=document_type,
    )
    return DocumentUploadResponse(
        document_id=doc.id,
        file_name=doc.file_name,
        document_type=doc.document_type,
        status=doc.status,
        message="Document uploaded and processed successfully.",
    )
