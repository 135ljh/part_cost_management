from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assistant import (
    AssistantCapabilityResponse,
    AssistantChatRequest,
    AssistantChatResponse,
)
from app.services.assistant_service import AssistantService


router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.get("/capabilities", response_model=AssistantCapabilityResponse, summary="AI 助手能力信息")
def capabilities(db: Session = Depends(get_db)) -> AssistantCapabilityResponse:
    return AssistantService(db).capabilities()


@router.post("/chat", response_model=AssistantChatResponse, summary="AI 助手对话")
def chat(payload: AssistantChatRequest, db: Session = Depends(get_db)) -> AssistantChatResponse:
    return AssistantService(db).chat(
        message=payload.message,
        history=[m.model_dump() for m in payload.history],
        context=payload.context,
        use_runtime_snapshot=payload.use_runtime_snapshot,
    )
