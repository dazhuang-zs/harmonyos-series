"""可观测性：全链路追踪、Token 统计、延迟监控"""

import time
import logging
from dataclasses import dataclass, field
from typing import Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """追踪跨度"""
    span_id: str
    name: str
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    duration_ms: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"  # ok / error
    error: str = ""
    children: list["TraceSpan"] = field(default_factory=list)

    def finish(self, status: str = "ok", error: str = ""):
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status
        self.error = error

    def to_dict(self) -> dict:
        return {
            "span_id": self.span_id,
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "error": self.error,
            "attributes": self.attributes,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class Trace:
    """完整追踪"""
    trace_id: str
    name: str
    spans: list[TraceSpan] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    total_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "duration_ms": round((time.time() - self.start_time) * 1000, 2),
            "total_tokens": self.total_tokens,
            "metadata": self.metadata,
            "spans": [s.to_dict() for s in self.spans],
        }


class Tracer:
    """链路追踪器"""

    def __init__(self):
        self._traces: list[Trace] = []
        self._current_trace: Trace | None = None
        self._span_counter = 0

    def start_trace(self, trace_id: str, name: str, metadata: dict | None = None) -> Trace:
        trace = Trace(trace_id=trace_id, name=name, metadata=metadata or {})
        self._traces.append(trace)
        self._current_trace = trace
        return trace

    @asynccontextmanager
    async def trace_span(self, name: str, attributes: dict | None = None):
        """异步上下文管理器，用于追踪一个操作"""
        self._span_counter += 1
        span = TraceSpan(
            span_id=f"span_{self._span_counter}",
            name=name,
            attributes=attributes or {},
        )

        if self._current_trace:
            self._current_trace.spans.append(span)

        try:
            yield span
            span.finish(status="ok")
        except Exception as e:
            span.finish(status="error", error=str(e))
            raise

    def record_tokens(self, count: int):
        """记录 Token 消耗"""
        if self._current_trace:
            self._current_trace.total_tokens += count

    def get_traces(self, limit: int = 50) -> list[dict]:
        """获取最近的追踪记录"""
        return [t.to_dict() for t in self._traces[-limit:]]

    def get_stats(self) -> dict:
        """获取追踪统计"""
        if not self._traces:
            return {"total_traces": 0}

        durations = []
        total_tokens = 0
        error_count = 0

        for trace in self._traces:
            duration = (time.time() - trace.start_time) * 1000
            durations.append(duration)
            total_tokens += trace.total_tokens
            for span in trace.spans:
                if span.status == "error":
                    error_count += 1

        return {
            "total_traces": len(self._traces),
            "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
            "total_tokens": total_tokens,
            "error_count": error_count,
        }

    def clear(self):
        """清除所有追踪记录"""
        self._traces.clear()
        self._current_trace = None


# 全局追踪器
tracer = Tracer()
