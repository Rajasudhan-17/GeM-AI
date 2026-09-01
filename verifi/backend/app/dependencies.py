from functools import lru_cache
from app.repositories.memory import (
    InMemoryTenderRepository,
    InMemoryBidderRepository,
    InMemoryBidRepository,
    InMemoryDocumentRepository,
    InMemoryVerificationRepository,
    InMemoryDecisionRepository,
    InMemoryAuditRepository,
)
from app.storage.local import LocalDocumentStorage
from app.services.audit_service import AuditService
from app.services.tender_service import TenderService
from app.services.bidder_service import BidderService
from app.services.bid_service import BidService
from app.services.document_service import DocumentService
from app.services.verification_service import VerificationService
from app.services.decision_service import DecisionService
from app.ai.chat import AIChatService
from app.ai.reason import AIReasonGenerator

# Singletons for In-Memory Repositories
tender_repo = InMemoryTenderRepository()
bidder_repo = InMemoryBidderRepository()
bid_repo = InMemoryBidRepository()
document_repo = InMemoryDocumentRepository()
verification_repo = InMemoryVerificationRepository()
decision_repo = InMemoryDecisionRepository()
audit_repo = InMemoryAuditRepository()

storage = LocalDocumentStorage()
audit_service = AuditService(audit_repo)

tender_service = TenderService(tender_repo)
bidder_service = BidderService(bidder_repo)
bid_service = BidService(
    bid_repo=bid_repo,
    bidder_repo=bidder_repo,
    tender_repo=tender_repo,
    verification_repo=verification_repo,
    document_repo=document_repo,
    decision_repo=decision_repo,
)
document_service = DocumentService(
    document_repo=document_repo,
    bid_repo=bid_repo,
    storage=storage,
    audit_service=audit_service,
)
verification_service = VerificationService(
    verification_repo=verification_repo,
    bid_repo=bid_repo,
    bidder_repo=bidder_repo,
    tender_repo=tender_repo,
    document_repo=document_repo,
    storage=storage,
    audit_service=audit_service,
)
decision_service = DecisionService(
    decision_repo=decision_repo,
    bid_repo=bid_repo,
    verification_repo=verification_repo,
    audit_service=audit_service,
)
ai_chat_service = AIChatService(
    bid_repo=bid_repo,
    bidder_repo=bidder_repo,
    verification_repo=verification_repo,
    audit_service=audit_service,
)
ai_reason_generator = AIReasonGenerator(
    bid_repo=bid_repo,
    bidder_repo=bidder_repo,
    verification_repo=verification_repo,
)


def get_tender_service() -> TenderService:
    return tender_service


def get_bidder_service() -> BidderService:
    return bidder_service


def get_bid_service() -> BidService:
    return bid_service


def get_document_service() -> DocumentService:
    return document_service


def get_verification_service() -> VerificationService:
    return verification_service


def get_decision_service() -> DecisionService:
    return decision_service


def get_audit_service() -> AuditService:
    return audit_service


def get_ai_chat_service() -> AIChatService:
    return ai_chat_service


def get_ai_reason_generator() -> AIReasonGenerator:
    return ai_reason_generator
