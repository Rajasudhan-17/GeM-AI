from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.core.enums import (
    VerificationStatus,
    VerificationRunStatus,
    RiskLevel,
    DocumentType,
)


class VerificationStartResponse(BaseModel):
    run_id: str
    status: VerificationRunStatus
    correlation_id: str
    message: str


class FactComparisonResponse(BaseModel):
    matched: bool
    discrepancies: List[str] = []
    field_comparisons: Dict[str, Dict[str, Any]] = {}


class VerificationCheckResponse(BaseModel):
    id: str
    run_id: str
    requirement_code: str
    rule_code: str
    check_name: str
    document_type: DocumentType
    document_id: Optional[str] = None
    status: VerificationStatus
    extracted_facts: Optional[Dict[str, Any]] = None
    source_facts: Optional[Dict[str, Any]] = None
    fact_comparison: Optional[FactComparisonResponse] = None
    reason: str
    evidence: Dict[str, Any] = {}
    evaluated_at: datetime


class ScoreComponentResponse(BaseModel):
    requirement_code: str
    rule_code: str
    weight: float
    status: str
    points_awarded: float
    max_possible_points: float
    notes: str


class ComplianceScoreResponse(BaseModel):
    total_score: float
    passed_count: int
    failed_count: int
    review_count: int
    na_count: int
    components: List[ScoreComponentResponse] = []


class RiskFactorResponse(BaseModel):
    category: str
    severity: str
    description: str
    impact: str


class RiskAssessmentResponse(BaseModel):
    risk_level: RiskLevel
    risk_score: float
    primary_risk_drivers: List[str] = []
    risk_factors: List[RiskFactorResponse] = []


class AIRecommendationResponse(BaseModel):
    summary: str
    risk_explanation: str
    key_findings: List[str] = []
    suggested_action: str
    drafted_reason: str


class VerificationRunResponse(BaseModel):
    id: str
    bid_id: str
    bidder_id: str
    correlation_id: str
    status: VerificationRunStatus
    current_stage: str
    progress_pct: int
    checks: List[VerificationCheckResponse] = []
    score: Optional[ComplianceScoreResponse] = None
    risk_assessment: Optional[RiskAssessmentResponse] = None
    ai_recommendation: Optional[AIRecommendationResponse] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
