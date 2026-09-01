from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.services.audit_service import AuditService
from app.services.bid_service import BidService
from app.dependencies import get_audit_service, get_bid_service

router = APIRouter(tags=["Audit"])


@router.get("/bids/{bid_id}/audit", response_model=List[Dict[str, Any]])
async def get_bid_audit_trail(
    bid_id: str,
    bid_service: BidService = Depends(get_bid_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    bid = await bid_service.get_bid_by_id(bid_id)
    all_events = await audit_service.get_all_events()

    # Filter events related to this bid (by entity_id, correlation_id, or metadata)
    bid_events = []
    run_id = bid.latest_verification_run_id

    for e in all_events:
        is_match = False
        if e.entity_id == bid_id or e.entity_id == bid.bidder_id:
            is_match = True
        elif run_id and (e.entity_id == run_id or e.correlation_id == run_id):
            is_match = True
        elif e.metadata and (e.metadata.get("bid_id") == bid_id or e.metadata.get("bidder_id") == bid.bidder_id):
            is_match = True
        
        if is_match:
            bid_events.append({
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "action": e.action.value,
                "actor": e.actor,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "correlation_id": e.correlation_id,
                "metadata": e.metadata,
                "previous_hash": e.previous_hash,
                "event_hash": e.event_hash,
            })

    return bid_events
