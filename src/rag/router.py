from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.rag.schemas import (
    RagQueryRequest,
    RagQueryResponse,
    RagIngestRequest,
    RagIngestResponse,
)
from src.rag import service

router = APIRouter(prefix="/api/v1/rag", tags=["RAG 文档问答"])


@router.post("/query", response_model=RagQueryResponse)
async def query_docs(req: RagQueryRequest):
    """基于知识库的文档问答"""
    result = await service.query(req.question, req.top_k)
    return RagQueryResponse(answer=result["answer"], sources=result["sources"])


@router.post("/query/stream")
async def query_docs_stream(req: RagQueryRequest):
    """基于知识库的文档问答（SSE 流式输出）"""

    async def event_generator():
        async for chunk in service.query_stream(req.question, req.top_k):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/ingest", response_model=RagIngestResponse)
async def ingest_docs(req: RagIngestRequest):
    """批量导入文档到知识库"""
    count = await service.ingest(req.texts, req.sources)
    return RagIngestResponse(inserted=count)
