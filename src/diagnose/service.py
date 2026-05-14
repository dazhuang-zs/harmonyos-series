from src.core.llm_provider import get_llm_provider
from src.core.embedding_provider import get_embedding_provider
from src.core.vector_store import search_similar

DIAGNOSE_SYSTEM_PROMPT = """你是 HarmonyOS 开发专家，擅长诊断编译错误和运行时问题。
请根据错误信息分析原因并给出修复方案。

回答格式：
1. 错误原因分析
2. 分步修复方案（含代码示例）
3. 预防建议"""


async def diagnose(error_message: str, code_context: str = "") -> dict:
    """诊断编译/运行时错误"""
    llm_provider = get_llm_provider()
    embedding_provider = get_embedding_provider()

    # 1. 检索相似错误案例
    query_embedding = await embedding_provider.embed_query(error_message)
    related_docs = await search_similar(query_embedding, top_k=3)

    # 2. 构建 Prompt
    context = "\n\n".join([doc["text"] for doc in related_docs])
    user_prompt = f"错误信息：\n{error_message}"
    if code_context:
        user_prompt += f"\n\n相关代码：\n```\n{code_context}\n```"
    if context:
        user_prompt += f"\n\n参考案例：\n{context}"

    messages = [
        {"role": "system", "content": DIAGNOSE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # 3. 生成诊断结果
    diagnosis = await llm_provider.chat(messages)

    return {
        "diagnosis": diagnosis,
        "fix_suggestions": _extract_suggestions(diagnosis),
        "related_docs": related_docs,
    }


def _extract_suggestions(diagnosis: str) -> list[str]:
    """从诊断结果中提取修复建议（简单实现）"""
    suggestions = []
    for line in diagnosis.split("\n"):
        line = line.strip()
        if line.startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")):
            suggestions.append(line)
    return suggestions[:5]
