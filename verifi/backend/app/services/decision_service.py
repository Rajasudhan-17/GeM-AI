import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.core.enums import DecisionEnum, AuditAction
from app.core.exceptions import EntityNotFoundException, BadRequestException
from app.models.decision import ProcurementDecision
from app.repositories.base import (
    DecisionRepository,
    BidRepository,
    VerificationRepository,
)
from app.services.audit_service import AuditService


class DecisionService:
    def __init__(
        self,
        decision_repo: DecisionRepository,
        bid_repo: BidRepository,
        verification_repo: VerificationRepository,
        audit_service: AuditService,
    ):
        self.decision_repo = decision_repo
        self.bid_repo = bid_repo
        self.verification_repo = verification_repo
        self.audit_service = audit_service

    async def record_decision(
        self,
        bid_id: str,
        decision: DecisionEnum,
        reason: str,
        officer_id: str = "OFFICER-001",
        officer_name: str = "Evaluation Officer",
    ) -> ProcurementDecision:
        if not reason or len(reason.strip()) < 5:
            raise BadRequestException("A detailed justification reason is mandatory for officer decisions.")

        bid = await self.bid_repo.get_by_id(bid_id)
        if not bid:
            raise EntityNotFoundException("Bid", bid_id)

        latest_run = await self.verification_repo.get_latest_run_by_bid_id(bid_id)
        if not latest_run or not latest_run.score or not latest_run.risk_assessment:
            raise BadRequestException("Cannot make a decision before a verification run is completed.")

        decision_record = ProcurementDecision(
            id=f"DEC-{uuid.uuid4().hex[:8]}",
            bid_id=bid_id,
            bidder_id=bid.bidder_id,
            decision=decision,
            reason=reason.strip(),
            officer_id=officer_id,
            officer_name=officer_name,
            score_at_decision=latest_run.score.total_score,
            risk_at_decision=latest_run.risk_assessment.risk_level,
            verification_run_id=latest_run.id,
            created_at=datetime.now(timezone.utc),
        )

        saved = await self.decision_repo.save(decision_record)

        # Update bid status
        bid.status = f"DECIDED_{decision.value}"
        bid.updated_at = datetime.now(timezone.utc)
        await self.bid_repo.save(bid)

        # Emit audit event
        await self.audit_service.log_event(
            action=AuditAction.DECISION_SUBMITTED,
            entity_type="DECISION",
            entity_id=saved.id,
            correlation_id=latest_run.correlation_id,
            actor=f"{officer_name} ({officer_id})",
            metadata={
                "bid_id": bid_id,
                "bidder_id": bid.bidder_id,
                "decision": decision.value,
                "reason": reason,
                "score_at_decision": latest_run.score.total_score,
                "risk_at_decision": latest_run.risk_assessment.risk_level.value,
            },
        )

        return saved

    async def get_latest_decision(self, bid_id: str) -> Optional[ProcurementDecision]:
        return await self.decision_repo.get_by_bid_id(bid_id)

    async def get_decision_history(self, bid_id: str) -> List[ProcurementDecision]:
        return await self.decision_repo.get_history_by_bid_id(bid_id)
