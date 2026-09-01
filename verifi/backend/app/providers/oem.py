from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.providers.base import VerificationProvider, ProviderVerificationResult


class MockOEMProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK_OEM_VERIFICATION_NETWORK"

    AUTHORITATIVE_DB = {
        "BDR-77291": {  # Suresh Enterprises
            "oem_name": "Cisco Systems India Pvt Ltd",
            "partner_name": "Suresh Enterprises Pvt Ltd",
            "partner_tier": "GOLD_PARTNER",
            "authorized_for_tender": True,
            "valid_from": "2026-01-15",
            "valid_until": "2027-01-14",
            "tender_number": "GEM/2026/B/2317045",
            "product_scope": "Networking Switches, Routers & Firewalls",
            "status": "ACTIVE_VALID",
        },
        "BDR-51064": {  # Vikram Traders
            "oem_name": "D-Link India Ltd",
            "partner_name": "Vikram Traders",
            "partner_tier": "AUTHORIZED_DEALER",
            "authorized_for_tender": True,
            "valid_from": "2026-01-01",
            "valid_until": "2026-12-31",
            "tender_number": "GEM/2026/B/2317045",
            "product_scope": "Enterprise Network Switches & Access Points",
            "status": "ACTIVE_VALID",
        },
        "BDR-90218": {  # NovaTech Systems - Scope mismatch
            "oem_name": "HP Enterprise India",
            "partner_name": "NovaTech Systems",
            "partner_tier": "REGISTERED_RESELLER",
            "authorized_for_tender": False,
            "valid_from": "2025-01-01",
            "valid_until": "2025-12-31",  # Expired
            "tender_number": "GEM/2025/B/9999999",  # Wrong tender
            "product_scope": "Consumer Laptops & Printers Only",
            "status": "EXPIRED_AND_MISMATCH",
        },
        "BDR-63357": {  # Green Fields Agro Equipment - NEAR EXPIRY (valid_until: 2026-09-15)
            "oem_name": "Ubiquiti Networks India",
            "partner_name": "Green Fields Agro Equipment",
            "partner_tier": "SILVER_PARTNER",
            "authorized_for_tender": True,
            "valid_from": "2025-09-16",
            "valid_until": "2026-09-15",  # Approaching expiry within 30 days
            "tender_number": "GEM/2026/B/2317045",
            "product_scope": "Enterprise WiFi & Network Equipment",
            "status": "EXPIRING_SOON",
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
