from typing import List
from fastapi import APIRouter, Depends
from app.schemas.tender import TenderResponse, TenderRequirementResponse
from app.services.tender_service import TenderService
from app.dependencies import get_tender_service

router = APIRouter(prefix="/tenders", tags=["Tenders"])


@router.get("", response_model=List[TenderResponse])
async def list_tenders(
    tender_service: TenderService = Depends(get_tender_service),
):
    tenders = await tender_service.get_all_tenders()
    res = []
    for t in tenders:
        reqs = await tender_service.get_tender_requirements(t.id)
        req_res = [
            TenderRequirementResponse(
                id=r.id,
                tender_id=r.tender_id,
                code=r.code,
                name=r.name,
                document_type=r.document_type,
                rule_code=r.rule_code,
                is_mandatory=r.is_mandatory,
                weight=r.weight,
                description=r.description,
            )
            for r in reqs
        ]
        res.append(
            TenderResponse(
                id=t.id,
                tender_number=t.tender_number,
                title=t.title,
                category=t.category,
                description=t.description,
                organization=t.organization,
                estimated_value_inr=t.estimated_value_inr,
                closing_date=t.closing_date,
                requirements=req_res,
                created_at=t.created_at,
            )
        )
    return res


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(
    tender_id: str,
    tender_service: TenderService = Depends(get_tender_service),
):
    t = await tender_service.get_tender_by_id(tender_id)
    reqs = await tender_service.get_tender_requirements(t.id)
    req_res = [
        TenderRequirementResponse(
            id=r.id,
            tender_id=r.tender_id,
            code=r.code,
            name=r.name,
            document_type=r.document_type,
            rule_code=r.rule_code,
            is_mandatory=r.is_mandatory,
            weight=r.weight,
            description=r.description,
        )
        for r in reqs
    ]
    return TenderResponse(
        id=t.id,
        tender_number=t.tender_number,
        title=t.title,
        category=t.category,
        description=t.description,
        organization=t.organization,
        estimated_value_inr=t.estimated_value_inr,
        closing_date=t.closing_date,
        requirements=req_res,
        created_at=t.created_at,
    )
