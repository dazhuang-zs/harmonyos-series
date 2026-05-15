"""
将分块数据批量导入 Milvus 向量数据库

用法：
    python scripts/ingest_chunks.py
    python scripts/ingest_chunks.py --chunks data/chunks/chunks.json
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.embedding_provider import get_embedding_provider
from src.core.vector_store import insert_documents, connect_milvus


async def ingest_all(chunks_file: str, batch_size: int = 32):
    """批量导入 chunks 到 Milvus"""
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"加载了 {len(chunks)} 个 chunks")

    # 连接 Milvus
    connect_milvus()
    embedding_provider = get_embedding_provider()

    texts = [c["text"] for c in chunks]
    sources = [
        f"{c.get('source', '')} | {c.get('heading_chain', '')}"
        for c in chunks
    ]

    # 分批向量化并入库
    total_inserted = 0
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_sources = sources[i : i + batch_size]

        print(f"处理批次 {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}...")

        embeddings = await embedding_provider.embed(batch_texts)
        await insert_documents(batch_texts, batch_sources, embeddings)

        total_inserted += len(batch_texts)
        print(f"  已入库: {total_inserted}/{len(texts)}")

    print(f"\n入库完成！共导入 {total_inserted} 个文档块。")


async def ingest_from_manual(texts: list[str], sources: list[str]):
    """手动导入文本（用于 API 调用）"""
    connect_milvus()
    embedding_provider = get_embedding_provider()

    embeddings = await embedding_provider.embed(texts)
    await insert_documents(texts, sources, embeddings)

    return len(texts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文档入库工具")
    parser.add_argument(
        "--chunks",
        default="data/chunks/chunks.json",
        help="chunks JSON 文件路径",
    )
    parser.add_argument("--batch-size", type=int, default=32, help="批处理大小")
    args = parser.parse_args()

    asyncio.run(ingest_all(args.chunks, args.batch_size))
