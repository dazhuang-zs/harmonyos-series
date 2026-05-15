import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.cache.semantic_cache import SemanticCache


class TestSemanticCache:
    @pytest.mark.asyncio
    async def test_cache_miss(self):
        cache = SemanticCache()
        result = await cache.get("test query")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_put_and_hit(self):
        cache = SemanticCache(similarity_threshold=0.5)

        with patch("src.cache.semantic_cache.get_embedding_provider") as mock_provider:
            mock_embed = AsyncMock(return_value=[1.0] + [0.0] * 1023)
            mock_provider.return_value.embed_query = mock_embed

            await cache.put("test query", "test answer", [{"text": "doc"}])
            result = await cache.get("test query")

            assert result is not None
            assert result["answer"] == "test answer"
            assert result["cache_hit"] is True

    def test_cache_stats(self):
        cache = SemanticCache()
        stats = cache.stats()
        assert stats["size"] == 0
        assert stats["max_size"] == 1000

    @pytest.mark.asyncio
    async def test_cache_eviction(self):
        cache = SemanticCache(max_size=2)

        with patch("src.cache.semantic_cache.get_embedding_provider") as mock_provider:
            mock_provider.return_value.embed_query = AsyncMock(return_value=[1.0] + [0.0] * 1023)

            await cache.put("q1", "a1")
            await cache.put("q2", "a2")
            await cache.put("q3", "a3")

            assert cache.stats()["size"] == 2
