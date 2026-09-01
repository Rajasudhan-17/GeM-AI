from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockESICProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_ESIC_PORTAL"

    AUTHORITATIVE_DB = {
        "BDR-77291": {  # Suresh Enterprises - Full 12 months paid
            "employer_code": "11000123450001001",
            "employer_name": "Suresh Enterprises Pvt Ltd",
            "status": "COMPLIANT",
            "last_paid_month": "2026-04",
            "has_missing_months": False,
            "missing_months": [],
        },
        "BDR-51064": {  # Vikram Traders - REAL GAPS in ESIC
            "employer_code": "11000543210001002",
            "employer_name": "Vikram Traders",
            "status": "NON_COMPLIANT_GAPS",
            "last_paid_month": "2026-01",
            "has_missing_months": True,
            "missing_months": ["2026-02", "2026-03", "2026-04"],
        },
        "BDR-90218": {  # NovaTech Systems
            "employer_code": "11000999990001003",
            "employer_name": "NovaTech Systems",
            "status": "DEFAULT_SUSPENDED",
            "last_paid_month": "2025-06",
            "has_missing_months": True,
            "missing_months": ["2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"],
        },
        "BDR-63357": {  # Green Fields Agro Equipment
            "employer_code": "11000778890001004",
            "employer_name": "Green Fields Agro Equipment",
            "status": "COMPLIANT",
            "last_paid_month": "2026-04",
            "has_missing_months": False,
            "missing_months": [],
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
