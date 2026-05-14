from abc import ABC, abstractmethod

from src.core.config import get_settings


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
        from sentence_transformers import SentenceTransformer

        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model_path)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    async def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()


def get_embedding_provider() -> EmbeddingProvider:
    """返回 Embedding Provider 实例"""
    return BGEEmbedding()
