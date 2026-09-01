import asyncio
import copy
from typing import List, Optional, Dict
from app.models.tender import Tender
from app.models.requirement import TenderRequirement
from app.models.bidder import Bidder
from app.models.bid import Bid
from app.models.document import Document
from app.models.verification import VerificationRun, VerificationCheck
from app.models.decision import ProcurementDecision
from app.models.audit import AuditEvent
from app.repositories.base import (
    TenderRepository,
    BidderRepository,
    BidRepository,
    DocumentRepository,
    VerificationRepository,
    DecisionRepository,
    AuditRepository,
)


class InMemoryTenderRepository(TenderRepository):
    def __init__(self):
        self._tenders: Dict[str, Tender] = {}
        self._requirements: Dict[str, List[TenderRequirement]] = {}
        self._lock = asyncio.Lock()

    async def get_all(self) -> List[Tender]:
        async with self._lock:
            return [copy.deepcopy(t) for t in self._tenders.values()]

    async def get_by_id(self, tender_id: str) -> Optional[Tender]:
        async with self._lock:
            tender = self._tenders.get(tender_id)
            return copy.deepcopy(tender) if tender else None

    async def save(self, tender: Tender) -> Tender:
        async with self._lock:
            self._tenders[tender.id] = copy.deepcopy(tender)
            return copy.deepcopy(tender)

    async def get_requirements(self, tender_id: str) -> List[TenderRequirement]:
        async with self._lock:
            reqs = self._requirements.get(tender_id, [])
            return [copy.deepcopy(r) for r in reqs]

    async def save_requirement(self, requirement: TenderRequirement) -> TenderRequirement:
        async with self._lock:
            tender_id = requirement.tender_id
            if tender_id not in self._requirements:
                self._requirements[tender_id] = []
            
            # Update existing or append
            for idx, existing in enumerate(self._requirements[tender_id]):
                if existing.id == requirement.id:
                    self._requirements[tender_id][idx] = copy.deepcopy(requirement)
                    return copy.deepcopy(requirement)
            
            self._requirements[tender_id].append(copy.deepcopy(requirement))
            return copy.deepcopy(requirement)


class InMemoryBidderRepository(BidderRepository):
    def __init__(self):
        self._bidders: Dict[str, Bidder] = {}
        self._lock = asyncio.Lock()

    async def get_all(self) -> List[Bidder]:
        async with self._lock:
            return [copy.deepcopy(b) for b in self._bidders.values()]

    async def get_by_id(self, bidder_id: str) -> Optional[Bidder]:
        async with self._lock:
            bidder = self._bidders.get(bidder_id)
            return copy.deepcopy(bidder) if bidder else None

    async def save(self, bidder: Bidder) -> Bidder:
        async with self._lock:
            self._bidders[bidder.id] = copy.deepcopy(bidder)
            return copy.deepcopy(bidder)


class InMemoryBidRepository(BidRepository):
    def __init__(self):
        self._bids: Dict[str, Bid] = {}
        self._lock = asyncio.Lock()

    async def get_all(self) -> List[Bid]:
        async with self._lock:
            return [copy.deepcopy(b) for b in self._bids.values()]

    async def get_by_id(self, bid_id: str) -> Optional[Bid]:
        async with self._lock:
            bid = self._bids.get(bid_id)
            return copy.deepcopy(bid) if bid else None

    async def get_by_tender_id(self, tender_id: str) -> List[Bid]:
        async with self._lock:
            return [copy.deepcopy(b) for b in self._bids.values() if b.tender_id == tender_id]

    async def get_by_bidder_id(self, bidder_id: str) -> Optional[Bid]:
        async with self._lock:
            for b in self._bids.values():
                if b.bidder_id == bidder_id:
                    return copy.deepcopy(b)
            return None

    async def save(self, bid: Bid) -> Bid:
        async with self._lock:
            self._bids[bid.id] = copy.deepcopy(bid)
            return copy.deepcopy(bid)


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self):
        self._documents: Dict[str, Document] = {}
        self._lock = asyncio.Lock()

    async def get_all(self) -> List[Document]:
        async with self._lock:
            return [copy.deepcopy(d) for d in self._documents.values()]

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        async with self._lock:
            doc = self._documents.get(document_id)
            return copy.deepcopy(doc) if doc else None

    async def get_by_bid_id(self, bid_id: str) -> List[Document]:
        async with self._lock:
            return [copy.deepcopy(d) for d in self._documents.values() if d.bid_id == bid_id]

    async def save(self, document: Document) -> Document:
        async with self._lock:
            self._documents[document.id] = copy.deepcopy(document)
            return copy.deepcopy(document)

    async def delete(self, document_id: str) -> bool:
        async with self._lock:
            if document_id in self._documents:
                del self._documents[document_id]
                return True
            return False


