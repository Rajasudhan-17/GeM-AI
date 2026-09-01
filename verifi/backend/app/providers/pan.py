from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockPANProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_INCOME_TAX_PAN_SERVICE"

    AUTHORITATIVE_DB = {
        "BDR-77291": {  # Suresh Enterprises
            "pan": "AABCS1429B",
            "name": "SURESH ENTERPRISES PVT LTD",
            "status": "VALID",
            "aadhaar_seeding_status": "LINKED",
        },
        "BDR-51064": {  # Vikram Traders
            "pan": "AACPV9821K",
            "name": "VIKRAM TRADERS",
            "status": "VALID",
            "aadhaar_seeding_status": "LINKED",
        },
        "BDR-90218": {  # NovaTech Systems - Authoritative PAN is AABCN8822M
            "pan": "AABCN8822M",
            "name": "NOVATECH SYSTEMS",
            "status": "VALID",
            "aadhaar_seeding_status": "NOT_LINKED",
        },
        "BDR-63357": {  # Green Fields Agro Equipment
            "pan": "AAACG5541L",
            "name": "GREEN FIELDS AGRO EQUIPMENT",
            "status": "VALID",
            "aadhaar_seeding_status": "LINKED",
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
