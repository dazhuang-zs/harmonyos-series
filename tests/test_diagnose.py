import pytest
from unittest.mock import AsyncMock, patch

from src.diagnose.service import diagnose


@pytest.mark.asyncio
async def test_diagnose_returns_diagnosis():
    with (
        patch("src.diagnose.service.get_llm_provider") as mock_llm,
        patch("src.diagnose.service.get_embedding_provider") as mock_embed,
        patch("src.diagnose.service.search_similar") as mock_search,
    ):
        mock_llm.return_value.chat = AsyncMock(
            return_value="错误原因：模块未找到\n1. 检查 import 路径\n2. 清理构建缓存"
        )
        mock_embed.return_value.embed_query = AsyncMock(return_value=[0.1] * 1024)
        mock_search.return_value = [
            {"text": "related error case", "source": "errors.md", "score": 0.85}
        ]

        result = await diagnose("Cannot find module '@ohos/net'", "")

        assert "diagnosis" in result
        assert "fix_suggestions" in result
        assert "related_docs" in result
        assert len(result["fix_suggestions"]) > 0


@pytest.mark.asyncio
async def test_diagnose_with_code_context():
    with (
        patch("src.diagnose.service.get_llm_provider") as mock_llm,
        patch("src.diagnose.service.get_embedding_provider") as mock_embed,
        patch("src.diagnose.service.search_similar") as mock_search,
    ):
        mock_llm.return_value.chat = AsyncMock(return_value="类型不匹配\n1. 检查类型定义")
        mock_embed.return_value.embed_query = AsyncMock(return_value=[0.1] * 1024)
        mock_search.return_value = []

        result = await diagnose("Type error", "let x: string = 42")

        assert result["diagnosis"] == "类型不匹配\n1. 检查类型定义"
