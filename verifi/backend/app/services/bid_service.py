from typing import List, Optional
from app.models.bid import Bid
from app.schemas.bid import BidSummaryResponse
from app.repositories.base import (
    BidRepository,
    BidderRepository,
    TenderRepository,
    VerificationRepository,
    DocumentRepository,
    DecisionRepository,
)
from app.core.exceptions import EntityNotFoundException


class BidService:
    def __init__(
        self,
        bid_repo: BidRepository,
        bidder_repo: BidderRepository,
        tender_repo: TenderRepository,
        verification_repo: VerificationRepository,
        document_repo: DocumentRepository,
        decision_repo: DecisionRepository,
    ):
        self.bid_repo = bid_repo
        self.bidder_repo = bidder_repo
        self.tender_repo = tender_repo
        self.verification_repo = verification_repo
        self.document_repo = document_repo
        self.decision_repo = decision_repo

    async def get_all_bids(self) -> List[Bid]:
        return await self.bid_repo.get_all()

    async def get_bid_by_id(self, bid_id: str) -> Bid:
        bid = await self.bid_repo.get_by_id(bid_id)
        if not bid:
            raise EntityNotFoundException("Bid", bid_id)
        return bid

    async def get_bid_summary(self, bid_id: str) -> BidSummaryResponse:
        bid = await self.get_bid_by_id(bid_id)
        bidder = await self.bidder_repo.get_by_id(bid.bidder_id)
        tender = await self.tender_repo.get_by_id(bid.tender_id)
        latest_run = await self.verification_repo.get_latest_run_by_bid_id(bid_id)
        docs = await self.document_repo.get_by_bid_id(bid_id)
        decision = await self.decision_repo.get_by_bid_id(bid_id)

        passed = latest_run.score.passed_count if latest_run and latest_run.score else 0
        failed = latest_run.score.failed_count if latest_run and latest_run.score else 0
        review = latest_run.score.review_count if latest_run and latest_run.score else 0
        na = latest_run.score.na_count if latest_run and latest_run.score else 0
        total = len(latest_run.checks) if latest_run else 0

        score_val = latest_run.score.total_score if latest_run and latest_run.score else None
        risk_val = latest_run.risk_assessment.risk_level if latest_run and latest_run.risk_assessment else None

        return BidSummaryResponse(
            bid_id=bid.id,
            bidder_id=bid.bidder_id,
            bidder_name=bidder.name if bidder else bid.bidder_id,
            tender_number=tender.tender_number if tender else bid.tender_id,
            tender_title=tender.title if tender else "N/A",
            submitted_at=bid.submitted_at,
            status=bid.status,
            verification_run_id=latest_run.id if latest_run else None,
            score=score_val,
            risk_level=risk_val,
            passed_checks=passed,
            failed_checks=failed,
            review_checks=review,
            na_checks=na,
            total_checks=total,
            documents_count=len(docs),
            latest_decision=decision.decision.value if decision else None,
        )
