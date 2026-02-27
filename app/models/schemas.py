from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Users ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"   # "admin" or "user"


class UserOut(BaseModel):
    username: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ── Manuals ───────────────────────────────────────────────────────────────────

class ManualMeta(BaseModel):
    unit_number: str
    filename: str
    description: Optional[str] = None
    uploaded_at: str
    uploaded_by: str
    page_count: int


class ManualList(BaseModel):
    manuals: List[ManualMeta]


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str        # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class SourceChunk(BaseModel):
    unit_number: str
    filename: str
    page: int
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
