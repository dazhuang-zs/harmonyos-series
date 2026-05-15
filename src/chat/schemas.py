from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = ""
    mode: str = "rag"  # rag / agent / codegen / diagnose
    stream: bool = False


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    mode: str
    sources: list[dict] = []
    steps: list[dict] = []
