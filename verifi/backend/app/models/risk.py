from datetime import datetime, timezone
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.core.enums import RiskLevel


class RiskFactor(BaseModel):
    category: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    impact: str


class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    risk_score: float  # Composite risk score
    primary_risk_drivers: List[str] = Field(default_factory=list)
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
