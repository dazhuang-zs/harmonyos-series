"""ReAct 引擎：思考 → 行动 → 观察 循环"""

import json
import logging
from dataclasses import dataclass, field
from typing import AsyncIterator

from src.core.llm_provider import LLMProvider
from src.agent.tools import TOOL_REGISTRY, get_openai_tools

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 5

REACT_SYSTEM_PROMPT = """你是 HarmonyOS 开发助手 Agent。你可以使用工具来帮助用户解决问题。

可用工具：
{tool_descriptions}

请遵循 ReAct 模式：
1. **Thought**: 分析用户需求，决定下一步行动
2. **Action**: 调用合适的工具获取信息
3. **Observation**: 观察工具返回结果
4. 重复上述步骤直到获得足够信息
5. **Final Answer**: 给出最终回答

重要规则：
- 每次只调用一个工具
- 如果工具返回的信息足够，直接给出最终答案
- 最多执行 {max_iterations} 轮工具调用
- 最终答案请用中文，包含代码示例（如适用）"""


@dataclass
class AgentStep:
    """Agent 单步记录"""
    step_type: str  # thought / action / observation / answer
    content: str
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Agent 执行结果"""
    answer: str
    steps: list[AgentStep]
    total_tokens: int = 0


async def run_react(
    llm: LLMProvider,
    user_message: str,
    chat_history: list[dict] | None = None,
    max_iterations: int = MAX_ITERATIONS,
) -> AgentResult:
    """执行 ReAct 循环"""
    tool_desc = "\n".join(
        f"- {t.name}: {t.description}" for t in TOOL_REGISTRY.values()
    )
    system_prompt = REACT_SYSTEM_PROMPT.format(
        tool_descriptions=tool_desc,
        max_iterations=max_iterations,
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    steps: list[AgentStep] = []
    tools = get_openai_tools()

    for i in range(max_iterations):
        # 调用 LLM，支持 function calling
        response = await llm.chat(messages, tools=tools, tool_choice="auto")

        # 检查是否有 tool_calls
        # 注意：chat() 返回字符串，需要检查是否需要 tool call
        # 这里用纯文本 ReAct 模式作为后备
        if not _is_tool_call(response):
            # LLM 直接给出了最终答案
            steps.append(AgentStep(step_type="answer", content=response))
            return AgentResult(answer=response, steps=steps)

        # 解析工具调用
        tool_call = _parse_tool_call(response)
        if not tool_call:
            steps.append(AgentStep(step_type="answer", content=response))
            return AgentResult(answer=response, steps=steps)

        steps.append(AgentStep(
            step_type="thought",
            content=f"调用工具: {tool_call['name']}",
            tool_name=tool_call["name"],
            tool_args=tool_call["args"],
        ))

        # 执行工具
        tool = TOOL_REGISTRY.get(tool_call["name"])
        if not tool:
            observation = f"错误：工具 '{tool_call['name']}' 不存在。可用工具：{list(TOOL_REGISTRY.keys())}"
        else:
            try:
                observation = await tool.execute(**tool_call["args"])
            except Exception as e:
                observation = f"工具执行出错: {e}"

        steps.append(AgentStep(step_type="observation", content=observation))

        # 将对话继续
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    # 达到最大轮次，强制生成最终答案
    messages.append({"role": "user", "content": "请根据以上所有观察结果，给出最终答案。"})
    final_answer = await llm.chat(messages)
    steps.append(AgentStep(step_type="answer", content=final_answer))
    return AgentResult(answer=final_answer, steps=steps)


async def run_react_stream(
    llm: LLMProvider,
    user_message: str,
    chat_history: list[dict] | None = None,
    max_iterations: int = MAX_ITERATIONS,
) -> AsyncIterator[str]:
    """流式执行 ReAct 循环，逐步输出"""
    tool_desc = "\n".join(
        f"- {t.name}: {t.description}" for t in TOOL_REGISTRY.values()
    )
    system_prompt = REACT_SYSTEM_PROMPT.format(
        tool_descriptions=tool_desc,
        max_iterations=max_iterations,
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    tools = get_openai_tools()

    for i in range(max_iterations):
        # 收集完整响应
        full_response = ""
        async for chunk in llm.chat_stream(messages, tools=tools, tool_choice="auto"):
            full_response += chunk
            yield chunk

        if not _is_tool_call(full_response):
            return

        tool_call = _parse_tool_call(full_response)
        if not tool_call:
            return

        # 输出工具调用标记
        yield f"\n\n> 🔧 调用工具: `{tool_call['name']}`\n"

        tool = TOOL_REGISTRY.get(tool_call["name"])
        if not tool:
            observation = f"错误：工具 '{tool_call['name']}' 不存在。"
        else:
            try:
                observation = await tool.execute(**tool_call["args"])
            except Exception as e:
                observation = f"工具执行出错: {e}"

        yield f"> ✅ 工具返回: {observation[:200]}{'...' if len(observation) > 200 else ''}\n\n"

        messages.append({"role": "assistant", "content": full_response})
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    # 最终答案
    messages.append({"role": "user", "content": "请根据以上所有观察结果，给出最终答案。"})
    async for chunk in llm.chat_stream(messages):
        yield chunk


def _is_tool_call(response: str) -> bool:
    """判断响应是否包含工具调用"""
    try:
        data = json.loads(response)
        return "tool_calls" in data or data.get("role") == "assistant" and "tool_calls" in data
    except (json.JSONDecodeError, TypeError):
        # 纯文本模式：检查是否包含 Action 标记
        return "Action:" in response and "Action Input:" in response


def _parse_tool_call(response: str) -> dict | None:
    """解析工具调用（支持 JSON 和纯文本两种格式）"""
    # 尝试 JSON 格式
    try:
        data = json.loads(response)
        if "tool_calls" in data:
            tc = data["tool_calls"][0]
            return {
                "name": tc["function"]["name"],
                "args": json.loads(tc["function"]["arguments"]),
            }
    except (json.JSONDecodeError, TypeError, KeyError, IndexError):
        pass

    # 纯文本 ReAct 格式
    lines = response.strip().split("\n")
    tool_name = None
    tool_input = None

    for line in lines:
        line = line.strip()
        if line.startswith("Action:"):
            tool_name = line.split(":", 1)[1].strip()
        elif line.startswith("Action Input:"):
            raw = line.split(":", 1)[1].strip()
            try:
                tool_input = json.loads(raw)
            except json.JSONDecodeError:
                tool_input = {"query": raw}

    if tool_name and tool_input is not None:
        return {"name": tool_name, "args": tool_input}

    return None
