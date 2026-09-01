from datetime import datetime, timezone
import hashlib
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.core.enums import AuditAction


class AuditEvent(BaseModel):
    id: str  # e.g., "AUD-0001"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: AuditAction
    actor: str = "SYSTEM"
    entity_type: str  # e.g., "BID", "DOCUMENT", "VERIFICATION_RUN", "DECISION"
    entity_id: str
    correlation_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    previous_hash: str = "0" * 64  # Genesis block hash default
    event_hash: str = ""

    def compute_hash(self) -> str:
        data = {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "actor": self.actor,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
