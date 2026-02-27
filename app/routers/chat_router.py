"""Chat router."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.models.schemas import ChatRequest, ChatResponse
from app.services import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        answer, sources = chat_service.chat(payload.message, payload.history or [])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return ChatResponse(answer=answer, sources=sources)
