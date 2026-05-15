import logging
from abc import ABC, abstractmethod

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Embedding 统一抽象接口"""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """将文本列表转换为向量"""
        ...

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """将单条查询文本转换为向量"""
        ...


class BGEEmbedding(EmbeddingProvider):
    """BGE-Large-ZH 本地 Embedding 模型"""

    def __init__(self):
        settings = get_settings()
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.embedding_model_path)
            logger.info("BGE-Large-ZH model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BGE model: {e}")
            raise RuntimeError(
                f"Cannot load embedding model `{settings.embedding_model_path}`: {e}"
            )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    async def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()


class DummyEmbedding(EmbeddingProvider):
    """测试用 Embedding 提供者（返回随机向量）"""

    def __init__(self, dim: int = 1024):
        self.dim = dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        import random
        return [[random.random() for _ in range(self.dim)] for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        import random
        return [random.random() for _ in range(self.dim)]


def get_embedding_provider() -> EmbeddingProvider:
    """返回 Embedding Provider 实例"""
    settings = get_settings()
    if settings.app_env == "test":
        return DummyEmbedding()
    return BGEEmbedding()
