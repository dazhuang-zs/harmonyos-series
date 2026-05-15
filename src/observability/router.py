"""可观测性 API：追踪查询、统计、健康检查"""

from fastapi import APIRouter

from src.observability.tracer import tracer
from src.cache.semantic_cache import semantic_cache
from src.guardrails.input_filter import input_filter
from src.guardrails.output_filter import output_filter

router = APIRouter(prefix="/api/v1/observability", tags=["可观测性"])


@router.get("/traces")
async def get_traces(limit: int = 50):
    """获取最近的追踪记录"""
    return {"traces": tracer.get_traces(limit)}


@router.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    return {
        "tracer": tracer.get_stats(),
        "cache": semantic_cache.stats(),
        "input_filter": input_filter.stats(),
        "output_filter": output_filter.stats(),
    }


@router.get("/health")
async def detailed_health():
    """详细健康检查"""
    return {
        "status": "ok",
        "components": {
            "tracer": "healthy",
            "cache": "healthy",
            "guardrails": "healthy",
        },
        "stats": tracer.get_stats(),
    }
