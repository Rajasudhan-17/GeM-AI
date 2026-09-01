import asyncio
from app.dependencies import audit_service
from app.core.enums import AuditAction


def test_audit_hash_chain_integrity():
    async def run_test():
        # Log 5 sample events
        for i in range(5):
            await audit_service.log_event(
                action=AuditAction.DOCUMENT_UPLOADED,
                entity_type="TEST",
                entity_id=f"TEST-{i}",
                correlation_id="CORR-TEST",
                metadata={"step": i},
            )

        # Verify chain integrity
        is_valid = await audit_service.verify_chain_integrity()
        assert is_valid is True

        # Retrieve all events and check chaining
        events = await audit_service.get_all_events()
        assert len(events) >= 5

        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]
            assert curr.previous_hash == prev.event_hash
            assert curr.compute_hash() == curr.event_hash

    asyncio.run(run_test())
