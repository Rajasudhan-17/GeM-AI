from typing import Dict, Any, List, Optional
from app.ai.provider import mock_ai_provider, AIProvider
from app.schemas.ai import AIDecisionReasonResponse
from app.repositories.base import (
    BidRepository,
    BidderRepository,
    VerificationRepository,
)
from app.core.exceptions import EntityNotFoundException, BadRequestException


class AIReasonGenerator:
    def __init__(
        self,
        bid_repo: BidRepository,
        bidder_repo: BidderRepository,
        verification_repo: VerificationRepository,
        provider: Optional[AIProvider] = None,
    ):
        self.bid_repo = bid_repo
        self.bidder_repo = bidder_repo
        self.verification_repo = verification_repo
        self.provider = provider or mock_ai_provider

    async def generate_reason(self, bid_id: str) -> AIDecisionReasonResponse:
        bid = await self.bid_repo.get_by_id(bid_id)
        if not bid:
            raise EntityNotFoundException("Bid", bid_id)

        bidder = await self.bidder_repo.get_by_id(bid.bidder_id)
        bidder_name = bidder.name if bidder else "Bidder"

        latest_run = await self.verification_repo.get_latest_run_by_bid_id(bid_id)
        if not latest_run or not latest_run.score or not latest_run.risk_assessment:
            raise BadRequestException("Cannot generate decision reason before a verification run is completed.")

        checks_data = [c.model_dump() for c in latest_run.checks]
        score = latest_run.score.total_score
        risk = latest_run.risk_assessment.risk_level.value

        result = await self.provider.draft_decision_reason(
            bidder_name=bidder_name,
            score=score,
            risk_level=risk,
            checks=checks_data,
        )

        return AIDecisionReasonResponse(
            reason=result["reason"],
            suggested_decision=result["suggested_decision"],
            confidence=result.get("confidence", 0.95),
        )
