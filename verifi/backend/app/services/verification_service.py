import uuid
from datetime import datetime, timezone
from typing import Optional, List
from app.core.enums import VerificationRunStatus, VerificationStatus, AuditAction
from app.core.exceptions import EntityNotFoundException, BadRequestException
from app.models.verification import VerificationRun, VerificationCheck
from app.schemas.verification import VerificationStartResponse
from app.repositories.base import (
    VerificationRepository,
    BidRepository,
    BidderRepository,
    TenderRepository,
    DocumentRepository,
)
from app.workers.queue import JobQueue, get_job_queue
from app.workers.verification_job import VerificationJobRunner
from app.services.audit_service import AuditService
from app.storage.base import DocumentStorage
from app.config import settings


class VerificationService:
    def __init__(
        self,
        verification_repo: VerificationRepository,
        bid_repo: BidRepository,
        bidder_repo: BidderRepository,
        tender_repo: TenderRepository,
        document_repo: DocumentRepository,
        storage: DocumentStorage,
        audit_service: AuditService,
        queue: Optional[JobQueue] = None,
    ):
        self.verification_repo = verification_repo
        self.bid_repo = bid_repo
        self.bidder_repo = bidder_repo
        self.tender_repo = tender_repo
        self.document_repo = document_repo
        self.storage = storage
        self.audit_service = audit_service
        self.queue = queue or get_job_queue(settings.QUEUE_MODE)

        self.runner = VerificationJobRunner(
            verification_repo=self.verification_repo,
            bid_repo=self.bid_repo,
            bidder_repo=self.bidder_repo,
            tender_repo=self.tender_repo,
            document_repo=self.document_repo,
            storage=self.storage,
            audit_service=self.audit_service,
        )

    async def start_verification(
        self,
        bid_id: str,
        actor: str = "OFFICER",
        delay_seconds: float = 0.05,
    ) -> VerificationStartResponse:
        bid = await self.bid_repo.get_by_id(bid_id)
        if not bid:
            raise EntityNotFoundException("Bid", bid_id)

        run_id = f"VR-{uuid.uuid4().hex[:8]}"
        correlation_id = run_id

        run = VerificationRun(
            id=run_id,
            bid_id=bid_id,
            bidder_id=bid.bidder_id,
            correlation_id=correlation_id,
            status=VerificationRunStatus.PENDING,
            current_stage="PENDING",
            progress_pct=0,
            started_at=datetime.now(timezone.utc),
        )

        saved_run = await self.verification_repo.save_run(run)

        # Update bid status
        bid.status = "IN_VERIFICATION"
        bid.latest_verification_run_id = run_id
        await self.bid_repo.save(bid)

        # Log audit
        await self.audit_service.log_event(
            action=AuditAction.DOCUMENT_PROCESSING_STARTED,
            entity_type="VERIFICATION_RUN",
            entity_id=run_id,
            correlation_id=correlation_id,
            actor=actor,
            metadata={"bid_id": bid_id, "bidder_id": bid.bidder_id},
        )

        # Enqueue background pipeline execution
        self.queue.enqueue(
            self.runner.execute_verification_pipeline,
            run_id=run_id,
            delay_seconds=delay_seconds,
        )

        return VerificationStartResponse(
            run_id=run_id,
            status=VerificationRunStatus.PENDING,
            correlation_id=correlation_id,
            message="Verification pipeline started in background.",
        )

    async def get_run_by_id(self, run_id: str) -> VerificationRun:
        run = await self.verification_repo.get_run_by_id(run_id)
        if not run:
            raise EntityNotFoundException("VerificationRun", run_id)
        return run

    async def get_check_by_id(self, check_id: str) -> VerificationCheck:
        check = await self.verification_repo.get_check_by_id(check_id)
        if not check:
            raise EntityNotFoundException("VerificationCheck", check_id)
        return check

    async def retry_check(self, check_id: str, actor: str = "OFFICER") -> VerificationCheck:
        check = await self.get_check_by_id(check_id)
        run = await self.get_run_by_id(check.run_id)

        # Log retry event
        await self.audit_service.log_event(
            action=AuditAction.VERIFICATION_RETRIED,
            entity_type="VERIFICATION_CHECK",
            entity_id=check_id,
            correlation_id=run.correlation_id,
            actor=actor,
            metadata={"rule_code": check.rule_code},
        )

        return check
