"""统一 Chat API：支持多模式 + 流式输出 + 对话记忆"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.chat.schemas import ChatRequest, ChatResponse
from src.core.llm_provider import get_llm_provider
from src.rag.service import query as rag_query, query_stream as rag_query_stream
from src.agent.react_engine import run_react, run_react_stream
from src.codegen.service import generate as codegen_generate
from src.diagnose.service import diagnose as diagnose_error
from src.memory.store import store
from src.memory.context_manager import (
    build_messages_with_window,
    maybe_summarize,
)

router = APIRouter(prefix="/api/v1/chat", tags=["统一 Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """统一聊天入口（非流式）"""
    # 确保有对话 ID
    if not req.conversation_id:
        conv = store.create()
        req.conversation_id = conv.conversation_id

    # 记录用户消息
    store.add_message(req.conversation_id, "user", req.message)

    # 根据模式分发
    if req.mode == "agent":
        result = await _run_agent(req)
    elif req.mode == "codegen":
        result = await _run_codegen(req)
    elif req.mode == "diagnose":
        result = await _run_diagnose(req)
    else:  # rag
        result = await _run_rag(req)

    # 记录助手回复
    store.add_message(req.conversation_id, "assistant", result["reply"])

    # 异步尝试摘要压缩
    llm = get_llm_provider()
    await maybe_summarize(llm, req.conversation_id)

    return ChatResponse(
        reply=result["reply"],
        conversation_id=req.conversation_id,
        mode=req.mode,
        sources=result.get("sources", []),
        steps=result.get("steps", []),
    )


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """统一聊天入口（SSE 流式输出）"""
    req.stream = True

    if not req.conversation_id:
        conv = store.create()
        req.conversation_id = conv.conversation_id

    store.add_message(req.conversation_id, "user", req.message)

    conversation_id = req.conversation_id

    async def event_generator():
        full_reply = ""

        if req.mode == "agent":
            llm = get_llm_provider()
            async for chunk in run_react_stream(llm, req.message):
                full_reply += chunk
                yield f"data: {chunk}\n\n"
        else:
            # RAG 流式
            async for chunk in rag_query_stream(req.message):
                full_reply += chunk
                yield f"data: {chunk}\n\n"

        store.add_message(conversation_id, "assistant", full_reply)
        yield f"data: [DONE:{conversation_id}]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _run_rag(req: ChatRequest) -> dict:
    """RAG 问答模式"""
    result = await rag_query(req.message)
    return {"reply": result["answer"], "sources": result["sources"]}


async def _run_agent(req: ChatRequest) -> dict:
    """Agent 模式"""
    llm = get_llm_provider()
    history = build_messages_with_window(req.conversation_id)
    agent_result = await run_react(llm, req.message, chat_history=history)
    return {
        "reply": agent_result.answer,
        "steps": [
            {"type": s.step_type, "content": s.content, "tool": s.tool_name}
            for s in agent_result.steps
        ],
    }


async def _run_codegen(req: ChatRequest) -> dict:
    """代码生成模式"""
    result = await codegen_generate(req.message)
    return {"reply": result["code"]}


async def _run_diagnose(req: ChatRequest) -> dict:
    """错误诊断模式"""
    result = await diagnose_error(req.message)
    return {"reply": result["diagnosis"]}
