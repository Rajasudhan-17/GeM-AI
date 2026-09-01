from fastapi import APIRouter, Depends
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIDecisionReasonResponse,
)
from app.ai.chat import AIChatService
from app.ai.reason import AIReasonGenerator
from app.dependencies import get_ai_chat_service, get_ai_reason_generator

router = APIRouter(tags=["AI"])


@router.post("/bids/{bid_id}/ai/chat", response_model=AIChatResponse)
async def ai_chat_endpoint(
    bid_id: str,
    request: AIChatRequest,
    chat_service: AIChatService = Depends(get_ai_chat_service),
):
    return await chat_service.chat(
        bid_id=bid_id,
        message=request.message,
        focus_check_id=request.focus_check_id,
    )


@router.post("/bids/{bid_id}/ai/generate-reason", response_model=AIDecisionReasonResponse)
async def ai_generate_reason_endpoint(
    bid_id: str,
    reason_generator: AIReasonGenerator = Depends(get_ai_reason_generator),
):
    return await reason_generator.generate_reason(bid_id=bid_id)
