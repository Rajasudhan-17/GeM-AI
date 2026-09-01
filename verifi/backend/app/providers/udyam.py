from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockUdyamProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_UDYAM_MSME_PORTAL"

    AUTHORITATIVE_DB = {
        "BDR-77291": {  # Suresh Enterprises
            "udyam_number": "UDYAM-DL-01-0019284",
            "enterprise_name": "Suresh Enterprises Pvt Ltd",
            "enterprise_type": "SMALL",
            "major_activity": "SERVICES",
            "registration_status": "ACTIVE",
            "msme_verified": True,
        },
        "BDR-51064": {  # Vikram Traders
            "udyam_number": "UDYAM-DL-02-0048192",
            "enterprise_name": "Vikram Traders",
            "enterprise_type": "MICRO",
            "major_activity": "TRADING",
            "registration_status": "ACTIVE",
            "msme_verified": True,
        },
        "BDR-90218": {  # NovaTech Systems
            "registration_status": "NOT_REGISTERED",
            "msme_verified": False,
        },
        "BDR-63357": {  # Green Fields Agro Equipment
            "udyam_number": "UDYAM-DL-03-0091823",
            "enterprise_name": "Green Fields Agro Equipment",
            "enterprise_type": "SMALL",
            "major_activity": "MANUFACTURING",
            "registration_status": "ACTIVE",
            "msme_verified": True,
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
