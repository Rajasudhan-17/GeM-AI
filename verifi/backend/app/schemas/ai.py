from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    message: str
    focus_check_id: Optional[str] = None


class AIChatResponse(BaseModel):
    answer: str
    related_checks: List[str] = []
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIDecisionReasonResponse(BaseModel):
    reason: str
    suggested_decision: str
    confidence: float
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
