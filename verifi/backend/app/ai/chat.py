from typing import Dict, Any, List, Optional
from app.ai.provider import mock_ai_provider, AIProvider
from app.schemas.ai import AIChatResponse
from app.repositories.base import (
    BidRepository,
    BidderRepository,
    VerificationRepository,
)
from app.services.audit_service import AuditService
from app.core.enums import AuditAction
from app.core.exceptions import EntityNotFoundException, BadRequestException


class AIChatService:
    def __init__(
        self,
        bid_repo: BidRepository,
        bidder_repo: BidderRepository,
        verification_repo: VerificationRepository,
        audit_service: AuditService,
        provider: Optional[AIProvider] = None,
    ):
        self.bid_repo = bid_repo
        self.bidder_repo = bidder_repo
        self.verification_repo = verification_repo
        self.audit_service = audit_service
        self.provider = provider or mock_ai_provider

    async def chat(
        self,
        bid_id: str,
        message: str,
        focus_check_id: Optional[str] = None,
        actor: str = "OFFICER",
    ) -> AIChatResponse:
        if not message or not message.strip():
            raise BadRequestException("Message cannot be empty.")

        bid = await self.bid_repo.get_by_id(bid_id)
        if not bid:
            raise EntityNotFoundException("Bid", bid_id)

        bidder = await self.bidder_repo.get_by_id(bid.bidder_id)
        bidder_name = bidder.name if bidder else "Bidder"

        latest_run = await self.verification_repo.get_latest_run_by_bid_id(bid_id)
        if not latest_run or not latest_run.score or not latest_run.risk_assessment:
            # Fallback if run not finished
            checks_data = []
            score = 0.0
            risk = "PENDING"
            corr_id = "N/A"
        else:
            checks_data = [c.model_dump() for c in latest_run.checks]
            score = latest_run.score.total_score
            risk = latest_run.risk_assessment.risk_level.value
            corr_id = latest_run.correlation_id

        result = await self.provider.answer_chat(
            message=message.strip(),
            bidder_name=bidder_name,
            score=score,
            risk_level=risk,
            checks=checks_data,
            focus_check_id=focus_check_id,
        )

        # Audit AI Chat interaction
        await self.audit_service.log_event(
            action=AuditAction.AI_CHAT_USED,
            entity_type="BID",
            entity_id=bid_id,
            correlation_id=corr_id,
            actor=actor,
            metadata={
                "question": message,
                "related_checks": result.get("related_checks", []),
            },
        )

        return AIChatResponse(
            answer=result["answer"],
            related_checks=result.get("related_checks", []),
        )
