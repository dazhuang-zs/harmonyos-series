from src.core.llm_provider import get_llm_provider
from src.core.embedding_provider import get_embedding_provider
from src.core.vector_store import search_similar, insert_documents

RAG_SYSTEM_PROMPT = """你是 HarmonyOS 开发助手，专注于鸿蒙应用开发领域。
请根据提供的参考文档回答用户问题。如果文档中没有相关信息，请明确告知。
回答时请：
1. 引用具体的文档来源
2. 提供代码示例（如果适用）
3. 使用中文回答"""


async def query(question: str, top_k: int = 5) -> dict:
    """RAG 问答流程：Embedding → 检索 → LLM 生成"""
    embedding_provider = get_embedding_provider()
    llm_provider = get_llm_provider()

    # 1. 将问题向量化
    query_embedding = await embedding_provider.embed_query(question)

    # 2. 在 Milvus 中检索相关文档
    docs = await search_similar(query_embedding, top_k=top_k)

    # 3. 拼接 Prompt
    context = "\n\n---\n\n".join(
        [f"【来源：{doc['source']}】\n{doc['text']}" for doc in docs]
    )

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"参考文档：\n{context}\n\n用户问题：{question}",
        },
    ]

    # 4. 调用 LLM 生成答案
    answer = await llm_provider.chat(messages)

    return {"answer": answer, "sources": docs}


async def ingest(texts: list[str], sources: list[str]) -> int:
    """批量导入文档到知识库"""
    embedding_provider = get_embedding_provider()

    # 1. 批量向量化
    embeddings = await embedding_provider.embed(texts)

    # 2. 存入 Milvus
    await insert_documents(texts, sources, embeddings)

    return len(texts)
