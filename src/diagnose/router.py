from fastapi import APIRouter

from src.diagnose.schemas import DiagnoseRequest, DiagnoseResponse
from src.diagnose import service

router = APIRouter(prefix="/api/v1/diagnose", tags=["错误诊断"])


@router.post("/", response_model=DiagnoseResponse)
async def diagnose_error(req: DiagnoseRequest):
    """诊断编译/运行时错误"""
    result = await service.diagnose(req.error_message, req.code_context)
    return DiagnoseResponse(
        diagnosis=result["diagnosis"],
        fix_suggestions=result["fix_suggestions"],
        related_docs=result["related_docs"],
    )
