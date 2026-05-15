import logging
from fastapi import APIRouter, HTTPException

from src.codegen.schemas import CodeGenRequest, CodeGenResponse
from src.codegen import service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/codegen", tags=["ArkTS 代码生成"])


@router.post("/generate", response_model=CodeGenResponse)
async def generate_code(req: CodeGenRequest):
    """根据需求生成 ArkTS 代码"""
    try:
        result = await service.generate(req.requirement, req.language, req.include_tests)
        return CodeGenResponse(
            code=result["code"],
            files=result["files"],
            explanation=result["explanation"],
        )
    except Exception as e:
        logger.error(f"CodeGen error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
