import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json

from src.core.llm_provider import get_llm_provider
from src.core.embedding_provider import get_embedding_provider
from src.core.vector_store import search_similar
from src.rag.schemas import (
    RagQueryRequest,
    RagQueryResponse,
    RagIngestRequest,
    RagIngestResponse,
)
from src.rag import service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/rag", tags=["RAG 文档问答"])


@router.post("/query", response_model=RagQueryResponse)
async def query_docs(req: RagQueryRequest):
    """基于知识库的文档问答（支持多轮对话和流式输出）"""
    try:
        if req.stream:
            # 流式输出
            async def event_stream():
                embedding_provider = get_embedding_provider()
                llm_provider = get_llm_provider()

                query_embedding = await embedding_provider.embed_query(req.question)
                docs = await search_similar(query_embedding, top_k=req.top_k)

                context = "\n\n---\n\n".join(
                    [f"【来源：{doc['source']}】\n{doc['text']}" for doc in docs]
                )

                messages = [{"role": "system", "content": service.RAG_SYSTEM_PROMPT}]
                history = service._get_history(req.session_id)
                if history:
                    messages.extend(history)

                messages.append({
                    "role": "user",
                    "content": f"参考文档：\n{context}\n\n用户问题：{req.question}",
                })

                full_answer = ""
                async for chunk in llm_provider.chat_stream(messages):
                    full_answer += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

                yield f"data: {json.dumps({'done': True})}\n\n"
                service._save_history(req.session_id, req.question, full_answer)

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        # 非流式
        result = await service.query(req.question, req.top_k, req.session_id)
        return RagQueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=req.session_id,
        )

    except Exception as e:
        logger.error(f"RAG query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=RagIngestResponse)
async def ingest_docs(req: RagIngestRequest):
    """批量导入文档到知识库"""
    try:
        count = await service.ingest(req.texts, req.sources)
        return RagIngestResponse(inserted=count)
    except Exception as e:
        logger.error(f"Ingest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
