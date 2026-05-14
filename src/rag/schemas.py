from pydantic import BaseModel


class RagQueryRequest(BaseModel):
    question: str
    top_k: int = 5


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[dict]  # [{text, source, score}]


class RagIngestRequest(BaseModel):
    texts: list[str]
    sources: list[str]


class RagIngestResponse(BaseModel):
    inserted: int
