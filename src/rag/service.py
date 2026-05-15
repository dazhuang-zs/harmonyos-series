"""RAG 服务：文档问答 + 流式输出 + 语义缓存 + 安全防护"""

from typing import AsyncIterator
import uuid

from src.core.llm_provider import get_llm_provider
from src.core.embedding_provider import get_embedding_provider
from src.core.vector_store import search_similar, insert_documents
from src.cache.semantic_cache import semantic_cache
from src.guardrails.input_filter import input_filter
from src.guardrails.output_filter import output_filter
from src.observability.tracer import tracer

RAG_SYSTEM_PROMPT = """你是 HarmonyOS 开发助手，专注于鸿蒙应用开发领域。
请根据提供的参考文档回答用户问题。如果文档中没有相关信息，请明确告知。
回答时请：
1. 引用具体的文档来源
2. 提供代码示例（如果适用）
3. 使用中文回答"""


async def _build_context(question: str, top_k: int) -> tuple[list[dict], str]:
    """构建检索上下文（Milvus 不可用时降级为纯 LLM 问答）"""
    try:
        embedding_provider = get_embedding_provider()
        query_embedding = await embedding_provider.embed_query(question)
        docs = await search_similar(query_embedding, top_k=top_k)
        context = "\n\n---\n\n".join(
            [f"【来源：{doc['source']}】\n{doc['text']}" for doc in docs]
        )
        return docs, context
    except Exception:
        # Milvus 不可用，降级为无检索的 LLM 问答
        return [], ""


def _build_messages(context: str, question: str) -> list[dict]:
    if context:
        user_content = f"参考文档：\n{context}\n\n用户问题：{question}"
    else:
        user_content = question
    return [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


async def query(question: str, top_k: int = 5) -> dict:
    """RAG 问答流程：安全检查 → 缓存 → Embedding → 检索 → LLM 生成 → 输出校验"""
    trace = tracer.start_trace(uuid.uuid4().hex[:12], "rag_query", {"question": question[:100]})

    # 1. 输入安全检查
    safety = input_filter.check(question)
    if not safety["safe"]:
        return {"answer": f"输入被安全过滤器拦截: {safety['reason']}", "sources": []}

    question = input_filter.sanitize(question)

    # 2. 语义缓存检查（容错）
    try:
        cached = await semantic_cache.get(question)
        if cached:
            return {"answer": cached["answer"], "sources": cached.get("sources", []), "cache_hit": True}
    except Exception:
        pass  # 缓存不可用时跳过

    # 3. 检索
    llm_provider = get_llm_provider()
    async with tracer.trace_span("retrieval", {"top_k": top_k}):
        docs, context = await _build_context(question, top_k)

    # 4. LLM 生成
    messages = _build_messages(context, question)
    async with tracer.trace_span("llm_generation"):
        answer = await llm_provider.chat(messages)

    # 5. 输出安全校验
    output_check = output_filter.check(answer)
    if not output_check["safe"]:
        answer = output_filter.sanitize(answer)
        answer += "\n\n> ⚠️ 注意：回答中可能包含不安全内容，已自动过滤。"

    # 6. 写入缓存（容错）
    try:
        await semantic_cache.put(question, answer, docs)
    except Exception:
        pass  # 缓存写入失败不影响主流程

    return {"answer": answer, "sources": docs}


async def query_stream(question: str, top_k: int = 5) -> AsyncIterator[str]:
    """RAG 问答流程（流式输出）"""
    # 输入安全检查
    safety = input_filter.check(question)
    if not safety["safe"]:
        yield f"输入被安全过滤器拦截: {safety['reason']}"
        return

    question = input_filter.sanitize(question)

    # 缓存检查（容错）
    try:
        cached = await semantic_cache.get(question)
        if cached:
            yield cached["answer"]
            return
    except Exception:
        pass

    llm_provider = get_llm_provider()
    docs, context = await _build_context(question, top_k)
    messages = _build_messages(context, question)

    full_answer = ""
    async for chunk in llm_provider.chat_stream(messages):
        full_answer += chunk
        yield chunk

    # 写入缓存（容错）
    try:
        await semantic_cache.put(question, full_answer, docs)
    except Exception:
        pass


async def ingest(texts: list[str], sources: list[str]) -> int:
    """批量导入文档到知识库"""
    embedding_provider = get_embedding_provider()

    embeddings = await embedding_provider.embed(texts)
    await insert_documents(texts, sources, embeddings)

    return len(texts)
