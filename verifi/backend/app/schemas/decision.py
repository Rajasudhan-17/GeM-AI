from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.core.enums import DecisionEnum, RiskLevel


class DecisionCreateRequest(BaseModel):
    decision: DecisionEnum  # ACCEPTED / REJECTED
    reason: str = Field(..., min_length=5, description="Mandatory decision rationale")
    officer_id: Optional[str] = "OFFICER-001"
    officer_name: Optional[str] = "Evaluation Officer"


class DecisionResponse(BaseModel):
    id: str
    bid_id: str
    bidder_id: str
    decision: DecisionEnum
    reason: str
    officer_id: str
    officer_name: str
    score_at_decision: float
    risk_at_decision: RiskLevel
    verification_run_id: str
    created_at: datetime


class DecisionHistoryResponse(BaseModel):
    bid_id: str
    current_decision: Optional[DecisionResponse] = None
    history: List[DecisionResponse] = []
