from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def get_health():
    return {
        "status": "healthy",
        "service": "verifi-backend",
        "database": "not_used",
        "repository": "in_memory",
        "version": settings.VERSION,
    }
