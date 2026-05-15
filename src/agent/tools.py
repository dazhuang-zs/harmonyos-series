"""Agent 工具定义：RAG 检索、代码生成、错误诊断"""

from abc import ABC, abstractmethod
from typing import Any
import json

from src.rag.service import query as rag_query
from src.codegen.service import generate as codegen_generate
from src.diagnose.service import diagnose as diagnose_error


class Tool(ABC):
    """工具基类"""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def parameters(self) -> dict: ...

    @abstractmethod
    async def execute(self, **kwargs) -> str: ...

    def to_openai_function(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class RAGSearchTool(Tool):
    """知识库检索工具"""

    @property
    def name(self) -> str:
        return "rag_search"

    @property
    def description(self) -> str:
        return "从 HarmonyOS 知识库中检索相关文档。当需要查找鸿蒙开发相关资料、API 用法、最佳实践时使用。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "检索查询文本",
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量，默认 3",
                    "default": 3,
                },
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs) -> str:
        query = kwargs["query"]
        top_k = kwargs.get("top_k", 3)
        result = await rag_query(query, top_k=top_k)
        sources = result.get("sources", [])
        if not sources:
            return "未找到相关文档。"
        parts = []
        for i, src in enumerate(sources, 1):
            parts.append(f"[{i}] (相关度: {src.get('score', 0):.2f}) {src['text'][:500]}")
        return "\n\n".join(parts)


class CodeGenTool(Tool):
    """ArkTS 代码生成工具"""

    @property
    def name(self) -> str:
        return "generate_arkts_code"

    @property
    def description(self) -> str:
        return "根据需求生成 ArkTS/ArkUI 代码。当用户需要生成鸿蒙应用代码时使用。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "requirement": {
                    "type": "string",
                    "description": "代码需求描述",
                },
                "include_tests": {
                    "type": "boolean",
                    "description": "是否生成单元测试，默认 false",
                    "default": False,
                },
            },
            "required": ["requirement"],
        }

    async def execute(self, **kwargs) -> str:
        requirement = kwargs["requirement"]
        include_tests = kwargs.get("include_tests", False)
        result = await codegen_generate(requirement, include_tests=include_tests)
        return result.get("code", "代码生成失败。")


class DiagnoseTool(Tool):
    """错误诊断工具"""

    @property
    def name(self) -> str:
        return "diagnose_error"

    @property
    def description(self) -> str:
        return "诊断 HarmonyOS 编译错误或运行时错误，给出修复方案。当用户粘贴错误信息时使用。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "error_message": {
                    "type": "string",
                    "description": "错误信息文本",
                },
                "code_context": {
                    "type": "string",
                    "description": "出错的代码片段（可选）",
                    "default": "",
                },
            },
            "required": ["error_message"],
        }

    async def execute(self, **kwargs) -> str:
        error_message = kwargs["error_message"]
        code_context = kwargs.get("code_context", "")
        result = await diagnose_error(error_message, code_context)
        return result.get("diagnosis", "诊断失败。")


# 工具注册表
TOOL_REGISTRY: dict[str, Tool] = {}


def register_tool(tool: Tool):
    TOOL_REGISTRY[tool.name] = tool


def get_all_tools() -> list[Tool]:
    return list(TOOL_REGISTRY.values())


def get_openai_tools() -> list[dict]:
    return [tool.to_openai_function() for tool in TOOL_REGISTRY.values()]


# 注册默认工具
register_tool(RAGSearchTool())
register_tool(CodeGenTool())
register_tool(DiagnoseTool())
