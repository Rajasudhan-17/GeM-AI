from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.core.enums import (
    VerificationStatus,
    VerificationRunStatus,
    RiskLevel,
    DocumentType,
)
from app.models.score import ComplianceScore
from app.models.risk import RiskAssessment


class ExtractedFacts(BaseModel):
    document_id: Optional[str] = None
    document_type: DocumentType = DocumentType.UNKNOWN
    raw_facts: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0


class SourceFacts(BaseModel):
    source_name: str
    status: str  # AVAILABLE, UNAVAILABLE, ERROR
    facts: Dict[str, Any] = Field(default_factory=dict)
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FactComparison(BaseModel):
    matched: bool
    discrepancies: List[str] = Field(default_factory=list)
    field_comparisons: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class VerificationCheck(BaseModel):
    id: str  # e.g., "CHK-001"
    run_id: str
    requirement_code: str  # e.g., "REQ-GST-001"
    rule_code: str  # e.g., "GST-001"
    check_name: str
    document_type: DocumentType
    document_id: Optional[str] = None
    status: VerificationStatus  # PASS, FAIL, REVIEW, NOT_APPLICABLE
    extracted_facts: Optional[Dict[str, Any]] = None
    source_facts: Optional[Dict[str, Any]] = None
    fact_comparison: Optional[FactComparison] = None
    reason: str = ""
    evidence: Dict[str, Any] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIRecommendation(BaseModel):
    summary: str
    risk_explanation: str
    key_findings: List[str] = Field(default_factory=list)
    suggested_action: str = ""  # ACCEPT / REJECT / FURTHER_INSPECTION
    drafted_reason: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerificationRun(BaseModel):
    id: str  # e.g., "VR-0001"
    bid_id: str
    bidder_id: str
    correlation_id: str
    status: VerificationRunStatus = VerificationRunStatus.PENDING
    current_stage: str = "PENDING"
    progress_pct: int = 0
    checks: List[VerificationCheck] = Field(default_factory=list)
    score: Optional[ComplianceScore] = None
    risk_assessment: Optional[RiskAssessment] = None
    ai_recommendation: Optional[AIRecommendation] = None
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
