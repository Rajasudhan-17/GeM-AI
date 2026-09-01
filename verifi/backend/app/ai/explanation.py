from typing import Dict, Any, List, Optional
from app.ai.provider import mock_ai_provider, AIProvider
from app.models.verification import AIRecommendation


class ExplanationService:
    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or mock_ai_provider

    async def generate_run_explanation(
        self,
        bidder_name: str,
        score: float,
        risk_level: str,
        checks: List[Dict[str, Any]],
    ) -> AIRecommendation:
        result = await self.provider.generate_explanation(
            bidder_name=bidder_name,
            score=score,
            risk_level=risk_level,
            checks=checks,
        )
        return AIRecommendation(
            summary=result["summary"],
            risk_explanation=result["risk_explanation"],
            key_findings=result["key_findings"],
            suggested_action=result["suggested_action"],
            drafted_reason=result["drafted_reason"],
        )


explanation_service = ExplanationService()
