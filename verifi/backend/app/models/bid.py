from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.enums import VerificationStatus, RiskLevel


class Bid(BaseModel):
    id: str  # e.g., "BID-001"
    tender_id: str
    bidder_id: str
    bid_number: str
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "SUBMITTED"  # SUBMITTED, IN_VERIFICATION, VERIFIED, DECIDED
    latest_verification_run_id: Optional[str] = None
    latest_score: Optional[float] = None
    latest_risk_level: Optional[RiskLevel] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
