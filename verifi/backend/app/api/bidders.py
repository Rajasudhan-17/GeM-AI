from typing import List
from fastapi import APIRouter, Depends
from app.schemas.bidder import BidderResponse
from app.services.bidder_service import BidderService
from app.dependencies import get_bidder_service

router = APIRouter(prefix="/bidders", tags=["Bidders"])


@router.get("", response_model=List[BidderResponse])
async def list_bidders(
    bidder_service: BidderService = Depends(get_bidder_service),
):
    bidders = await bidder_service.get_all_bidders()
    return [
        BidderResponse(
            id=b.id,
            name=b.name,
            legal_entity_type=b.legal_entity_type,
            primary_email=b.primary_email,
            primary_phone=b.primary_phone,
            registered_address=b.registered_address,
            pan=b.pan,
            gstin=b.gstin,
            udyam_number=b.udyam_number,
            created_at=b.created_at,
        )
        for b in bidders
    ]


@router.get("/{bidder_id}", response_model=BidderResponse)
async def get_bidder(
    bidder_id: str,
    bidder_service: BidderService = Depends(get_bidder_service),
):
    b = await bidder_service.get_bidder_by_id(bidder_id)
    return BidderResponse(
        id=b.id,
        name=b.name,
        legal_entity_type=b.legal_entity_type,
        primary_email=b.primary_email,
        primary_phone=b.primary_phone,
        registered_address=b.registered_address,
        pan=b.pan,
        gstin=b.gstin,
        udyam_number=b.udyam_number,
        created_at=b.created_at,
    )
