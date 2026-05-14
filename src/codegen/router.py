from fastapi import APIRouter

from src.codegen.schemas import CodeGenRequest, CodeGenResponse
from src.codegen import service

router = APIRouter(prefix="/api/v1/codegen", tags=["ArkTS 代码生成"])


@router.post("/generate", response_model=CodeGenResponse)
async def generate_code(req: CodeGenRequest):
    """根据需求生成 ArkTS 代码"""
    result = await service.generate(req.requirement, req.language, req.include_tests)
    return CodeGenResponse(
        code=result["code"],
        files=result["files"],
        explanation=result["explanation"],
    )
