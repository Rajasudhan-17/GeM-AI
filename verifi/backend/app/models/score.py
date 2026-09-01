from datetime import datetime, timezone
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ScoreComponent(BaseModel):
    requirement_code: str
    rule_code: str
    weight: float
    status: str  # PASS / FAIL / REVIEW / NOT_APPLICABLE
    points_awarded: float
    max_possible_points: float
    notes: str = ""


class ComplianceScore(BaseModel):
    total_score: float  # 0.0 - 100.0
    passed_count: int
    failed_count: int
    review_count: int
    na_count: int
    components: List[ScoreComponent] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
