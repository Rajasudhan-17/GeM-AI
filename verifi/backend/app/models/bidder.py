from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Bidder(BaseModel):
    id: str  # e.g., "BDR-77291"
    name: str  # e.g., "Suresh Enterprises Pvt Ltd"
    legal_entity_type: str = "Private Limited Company"
    primary_email: str = ""
    primary_phone: str = ""
    registered_address: str = ""
    pan: str = ""
    gstin: str = ""
    udyam_number: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