class InMemoryVerificationRepository(VerificationRepository):
    def __init__(self):
        self._runs: Dict[str, VerificationRun] = {}
        self._checks: Dict[str, VerificationCheck] = {}
        self._lock = asyncio.Lock()

    async def get_run_by_id(self, run_id: str) -> Optional[VerificationRun]:
        async with self._lock:
            run = self._runs.get(run_id)
            return copy.deepcopy(run) if run else None

    async def get_latest_run_by_bid_id(self, bid_id: str) -> Optional[VerificationRun]:
        async with self._lock:
            matching = [r for r in self._runs.values() if r.bid_id == bid_id]
            if not matching:
                return None
            matching.sort(key=lambda x: x.started_at, reverse=True)
            return copy.deepcopy(matching[0])

    async def get_all_runs_by_bid_id(self, bid_id: str) -> List[VerificationRun]:
        async with self._lock:
            matching = [r for r in self._runs.values() if r.bid_id == bid_id]
            matching.sort(key=lambda x: x.started_at, reverse=True)
            return [copy.deepcopy(r) for r in matching]

    async def save_run(self, run: VerificationRun) -> VerificationRun:
        async with self._lock:
            self._runs[run.id] = copy.deepcopy(run)
            for check in run.checks:
                self._checks[check.id] = copy.deepcopy(check)
            return copy.deepcopy(run)

    async def get_check_by_id(self, check_id: str) -> Optional[VerificationCheck]:
        async with self._lock:
            check = self._checks.get(check_id)
            return copy.deepcopy(check) if check else None

    async def save_check(self, check: VerificationCheck) -> VerificationCheck:
        async with self._lock:
            self._checks[check.id] = copy.deepcopy(check)
            # Also update in run if present
            if check.run_id in self._runs:
                run = self._runs[check.run_id]
                for idx, c in enumerate(run.checks):
                    if c.id == check.id:
                        run.checks[idx] = copy.deepcopy(check)
                        break
                else:
                    run.checks.append(copy.deepcopy(check))
            return copy.deepcopy(check)


class InMemoryDecisionRepository(DecisionRepository):
    def __init__(self):
        self._decisions: Dict[str, List[ProcurementDecision]] = {}
        self._lock = asyncio.Lock()

    async def get_by_bid_id(self, bid_id: str) -> Optional[ProcurementDecision]:
        async with self._lock:
            history = self._decisions.get(bid_id, [])
            if not history:
                return None
            return copy.deepcopy(history[-1])  # Latest decision

    async def get_history_by_bid_id(self, bid_id: str) -> List[ProcurementDecision]:
        async with self._lock:
            history = self._decisions.get(bid_id, [])
            return [copy.deepcopy(d) for d in history]

    async def save(self, decision: ProcurementDecision) -> ProcurementDecision:
        async with self._lock:
            bid_id = decision.bid_id
            if bid_id not in self._decisions:
                self._decisions[bid_id] = []
            self._decisions[bid_id].append(copy.deepcopy(decision))
            return copy.deepcopy(decision)


class InMemoryAuditRepository(AuditRepository):
    def __init__(self):
        self._events: List[AuditEvent] = []
        self._lock = asyncio.Lock()

    async def get_all(self) -> List[AuditEvent]:
        async with self._lock:
            return [copy.deepcopy(e) for e in self._events]

    async def get_by_entity(self, entity_type: str, entity_id: str) -> List[AuditEvent]:
        async with self._lock:
            return [
                copy.deepcopy(e)
                for e in self._events
                if e.entity_type == entity_type and e.entity_id == entity_id
            ]

    async def get_by_correlation_id(self, correlation_id: str) -> List[AuditEvent]:
        async with self._lock:
            return [
                copy.deepcopy(e)
                for e in self._events
                if e.correlation_id == correlation_id
            ]

    async def get_latest_event(self) -> Optional[AuditEvent]:
        async with self._lock:
            if not self._events:
                return None
            return copy.deepcopy(self._events[-1])

    async def append(self, event: AuditEvent) -> AuditEvent:
        async with self._lock:
            # Hash chaining: set previous_hash
            if self._events:
                event.previous_hash = self._events[-1].event_hash
            else:
                event.previous_hash = "0" * 64  # Genesis
            
            event.event_hash = event.compute_hash()
            self._events.append(copy.deepcopy(event))
            return copy.deepcopy(event)
