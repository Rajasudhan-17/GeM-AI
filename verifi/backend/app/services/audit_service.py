import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from app.core.enums import AuditAction
from app.models.audit import AuditEvent
from app.repositories.base import AuditRepository


class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.repo = audit_repo

    async def log_event(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        correlation_id: str,
        actor: str = "SYSTEM",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=f"AUD-{uuid.uuid4().hex[:10]}",
            timestamp=datetime.now(timezone.utc),
            action=action,
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )
        return await self.repo.append(event)

    async def get_all_events(self) -> List[AuditEvent]:
        return await self.repo.get_all()

    async def get_events_for_entity(self, entity_type: str, entity_id: str) -> List[AuditEvent]:
        return await self.repo.get_by_entity(entity_type, entity_id)

    async def get_events_by_correlation_id(self, correlation_id: str) -> List[AuditEvent]:
        return await self.repo.get_by_correlation_id(correlation_id)

    async def verify_chain_integrity(self) -> bool:
        events = await self.repo.get_all()
        if not events:
            return True

        for i, event in enumerate(events):
            expected_prev_hash = "0" * 64 if i == 0 else events[i - 1].event_hash
            if event.previous_hash != expected_prev_hash:
                return False
            if event.compute_hash() != event.event_hash:
                return False

        return True
