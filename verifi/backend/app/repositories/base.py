from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.tender import Tender
from app.models.requirement import TenderRequirement
from app.models.bidder import Bidder
from app.models.bid import Bid
from app.models.document import Document
from app.models.verification import VerificationRun, VerificationCheck
from app.models.decision import ProcurementDecision
from app.models.audit import AuditEvent


class TenderRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Tender]:
        pass

    @abstractmethod
    async def get_by_id(self, tender_id: str) -> Optional[Tender]:
        pass

    @abstractmethod
    async def save(self, tender: Tender) -> Tender:
        pass

    @abstractmethod
    async def get_requirements(self, tender_id: str) -> List[TenderRequirement]:
        pass

    @abstractmethod
    async def save_requirement(self, requirement: TenderRequirement) -> TenderRequirement:
        pass


class BidderRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Bidder]:
        pass

    @abstractmethod
    async def get_by_id(self, bidder_id: str) -> Optional[Bidder]:
        pass

    @abstractmethod
    async def save(self, bidder: Bidder) -> Bidder:
        pass


class BidRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Bid]:
        pass

    @abstractmethod
    async def get_by_id(self, bid_id: str) -> Optional[Bid]:
        pass

    @abstractmethod
    async def get_by_tender_id(self, tender_id: str) -> List[Bid]:
        pass

    @abstractmethod
    async def get_by_bidder_id(self, bidder_id: str) -> Optional[Bid]:
        pass

    @abstractmethod
    async def save(self, bid: Bid) -> Bid:
        pass


class DocumentRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Document]:
        pass

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        pass

    @abstractmethod
    async def get_by_bid_id(self, bid_id: str) -> List[Document]:
        pass

    @abstractmethod
    async def save(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        pass


class VerificationRepository(ABC):
    @abstractmethod
    async def get_run_by_id(self, run_id: str) -> Optional[VerificationRun]:
        pass

    @abstractmethod
    async def get_latest_run_by_bid_id(self, bid_id: str) -> Optional[VerificationRun]:
        pass

    @abstractmethod
    async def get_all_runs_by_bid_id(self, bid_id: str) -> List[VerificationRun]:
        pass

    @abstractmethod
    async def save_run(self, run: VerificationRun) -> VerificationRun:
        pass

    @abstractmethod
    async def get_check_by_id(self, check_id: str) -> Optional[VerificationCheck]:
        pass

    @abstractmethod
    async def save_check(self, check: VerificationCheck) -> VerificationCheck:
        pass


class DecisionRepository(ABC):
    @abstractmethod
    async def get_by_bid_id(self, bid_id: str) -> Optional[ProcurementDecision]:
        pass

    @abstractmethod
    async def get_history_by_bid_id(self, bid_id: str) -> List[ProcurementDecision]:
        pass

    @abstractmethod
    async def save(self, decision: ProcurementDecision) -> ProcurementDecision:
        pass


class AuditRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[AuditEvent]:
        pass

    @abstractmethod
    async def get_by_entity(self, entity_type: str, entity_id: str) -> List[AuditEvent]:
        pass

    @abstractmethod
    async def get_by_correlation_id(self, correlation_id: str) -> List[AuditEvent]:
        pass

    @abstractmethod
    async def get_latest_event(self) -> Optional[AuditEvent]:
        pass

    @abstractmethod
    async def append(self, event: AuditEvent) -> AuditEvent:
        pass
