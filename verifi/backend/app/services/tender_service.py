from typing import List, Optional
from app.models.tender import Tender
from app.models.requirement import TenderRequirement
from app.repositories.base import TenderRepository
from app.core.exceptions import EntityNotFoundException


class TenderService:
    def __init__(self, tender_repo: TenderRepository):
        self.tender_repo = tender_repo

    async def get_all_tenders(self) -> List[Tender]:
        return await self.tender_repo.get_all()

    async def get_tender_by_id(self, tender_id: str) -> Tender:
        tender = await self.tender_repo.get_by_id(tender_id)
        if not tender:
            raise EntityNotFoundException("Tender", tender_id)
        return tender

    async def get_tender_requirements(self, tender_id: str) -> List[TenderRequirement]:
        await self.get_tender_by_id(tender_id)  # Ensure tender exists
        return await self.tender_repo.get_requirements(tender_id)
