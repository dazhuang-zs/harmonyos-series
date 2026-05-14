from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.rag.router import router as rag_router
from src.codegen.router import router as codegen_router
from src.diagnose.router import router as diagnose_router
from src.migrate.router import router as migrate_router
from src.publish.router import router as publish_router

app = FastAPI(
    title="HarmonyOS 开发助手",
    description="MiMo 大模型驱动的鸿蒙开发助手，提供 RAG 问答、代码生成、错误诊断、代码迁移和 CSDN 发布功能。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)
app.include_router(codegen_router)
app.include_router(diagnose_router)
app.include_router(migrate_router)
app.include_router(publish_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
