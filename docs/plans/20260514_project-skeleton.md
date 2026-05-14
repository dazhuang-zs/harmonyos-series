# 设计稿：项目骨架搭建

**日期**：2026-05-14
**状态**：实施中

## 目标

搭建 HarmonyOS 开发助手的完整项目骨架，包含所有模块的目录结构、核心抽象层、API 路由定义和基础配置。

## 项目结构

```
harmonyos-mimo-assistant/
├── .gitignore
├── .env.example
├── requirements.txt
├── README.md
├── docs/
│   ├── project_proposal_zh.md
│   └── plans/
│       └── 20260514_project-skeleton.md
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI 入口
│   ├── core/                       # 核心共享模块
│   │   ├── __init__.py
│   │   ├── config.py               # 环境变量 / 配置管理
│   │   ├── llm_provider.py         # LLM 抽象层（MiMo / DeepSeek / OpenAI）
│   │   ├── embedding_provider.py   # Embedding 抽象层（BGE-Large-ZH）
│   │   └── vector_store.py         # Milvus 向量数据库连接
│   ├── rag/                        # RAG 文档问答
│   │   ├── __init__.py
│   │   ├── router.py               # API 路由
│   │   ├── service.py              # 业务逻辑
│   │   └── schemas.py              # 请求/响应模型
│   ├── codegen/                    # ArkTS 代码生成
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── diagnose/                   # 错误诊断
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── migrate/                    # Android → ArkTS 迁移
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   └── publish/                    # CSDN 文章发布
│       ├── __init__.py
│       ├── router.py
│       ├── service.py
│       └── schemas.py
├── scripts/
│   └── crawl_huawei_docs.py        # 华为文档爬虫（Playwright）
├── tests/
│   ├── __init__.py
│   ├── test_rag.py
│   └── test_codegen.py
└── config/
    └── example.env                 # 环境变量示例
```

## 核心设计决策

### 1. LLM 抽象层

统一接口，支持多后端切换：

```python
class LLMProvider(ABC):
    async def chat(messages, **kwargs) -> str
    async def chat_stream(messages, **kwargs) -> AsyncIterator[str]

class MiMoProvider(LLMProvider)      # 主力
class DeepSeekProvider(LLMProvider)  # 备用（OpenAI 兼容）
```

通过 `.env` 的 `LLM_PROVIDER` 一行切换。

### 2. Embedding 抽象层

```python
class EmbeddingProvider(ABC):
    async def embed(texts) -> list[list[float]]

class BGEEmbedding(EmbeddingProvider)  # 本地 BGE-Large-ZH
```

### 3. 每个业务模块的三层结构

- **router.py**：FastAPI 路由定义，只做参数校验和响应格式化
- **service.py**：业务逻辑，调用 core 层的 LLM/Embedding/VectorStore
- **schemas.py**：Pydantic 请求/响应模型

### 4. API 路由前缀

| 模块 | 前缀 | 说明 |
|------|------|------|
| rag | `/api/v1/rag` | RAG 文档问答 |
| codegen | `/api/v1/codegen` | 代码生成 |
| diagnose | `/api/v1/diagnose` | 错误诊断 |
| migrate | `/api/v1/migrate` | 代码迁移 |
| publish | `/api/v1/publish` | CSDN 发布 |
