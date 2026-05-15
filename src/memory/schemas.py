from pydantic import BaseModel


class ConversationCreateRequest(BaseModel):
    title: str = "新对话"


class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    message_count: int
    created_at: float
    updated_at: float


class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: float


class ConversationDetailResponse(BaseModel):
    conversation_id: str
    title: str
    messages: list[MessageResponse]
    user_preferences: dict
    created_at: float
    updated_at: float
