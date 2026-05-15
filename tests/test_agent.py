import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.agent.tools import RAGSearchTool, CodeGenTool, DiagnoseTool, TOOL_REGISTRY
from src.agent.react_engine import run_react, _parse_tool_call, _is_tool_call


class TestTools:
    def test_tool_registry_has_default_tools(self):
        assert "rag_search" in TOOL_REGISTRY
        assert "generate_arkts_code" in TOOL_REGISTRY
        assert "diagnose_error" in TOOL_REGISTRY

    def test_rag_search_tool_schema(self):
        tool = RAGSearchTool()
        assert tool.name == "rag_search"
        schema = tool.to_openai_function()
        assert schema["type"] == "function"
        assert "query" in schema["function"]["parameters"]["properties"]

    def test_codegen_tool_schema(self):
        tool = CodeGenTool()
        assert tool.name == "generate_arkts_code"
        schema = tool.to_openai_function()
        assert "requirement" in schema["function"]["parameters"]["properties"]

    def test_diagnose_tool_schema(self):
        tool = DiagnoseTool()
        assert tool.name == "diagnose_error"
        schema = tool.to_openai_function()
        assert "error_message" in schema["function"]["parameters"]["properties"]


class TestReActEngine:
    def test_parse_tool_call_text_format(self):
        response = 'Thought: 需要检索文档\nAction: rag_search\nAction Input: {"query": "Button 组件"}'
        result = _parse_tool_call(response)
        assert result is not None
        assert result["name"] == "rag_search"
        assert result["args"]["query"] == "Button 组件"

    def test_is_tool_call_text_format(self):
        response = 'Thought: 需要检索\nAction: rag_search\nAction Input: {"query": "test"}'
        assert _is_tool_call(response) is True

    def test_is_not_tool_call(self):
        response = "这是一个普通的回答，不包含工具调用。"
        assert _is_tool_call(response) is False

    @pytest.mark.asyncio
    async def test_run_react_direct_answer(self):
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="直接回答：Button 是 ArkUI 的基础组件。")

        result = await run_react(mock_llm, "什么是 Button？")
        assert "Button" in result.answer
        assert len(result.steps) == 1
        assert result.steps[0].step_type == "answer"
