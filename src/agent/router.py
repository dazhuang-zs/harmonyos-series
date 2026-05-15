from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.agent.schemas import AgentRequest, AgentResponse, AgentStepResponse
from src.agent.react_engine import run_react, run_react_stream
from src.core.llm_provider import get_llm_provider

router = APIRouter(prefix="/api/v1/agent", tags=["Agent 工具调用"])


@router.post("/run", response_model=AgentResponse)
async def agent_run(req: AgentRequest):
    """执行 Agent ReAct 循环（非流式）"""
    llm = get_llm_provider()
    result = await run_react(llm, req.message, max_iterations=req.max_iterations)
    return AgentResponse(
        answer=result.answer,
        steps=[
            AgentStepResponse(
                step_type=s.step_type,
                content=s.content,
                tool_name=s.tool_name,
                tool_args=s.tool_args,
            )
            for s in result.steps
        ],
        conversation_id=req.conversation_id,
    )


@router.post("/stream")
async def agent_stream(req: AgentRequest):
    """执行 Agent ReAct 循环（SSE 流式输出）"""
    llm = get_llm_provider()

    async def event_generator():
        async for chunk in run_react_stream(llm, req.message, max_iterations=req.max_iterations):
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
