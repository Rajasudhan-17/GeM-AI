from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockEPFOProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_EPFO_PORTAL"

    AUTHORITATIVE_DB = {
        "BDR-77291": {  # Suresh Enterprises
            "establishment_code": "DL/12345/67890",
            "establishment_name": "SURESH ENTERPRISES PVT LTD",
            "status": "ACTIVE",
            "recent_filing_status": "PAID",
            "active_members_count": 48,
        },
        "BDR-51064": {  # Vikram Traders
            "establishment_code": "DL/54321/09876",
            "establishment_name": "VIKRAM TRADERS",
            "status": "ACTIVE",
            "recent_filing_status": "PAID",
            "active_members_count": 12,
        },
        "BDR-90218": {  # NovaTech Systems - Establishment code missing/inactive
            "establishment_code": "DL/99999/00000",
            "establishment_name": "NOVATECH SYSTEMS",
            "status": "DEFAULTER_INACTIVE",
            "recent_filing_status": "UNPAID",
            "active_members_count": 0,
        },
        "BDR-63357": {  # Green Fields Agro Equipment
            "establishment_code": "DL/77889/11223",
            "establishment_name": "GREEN FIELDS AGRO EQUIPMENT",
            "status": "ACTIVE",
            "recent_filing_status": "PAID",
            "active_members_count": 25,
        },
    }

    async def verify(
        self,
        bidder_id: str,
        extracted_facts: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderVerificationResult:
        auth_record = self.AUTHORITATIVE_DB.get(bidder_id)
        if not auth_record:
            return ProviderVerificationResult(
                source_name=self.provider_name,
                status="NOT_FOUND",
                is_available=True,
                authoritative_facts={},
            )

        return ProviderVerificationResult(
            source_name=self.provider_name,
            status="AVAILABLE",
            is_available=True,
            authoritative_facts=auth_record,
        )
