"""语义缓存：相似问题向量匹配命中缓存，减少重复 LLM 调用"""

import hashlib
import json
import time
from dataclasses import dataclass, field

from src.core.embedding_provider import get_embedding_provider


@dataclass
class CacheEntry:
    query_hash: str
    query: str
    query_embedding: list[float]
    answer: str
    sources: list[dict] = field(default_factory=list)
    hit_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_hit: float = field(default_factory=time.time)


class SemanticCache:
    """语义缓存实现"""

    def __init__(self, similarity_threshold: float = 0.95, max_size: int = 1000):
        self.similarity_threshold = similarity_threshold
        self.max_size = max_size
        self._cache: dict[str, CacheEntry] = {}

    async def get(self, query: str) -> dict | None:
        """查找相似问题的缓存"""
        if not self._cache:
            return None

        embedding_provider = get_embedding_provider()
        query_embedding = await embedding_provider.embed_query(query)

        best_match = None
        best_score = 0.0

        for entry in self._cache.values():
            score = self._cosine_similarity(query_embedding, entry.query_embedding)
            if score > best_score:
                best_score = score
                best_match = entry

        if best_match and best_score >= self.similarity_threshold:
            best_match.hit_count += 1
            best_match.last_hit = time.time()
            return {
                "answer": best_match.answer,
                "sources": best_match.sources,
                "cache_hit": True,
                "similarity": best_score,
            }

        return None

    async def put(self, query: str, answer: str, sources: list[dict] | None = None):
        """缓存问答对"""
        embedding_provider = get_embedding_provider()
        query_embedding = await embedding_provider.embed_query(query)

        query_hash = hashlib.md5(query.encode()).hexdigest()

        self._cache[query_hash] = CacheEntry(
            query_hash=query_hash,
            query=query,
            query_embedding=query_embedding,
            answer=answer,
            sources=sources or [],
        )

        # LRU 淘汰
        if len(self._cache) > self.max_size:
            oldest = min(self._cache.values(), key=lambda e: e.last_hit)
            self._cache.pop(oldest.query_hash)

    def stats(self) -> dict:
        """缓存统计"""
        entries = list(self._cache.values())
        return {
            "size": len(entries),
            "max_size": self.max_size,
            "total_hits": sum(e.hit_count for e in entries),
            "avg_similarity_threshold": self.similarity_threshold,
        }

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)


# 全局缓存实例
semantic_cache = SemanticCache()
