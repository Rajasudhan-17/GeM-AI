from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ProviderVerificationResult(BaseModel):
    source_name: str
    status: str  # AVAILABLE, UNAVAILABLE, ERROR
    is_available: bool = True
    authoritative_facts: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerificationProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def verify(
        self,
        bidder_id: str,
        extracted_facts: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProviderVerificationResult:
        """Queries authoritative government or third-party mock source."""
        pass
