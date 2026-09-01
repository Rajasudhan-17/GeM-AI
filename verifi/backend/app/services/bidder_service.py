from typing import List, Optional
from app.models.bidder import Bidder
from app.repositories.base import BidderRepository
from app.core.exceptions import EntityNotFoundException


class BidderService:
    def __init__(self, bidder_repo: BidderRepository):
        self.bidder_repo = bidder_repo

    async def get_all_bidders(self) -> List[Bidder]:
        return await self.bidder_repo.get_all()

    async def get_bidder_by_id(self, bidder_id: str) -> Bidder:
        bidder = await self.bidder_repo.get_by_id(bidder_id)
        if not bidder:
            raise EntityNotFoundException("Bidder", bidder_id)
        return bidder
