"""对话上下文管理：Token 窗口管理 + 摘要压缩"""

from src.core.llm_provider import LLMProvider
from src.memory.store import Message, store

# Token 预算配置
MAX_CONTEXT_TOKENS = 4000  # 对话历史最大 Token 数
SUMMARY_THRESHOLD = 3000  # 超过此 Token 数触发摘要压缩
SUMMARY_TARGET_TOKENS = 200  # 摘要目标 Token 数

# 简单 Token 估算：1 个中文字符 ≈ 2 tokens
def estimate_tokens(text: str) -> int:
    return len(text) * 2


def build_messages_with_window(
    conversation_id: str,
    system_prompt: str = "",
) -> list[dict]:
    """构建带窗口管理的消息列表"""
    messages = store.get_messages(conversation_id)
    if not messages:
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        return result

    # 从后往前取，直到 Token 预算用完
    selected: list[Message] = []
    total_tokens = 0

    for msg in reversed(messages):
        msg_tokens = estimate_tokens(msg.content)
        if total_tokens + msg_tokens > MAX_CONTEXT_TOKENS:
            break
        selected.insert(0, msg)
        total_tokens += msg_tokens

    # 构建消息列表
    result = []
    if system_prompt:
        result.append({"role": "system", "content": system_prompt})

    # 如果有摘要，插入到最前面
    conv = store.get(conversation_id)
    if conv and conv.user_preferences.get("summary"):
        result.append({
            "role": "system",
            "content": f"之前的对话摘要：{conv.user_preferences['summary']}",
        })

    for msg in selected:
        result.append({"role": msg.role, "content": msg.content})

    return result


async def maybe_summarize(llm: LLMProvider, conversation_id: str) -> str | None:
    """如果对话历史过长，自动摘要压缩"""
    messages = store.get_messages(conversation_id)
    total_tokens = sum(estimate_tokens(m.content) for m in messages)

    if total_tokens < SUMMARY_THRESHOLD:
        return None

    # 取前面的消息做摘要（保留最近 4 轮）
    recent_count = 8  # 4 轮 = 8 条消息
    if len(messages) <= recent_count:
        return None

    old_messages = messages[:-recent_count]
    summary_text = "\n".join(
        f"{m.role}: {m.content[:200]}" for m in old_messages
    )

    summary_prompt = [
        {
            "role": "system",
            "content": "请将以下对话历史压缩为 200 字以内的摘要，保留关键信息（用户需求、已生成的代码、已解决的问题）。",
        },
        {"role": "user", "content": summary_text},
    ]

    summary = await llm.chat(summary_prompt, max_tokens=400)

    # 存储摘要
    store.update_preferences(conversation_id, {"summary": summary})

    return summary


def extract_user_preferences(messages: list[Message]) -> dict:
    """从对话中提取用户偏好（简单关键词匹配）"""
    preferences: dict = {}

    for msg in messages:
        if msg.role != "user":
            continue
        content = msg.content.lower()

        # 代码风格偏好
        if "严格模式" in content or "strict" in content:
            preferences["code_style"] = "strict"
        if "简洁" in content or "简单" in content:
            preferences["code_style"] = "concise"

        # 常用组件
        for component in ["Button", "Text", "Image", "List", "Column", "Row", "Stack"]:
            if component.lower() in content:
                preferences.setdefault("frequent_components", [])
                if component not in preferences["frequent_components"]:
                    preferences["frequent_components"].append(component)

    return preferences
