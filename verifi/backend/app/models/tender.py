from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.requirement import TenderRequirement


class Tender(BaseModel):
    id: str
    tender_number: str  # e.g., "GEM/2026/B/2317045"
    title: str  # e.g., "Supply of Networking Equipment"
    category: str  # e.g., "IT & Networking Hardware"
    description: str = ""
    organization: str = "Government e-Marketplace (GeM)"
    estimated_value_inr: float = 15000000.0  # 1.5 Cr
    closing_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
