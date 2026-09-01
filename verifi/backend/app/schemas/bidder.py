from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class BidderResponse(BaseModel):
    id: str
    name: str
    legal_entity_type: str
    primary_email: str
    primary_phone: str
    registered_address: str
    pan: str
    gstin: str
    udyam_number: str
    created_at: datetime
