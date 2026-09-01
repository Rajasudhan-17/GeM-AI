from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.core.enums import RiskLevel, VerificationStatus


class BidResponse(BaseModel):
    id: str
    tender_id: str
    bidder_id: str
    bidder_name: Optional[str] = None
    bid_number: str
    submitted_at: datetime
    status: str
    latest_verification_run_id: Optional[str] = None
    latest_score: Optional[float] = None
    latest_risk_level: Optional[RiskLevel] = None


class BidSummaryResponse(BaseModel):
    bid_id: str
    bidder_id: str
    bidder_name: str
    tender_number: str
    tender_title: str
    submitted_at: datetime
    status: str
    verification_run_id: Optional[str] = None
    score: Optional[float] = None
    risk_level: Optional[RiskLevel] = None
    passed_checks: int = 0
    failed_checks: int = 0
    review_checks: int = 0
    na_checks: int = 0
    total_checks: int = 0
    documents_count: int = 0
    latest_decision: Optional[str] = None
