import pytest
from unittest.mock import AsyncMock, patch

from src.rag.service import query, ingest


@pytest.mark.asyncio
async def test_query_returns_answer():
    with (
        patch("src.rag.service.get_llm_provider") as mock_llm,
        patch("src.rag.service.get_embedding_provider") as mock_embed,
        patch("src.rag.service.search_similar") as mock_search,
    ):
        mock_embed.return_value.embed_query = AsyncMock(return_value=[0.1] * 1024)
        mock_search.return_value = [
            {"text": "test doc", "source": "test.md", "score": 0.9}
        ]
        mock_llm.return_value.chat = AsyncMock(return_value="test answer")

        result = await query("test question")

        assert "answer" in result
        assert "sources" in result
        assert result["answer"] == "test answer"


@pytest.mark.asyncio
async def test_ingest_inserts_documents():
    with (
        patch("src.rag.service.get_embedding_provider") as mock_embed,
        patch("src.rag.service.insert_documents") as mock_insert,
    ):
        mock_embed.return_value.embed = AsyncMock(return_value=[[0.1] * 1024])
        mock_insert.return_value = None

        count = await ingest(["test text"], ["test.md"])

        assert count == 1
