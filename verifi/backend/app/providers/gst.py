from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockGSTProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_GST_PORTAL"

    # Authoritative records in GST database
    AUTHORITATIVE_DB = {
        "BDR-77291": {  # Suresh Enterprises
            "gstin": "07AABCS1429B1Z1",
            "legal_name": "Suresh Enterprises Pvt Ltd",
            "trade_name": "Suresh Enterprises",
            "registration_status": "ACTIVE",
            "constitution": "Private Limited Company",
            "filing_frequency": "MONTHLY",
            "compliance_rating": "HIGH",
        },
        "BDR-51064": {  # Vikram Traders - CRITICAL MISMATCH POINT
            # Authoritative GSTIN is 07AACPV9821K1ZP
            "gstin": "07AACPV9821K1ZP",
            "legal_name": "Vikram Traders",
            "trade_name": "Vikram Traders",
            "registration_status": "ACTIVE",
            "constitution": "Proprietorship",
            "filing_frequency": "MONTHLY",
            "compliance_rating": "GOOD",
        },
        "BDR-90218": {  # NovaTech Systems
            "gstin": "07AABCN8822M1ZQ",
            "legal_name": "NovaTech Systems",
            "trade_name": "NovaTech",
            "registration_status": "CANCELLED",
            "constitution": "Private Limited Company",
            "filing_frequency": "IRREGULAR",
            "compliance_rating": "LOW",
        },
        "BDR-63357": {  # Green Fields Agro Equipment
            "gstin": "07AAACG5541L1Z9",
            "legal_name": "Green Fields Agro Equipment",
            "trade_name": "Green Fields",
            "registration_status": "ACTIVE",
            "constitution": "Partnership Firm",
            "filing_frequency": "MONTHLY",
            "compliance_rating": "HIGH",
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
