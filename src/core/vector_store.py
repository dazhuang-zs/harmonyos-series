from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections

from src.core.config import get_settings

VECTOR_DIM = 1024  # BGE-Large-ZH 输出维度


def connect_milvus():
    """建立 Milvus 连接"""
    settings = get_settings()
    connections.connect(
        alias="default",
        host=settings.milvus_host,
        port=settings.milvus_port,
    )


def get_or_create_collection(name: str | None = None) -> Collection:
    """获取或创建 Milvus Collection"""
    from pymilvus import utility

    settings = get_settings()
    collection_name = name or settings.milvus_collection

    # 如果集合已存在，直接返回
    if utility.has_collection(collection_name):
        collection = Collection(name=collection_name)
        # 确保索引存在
        if not collection.indexes:
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
            }
            collection.create_index(field_name="embedding", index_params=index_params)
        return collection

    # 创建新集合
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1024),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
    ]
    schema = CollectionSchema(fields=fields, description="HarmonyOS docs knowledge base")

    collection = Collection(name=collection_name, schema=schema)

    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
    }
    collection.create_index(field_name="embedding", index_params=index_params)

    return collection


async def search_similar(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """在 Milvus 中检索相似文档"""
    collection = get_or_create_collection()
    collection.load()

    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"nprobe": 16}},
        limit=top_k,
        output_fields=["text", "source"],
    )

    return [
        {
            "text": hit.entity.get("text"),
            "source": hit.entity.get("source"),
            "score": hit.score,
        }
        for hit in results[0]
    ]


async def insert_documents(texts: list[str], sources: list[str], embeddings: list[list[float]]):
    """批量插入文档到 Milvus"""
    collection = get_or_create_collection()
    collection.insert([texts, sources, embeddings])
    collection.flush()
