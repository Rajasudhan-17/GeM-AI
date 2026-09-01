import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.core.enums import (
    VerificationRunStatus,
    VerificationStatus,
    DocumentStatus,
    DocumentType,
    AuditAction,
)
from app.models.verification import VerificationRun, VerificationCheck
from app.repositories.base import (
    VerificationRepository,
    BidRepository,
    BidderRepository,
    TenderRepository,
    DocumentRepository,
)
from app.storage.base import DocumentStorage
from app.ocr.service import ocr_service
from app.extraction.classifier import classifier
from app.extraction.extractor import structured_extractor
from app.rules.engine import rule_engine
from app.services.scoring_service import scoring_service
from app.services.risk_service import risk_service
from app.ai.explanation import explanation_service
from app.services.audit_service import AuditService
from app.providers.gst import MockGSTProvider
from app.providers.udyam import MockUdyamProvider
from app.providers.pan import MockPANProvider
from app.providers.epfo import MockEPFOProvider
from app.providers.esic import MockESICProvider
from app.providers.oem import MockOEMProvider
from app.providers.digilocker import MockDigiLockerProvider
from app.providers.blacklist import MockBlacklistProvider
from app.core.logging import logger


class VerificationJobRunner:
    def __init__(
        self,
        verification_repo: VerificationRepository,
        bid_repo: BidRepository,
        bidder_repo: BidderRepository,
        tender_repo: TenderRepository,
        document_repo: DocumentRepository,
        storage: DocumentStorage,
        audit_service: AuditService,
    ):
        self.verification_repo = verification_repo
        self.bid_repo = bid_repo
        self.bidder_repo = bidder_repo
        self.tender_repo = tender_repo
        self.document_repo = document_repo
        self.storage = storage
        self.audit_service = audit_service

        # Initialize mock providers
        self.providers = {
            DocumentType.GST: MockGSTProvider(),
            DocumentType.UDYAM: MockUdyamProvider(),
            DocumentType.PAN: MockPANProvider(),
            DocumentType.EPFO: MockEPFOProvider(),
            DocumentType.ESIC: MockESICProvider(),
            DocumentType.OEM: MockOEMProvider(),
            DocumentType.DIGILOCKER: MockDigiLockerProvider(),
            DocumentType.BLACKLIST: MockBlacklistProvider(),
        }

    async def execute_verification_pipeline(self, run_id: str, delay_seconds: float = 0.05) -> None:
        run = await self.verification_repo.get_run_by_id(run_id)
        if not run:
            logger.error(f"Verification run {run_id} not found.")
            return

        correlation_id = run.correlation_id

        try:
            bid = await self.bid_repo.get_by_id(run.bid_id)
            bidder = await self.bidder_repo.get_by_id(run.bidder_id)
            tender = await self.tender_repo.get_by_id(bid.tender_id)
            requirements = await self.tender_repo.get_requirements(tender.id)
            documents = await self.document_repo.get_by_bid_id(bid.id)

            # Stage 1: RUNNING
            run.status = VerificationRunStatus.RUNNING
            run.current_stage = "RUNNING"
            run.progress_pct = 10
            await self.verification_repo.save_run(run)
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            # Stage 2: OCR
            run.status = VerificationRunStatus.OCR
            run.current_stage = "OCR"
            run.progress_pct = 25
            await self.verification_repo.save_run(run)

            await self.audit_service.log_event(
                action=AuditAction.OCR_STARTED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
                metadata={"documents_count": len(documents)},
            )

            for doc in documents:
                if not doc.ocr_text:
                    if await self.storage.file_exists(doc.file_path):
                        file_bytes = await self.storage.get_file_bytes(doc.file_path)
                        text, method = ocr_service.process_document(file_bytes, doc.file_name)
                        doc.ocr_text = text
                        doc.metadata["ocr_method"] = method
                    else:
                        doc.ocr_text = f"Mock text content for {doc.file_name}"
                doc.status = DocumentStatus.PROCESSING
                await self.document_repo.save(doc)

            await self.audit_service.log_event(
                action=AuditAction.OCR_COMPLETED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
                metadata={"processed_docs": len(documents)},
            )
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            # Stage 3: EXTRACTING
            run.status = VerificationRunStatus.EXTRACTING
            run.current_stage = "EXTRACTING"
            run.progress_pct = 40
            await self.verification_repo.save_run(run)

            doc_map: Dict[DocumentType, Document] = {}
            for doc in documents:
                # Classify if unknown
                if doc.document_type == DocumentType.UNKNOWN:
                    doc.document_type = classifier.classify(doc.ocr_text or "", doc.file_name)
                
                # Extract facts
                doc.extracted_facts = structured_extractor.extract(doc.ocr_text or "", doc.document_type)
                doc.status = DocumentStatus.PROCESSED
                await self.document_repo.save(doc)
                doc_map[doc.document_type] = doc

            await self.audit_service.log_event(
                action=AuditAction.FACTS_EXTRACTED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
                metadata={"extracted_types": [k.value for k in doc_map.keys()]},
            )
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            # Stage 4: VERIFYING & Stage 5: RULE_EVALUATION
            run.status = VerificationRunStatus.VERIFYING
            run.current_stage = "VERIFYING"
            run.progress_pct = 60
            await self.verification_repo.save_run(run)

            await self.audit_service.log_event(
                action=AuditAction.SOURCE_VERIFICATION_STARTED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
            )

            checks: List[VerificationCheck] = []

            for req in requirements:
                target_doc = doc_map.get(req.document_type)
                doc_facts = target_doc.extracted_facts if target_doc else None
                doc_id = target_doc.id if target_doc else None

                provider = self.providers.get(req.document_type)
                provider_res = None
                if provider:
                    provider_res = await provider.verify(
                        bidder_id=bidder.id,
                        extracted_facts=doc_facts,
                    )

                check = rule_engine.evaluate(
                    run_id=run.id,
                    requirement_code=req.code,
                    rule_code=req.rule_code,
                    check_name=req.name,
                    document_type=req.document_type,
                    document_id=doc_id,
                    doc_facts=doc_facts,
                    provider_result=provider_res,
                )
                checks.append(check)

            await self.audit_service.log_event(
                action=AuditAction.SOURCE_VERIFICATION_COMPLETED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
                metadata={"checks_evaluated": len(checks)},
            )
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            # Stage 5: RULE_EVALUATION
            run.status = VerificationRunStatus.RULE_EVALUATION
            run.current_stage = "RULE_EVALUATION"
            run.progress_pct = 75
            run.checks = checks
            await self.verification_repo.save_run(run)

            for c in checks:
                await self.audit_service.log_event(
                    action=AuditAction.RULE_EVALUATED,
                    entity_type="VERIFICATION_CHECK",
                    entity_id=c.id,
                    correlation_id=correlation_id,
                    metadata={"rule": c.rule_code, "status": c.status.value, "reason": c.reason},
                )
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            # Stage 6: SCORING
            run.status = VerificationRunStatus.SCORING
            run.current_stage = "SCORING"
            run.progress_pct = 85

            score = scoring_service.calculate_score(checks)
            risk = risk_service.assess_risk(score, checks)

            run.score = score
            run.risk_assessment = risk
            await self.verification_repo.save_run(run)

            await self.audit_service.log_event(
                action=AuditAction.SCORE_CALCULATED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
                metadata={"total_score": score.total_score},
            )
            await self.audit_service.log_event(
                action=AuditAction.RISK_CALCULATED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
                metadata={"risk_level": risk.risk_level.value, "risk_score": risk.risk_score},
            )
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            # Stage 7: AI_ANALYSIS
            run.status = VerificationRunStatus.AI_ANALYSIS
            run.current_stage = "AI_ANALYSIS"
            run.progress_pct = 95
            await self.verification_repo.save_run(run)

            ai_rec = await explanation_service.generate_run_explanation(
                bidder_name=bidder.name,
                score=score.total_score,
                risk_level=risk.risk_level.value,
                checks=[c.model_dump() for c in checks],
            )
            run.ai_recommendation = ai_rec
            await self.verification_repo.save_run(run)

            await self.audit_service.log_event(
                action=AuditAction.AI_RECOMMENDATION_GENERATED,
                entity_type="VERIFICATION_RUN",
                entity_id=run.id,
                correlation_id=correlation_id,
                metadata={"suggested_action": ai_rec.suggested_action},
            )
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            # Stage 8: COMPLETED
            run.status = VerificationRunStatus.COMPLETED
            run.current_stage = "COMPLETED"
            run.progress_pct = 100
            run.completed_at = datetime.now(timezone.utc)
            await self.verification_repo.save_run(run)

            # Update Bid record
            bid.status = "VERIFIED"
            bid.latest_verification_run_id = run.id
            bid.latest_score = score.total_score
            bid.latest_risk_level = risk.risk_level
            bid.updated_at = datetime.now(timezone.utc)
            await self.bid_repo.save(bid)

        except Exception as e:
            logger.error(f"Error in verification run {run_id}: {e}", exc_info=True)
            run.status = VerificationRunStatus.FAILED
            run.current_stage = "FAILED"
            run.error_message = str(e)
            run.completed_at = datetime.now(timezone.utc)
            await self.verification_repo.save_run(run)
