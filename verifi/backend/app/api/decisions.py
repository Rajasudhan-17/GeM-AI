from typing import Optional
from fastapi import APIRouter, Depends
from app.schemas.decision import (
    DecisionCreateRequest,
    DecisionResponse,
    DecisionHistoryResponse,
)
from app.services.decision_service import DecisionService
from app.dependencies import get_decision_service

router = APIRouter(tags=["Decisions"])


@router.post("/bids/{bid_id}/decision", response_model=DecisionResponse)
async def submit_officer_decision(
    bid_id: str,
    request: DecisionCreateRequest,
    decision_service: DecisionService = Depends(get_decision_service),
):
    decision = await decision_service.record_decision(
        bid_id=bid_id,
        decision=request.decision,
        reason=request.reason,
        officer_id=request.officer_id or "OFFICER-001",
        officer_name=request.officer_name or "Evaluation Officer",
    )
    return DecisionResponse(
        id=decision.id,
        bid_id=decision.bid_id,
        bidder_id=decision.bidder_id,
        decision=decision.decision,
        reason=decision.reason,
        officer_id=decision.officer_id,
        officer_name=decision.officer_name,
        score_at_decision=decision.score_at_decision,
        risk_at_decision=decision.risk_at_decision,
        verification_run_id=decision.verification_run_id,
        created_at=decision.created_at,
    )


@router.get("/bids/{bid_id}/decision", response_model=DecisionHistoryResponse)
async def get_officer_decision(
    bid_id: str,
    decision_service: DecisionService = Depends(get_decision_service),
):
    latest = await decision_service.get_latest_decision(bid_id)
    history = await decision_service.get_decision_history(bid_id)

    latest_res = None
    if latest:
        latest_res = DecisionResponse(
            id=latest.id,
            bid_id=latest.bid_id,
            bidder_id=latest.bidder_id,
            decision=latest.decision,
            reason=latest.reason,
            officer_id=latest.officer_id,
            officer_name=latest.officer_name,
            score_at_decision=latest.score_at_decision,
            risk_at_decision=latest.risk_at_decision,
            verification_run_id=latest.verification_run_id,
            created_at=latest.created_at,
        )

    history_res = [
        DecisionResponse(
            id=d.id,
            bid_id=d.bid_id,
            bidder_id=d.bidder_id,
            decision=d.decision,
            reason=d.reason,
            officer_id=d.officer_id,
            officer_name=d.officer_name,
            score_at_decision=d.score_at_decision,
            risk_at_decision=d.risk_at_decision,
            verification_run_id=d.verification_run_id,
            created_at=d.created_at,
        )
        for d in history
    ]

    return DecisionHistoryResponse(
        bid_id=bid_id,
        current_decision=latest_res,
        history=history_res,
    )
