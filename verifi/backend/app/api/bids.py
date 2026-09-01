from typing import List
from fastapi import APIRouter, Depends
from app.schemas.bid import BidResponse, BidSummaryResponse
from app.schemas.document import DocumentResponse
from app.schemas.verification import (
    VerificationStartResponse,
    VerificationCheckResponse,
    FactComparisonResponse,
)
from app.services.bid_service import BidService
from app.services.bidder_service import BidderService
from app.services.document_service import DocumentService
from app.services.verification_service import VerificationService
from app.dependencies import (
    get_bid_service,
    get_bidder_service,
    get_document_service,
    get_verification_service,
)

router = APIRouter(prefix="/bids", tags=["Bids"])


@router.get("", response_model=List[BidResponse])
async def list_bids(
    bid_service: BidService = Depends(get_bid_service),
    bidder_service: BidderService = Depends(get_bidder_service),
):
    bids = await bid_service.get_all_bids()
    res = []
    for b in bids:
        bidder = await bidder_service.get_bidder_by_id(b.bidder_id)
        res.append(
            BidResponse(
                id=b.id,
                tender_id=b.tender_id,
                bidder_id=b.bidder_id,
                bidder_name=bidder.name if bidder else b.bidder_id,
                bid_number=b.bid_number,
                submitted_at=b.submitted_at,
                status=b.status,
                latest_verification_run_id=b.latest_verification_run_id,
                latest_score=b.latest_score,
                latest_risk_level=b.latest_risk_level,
            )
        )
    return res


@router.get("/{bid_id}", response_model=BidResponse)
async def get_bid(
    bid_id: str,
    bid_service: BidService = Depends(get_bid_service),
    bidder_service: BidderService = Depends(get_bidder_service),
):
    b = await bid_service.get_bid_by_id(bid_id)
    bidder = await bidder_service.get_bidder_by_id(b.bidder_id)
    return BidResponse(
        id=b.id,
        tender_id=b.tender_id,
        bidder_id=b.bidder_id,
        bidder_name=bidder.name if bidder else b.bidder_id,
        bid_number=b.bid_number,
        submitted_at=b.submitted_at,
        status=b.status,
        latest_verification_run_id=b.latest_verification_run_id,
        latest_score=b.latest_score,
        latest_risk_level=b.latest_risk_level,
    )


@router.get("/{bid_id}/summary", response_model=BidSummaryResponse)
async def get_bid_summary(
    bid_id: str,
    bid_service: BidService = Depends(get_bid_service),
):
    return await bid_service.get_bid_summary(bid_id)


@router.get("/{bid_id}/checks", response_model=List[VerificationCheckResponse])
async def get_bid_checks(
    bid_id: str,
    bid_service: BidService = Depends(get_bid_service),
    verification_service: VerificationService = Depends(get_verification_service),
):
    bid = await bid_service.get_bid_by_id(bid_id)
    if not bid.latest_verification_run_id:
        return []
    
    run = await verification_service.get_run_by_id(bid.latest_verification_run_id)
    res = []
    for c in run.checks:
        fc = None
        if c.fact_comparison:
            fc = FactComparisonResponse(
                matched=c.fact_comparison.matched,
                discrepancies=c.fact_comparison.discrepancies,
                field_comparisons=c.fact_comparison.field_comparisons,
            )
        res.append(
            VerificationCheckResponse(
                id=c.id,
                run_id=c.run_id,
                requirement_code=c.requirement_code,
                rule_code=c.rule_code,
                check_name=c.check_name,
                document_type=c.document_type,
                document_id=c.document_id,
                status=c.status,
                extracted_facts=c.extracted_facts,
                source_facts=c.source_facts,
                fact_comparison=fc,
                reason=c.reason,
                evidence=c.evidence,
                evaluated_at=c.evaluated_at,
            )
        )
    return res


@router.get("/{bid_id}/documents", response_model=List[DocumentResponse])
async def get_bid_documents(
    bid_id: str,
    document_service: DocumentService = Depends(get_document_service),
):
    docs = await document_service.get_documents_by_bid_id(bid_id)
    return [
        DocumentResponse(
            id=d.id,
            bid_id=d.bid_id,
            bidder_id=d.bidder_id,
            file_name=d.file_name,
            original_file_name=d.original_file_name,
            file_size_bytes=d.file_size_bytes,
            mime_type=d.mime_type,
            document_type=d.document_type,
            status=d.status,
            ocr_text_preview=d.ocr_text[:300] if d.ocr_text else None,
            extracted_facts=d.extracted_facts,
            created_at=d.created_at,
        )
        for d in docs
    ]


@router.post("/{bid_id}/verify", response_model=VerificationStartResponse)
async def start_bid_verification(
    bid_id: str,
    verification_service: VerificationService = Depends(get_verification_service),
):
    return await verification_service.start_verification(bid_id=bid_id)
