from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockDigiLockerProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_DIGILOCKER_GATEWAY"

    async def verify(
        self,
        bidder_id: str,
        extracted_facts: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderVerificationResult:
        # Simulate Provider Outage / Unavailability specifically for NovaTech (BDR-90218)
        if bidder_id == "BDR-90218":
            return ProviderVerificationResult(
                source_name=self.provider_name,
                status="UNAVAILABLE",
                is_available=False,
                authoritative_facts={},
                metadata={"error_detail": "DigiLocker API gateway timed out (HTTP 503 Service Unavailable)."},
            )

        # Other bidders are available and verified
        return ProviderVerificationResult(
            source_name=self.provider_name,
            status="AVAILABLE",
            is_available=True,
            authoritative_facts={
                "issuer_verified": True,
                "digital_signature_valid": True,
                "timestamp_verified": True,
                "tamper_proof": True,
            },
        )
