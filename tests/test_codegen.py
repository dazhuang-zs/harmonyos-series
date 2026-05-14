import pytest
from unittest.mock import AsyncMock, patch

from src.codegen.service import generate


@pytest.mark.asyncio
async def test_generate_returns_code():
    with patch("src.codegen.service.get_llm_provider") as mock_llm:
        mock_llm.return_value.chat = AsyncMock(
            return_value='=== FILE: main.ets ===\n@Entry\n@Component\nstruct Main {}\n=== FILE: Index.ets ===\n@Component\nstruct Index {}'
        )

        result = await generate("创建一个简单的 Hello World 页面")

        assert "code" in result
        assert "files" in result
        assert len(result["files"]) == 2
        assert result["files"][0]["filename"] == "main.ets"


@pytest.mark.asyncio
async def test_generate_single_file():
    with patch("src.codegen.service.get_llm_provider") as mock_llm:
        mock_llm.return_value.chat = AsyncMock(return_value="@Entry\n@Component\nstruct Main {}")

        result = await generate("创建一个简单的页面")

        assert len(result["files"]) == 1
        assert result["files"][0]["filename"] == "main.ets"
