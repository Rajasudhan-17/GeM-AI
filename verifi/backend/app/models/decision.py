from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.enums import DecisionEnum, RiskLevel


class ProcurementDecision(BaseModel):
    id: str  # e.g., "DEC-001"
    bid_id: str
    bidder_id: str
    decision: DecisionEnum  # ACCEPTED / REJECTED
    reason: str  # Mandatory officer justification
    officer_id: str = "OFFICER-001"
    officer_name: str = "Evaluation Officer"
    score_at_decision: float
    risk_at_decision: RiskLevel
    verification_run_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
