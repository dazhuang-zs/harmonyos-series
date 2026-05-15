import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.rag.router import router as rag_router
from src.codegen.router import router as codegen_router
from src.diagnose.router import router as diagnose_router
from src.migrate.router import router as migrate_router
from src.publish.router import router as publish_router
from src.agent.router import router as agent_router
from src.memory.router import router as memory_router
from src.chat.router import router as chat_router
from src.observability.router import router as observability_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="HarmonyOS 开发助手",
    description="MiMo 大模型驱动的鸿蒙开发助手，提供 RAG 问答、代码生成、错误诊断、代码迁移、CSDN 发布、Agent 工具调用、对话管理和可观测性功能。",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 核心功能路由
app.include_router(rag_router)
app.include_router(codegen_router)
app.include_router(diagnose_router)
app.include_router(migrate_router)
app.include_router(publish_router)

# 新增路由
app.include_router(agent_router)
app.include_router(memory_router)
app.include_router(chat_router)
app.include_router(observability_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.2.0"}
