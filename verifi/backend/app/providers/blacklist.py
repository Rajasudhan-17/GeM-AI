from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockBlacklistProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_CENTRAL_DEBARMENT_DATABASE"

    BLACKLIST_REGISTRY = {
        "BDR-90218": {  # NovaTech Systems
            "is_blacklisted": True,
            "debarment_reason": "Default on delivery in tender GEM/2025/B/1109482 and non-response to show-cause notice.",
            "debarred_by": "GeM Incident Management Cell",
            "debarred_from": "2025-11-01",
            "debarred_until": "2027-10-31",
            "status": "ACTIVE_DEBARMENT",
        }
    }

    async def verify(
        self,
        bidder_id: str,
        extracted_facts: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderVerificationResult:
        blacklisted_record = self.BLACKLIST_REGISTRY.get(bidder_id)
        if blacklisted_record:
            return ProviderVerificationResult(
                source_name=self.provider_name,
                status="AVAILABLE",
                is_available=True,
                authoritative_facts=blacklisted_record,
            )

        return ProviderVerificationResult(
            source_name=self.provider_name,
            status="AVAILABLE",
            is_available=True,
            authoritative_facts={
                "is_blacklisted": False,
                "debarment_reason": None,
                "status": "CLEAR",
            },
        )
