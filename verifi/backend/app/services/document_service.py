import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import UploadFile
from app.core.enums import DocumentType, DocumentStatus, AuditAction
from app.core.exceptions import BadRequestException, EntityNotFoundException
from app.models.document import Document
from app.repositories.base import DocumentRepository, BidRepository
from app.storage.base import DocumentStorage
from app.ocr.service import ocr_service
from app.extraction.classifier import classifier
from app.extraction.extractor import structured_extractor
from app.services.audit_service import AuditService
from app.config import settings


class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        bid_repo: BidRepository,
        storage: DocumentStorage,
        audit_service: AuditService,
    ):
        self.document_repo = document_repo
        self.bid_repo = bid_repo
        self.storage = storage
        self.audit_service = audit_service

    async def get_documents_by_bid_id(self, bid_id: str) -> List[Document]:
        return await self.document_repo.get_by_bid_id(bid_id)

    async def get_document_by_id(self, document_id: str) -> Document:
        doc = await self.document_repo.get_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document", document_id)
        return doc

    async def upload_document(
        self,
        bid_id: str,
        file: UploadFile,
        document_type_hint: Optional[DocumentType] = None,
        actor: str = "OFFICER",
    ) -> Document:
        bid = await self.bid_repo.get_by_id(bid_id)
        if not bid:
            raise EntityNotFoundException("Bid", bid_id)

        # Validate file size and extension
        filename = file.filename or "uploaded_doc.pdf"
        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise BadRequestException(f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB.")

        # Save to storage
        stored_path = await self.storage.save_file(
            file_bytes=file_bytes,
            filename=filename,
            subdirectory=f"bids/{bid_id}",
        )

        # Extract text via OCR
        ocr_text, ocr_method = ocr_service.process_document(file_bytes, filename)

        # Classify document type
        if document_type_hint and document_type_hint != DocumentType.UNKNOWN:
            doc_type = document_type_hint
        else:
            doc_type = classifier.classify(ocr_text, filename_hint=filename)

        # Extract structured facts
        extracted_facts = structured_extractor.extract(ocr_text, doc_type)

        doc_id = f"DOC-{uuid.uuid4().hex[:8]}"
        doc = Document(
            id=doc_id,
            bid_id=bid_id,
            bidder_id=bid.bidder_id,
            file_name=filename,
            original_file_name=filename,
            file_path=stored_path,
            file_size_bytes=file_size,
            mime_type=file.content_type or "application/pdf",
            document_type=doc_type,
            status=DocumentStatus.PROCESSED,
            ocr_text=ocr_text,
            extracted_facts=extracted_facts,
            metadata={"ocr_method": ocr_method},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        saved = await self.document_repo.save(doc)

        # Log audit events
        corr_id = bid.latest_verification_run_id or f"CORR-{uuid.uuid4().hex[:6]}"
        await self.audit_service.log_event(
            action=AuditAction.DOCUMENT_UPLOADED,
            entity_type="DOCUMENT",
            entity_id=saved.id,
            correlation_id=corr_id,
            actor=actor,
            metadata={
                "filename": filename,
                "file_size": file_size,
                "document_type": doc_type.value,
                "bid_id": bid_id,
            },
        )

        return saved
