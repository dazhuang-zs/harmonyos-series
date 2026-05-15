from typing import Optional
from pydantic import BaseModel


class RagQueryRequest(BaseModel):
    question: str
    top_k: int = 5
    session_id: Optional[str] = None  # 多轮对话会话 ID
    stream: bool = False  # 是否流式返回


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[dict]  # [{text, source, score}]
    session_id: Optional[str] = None


class RagIngestRequest(BaseModel):
    texts: list[str]
    sources: list[str]


class RagIngestResponse(BaseModel):
    inserted: int
