import logging
from fastapi import APIRouter, HTTPException

from src.diagnose.schemas import DiagnoseRequest, DiagnoseResponse
from src.diagnose import service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/diagnose", tags=["错误诊断"])


@router.post("/", response_model=DiagnoseResponse)
async def diagnose_error(req: DiagnoseRequest):
    """诊断编译/运行时错误"""
    try:
        result = await service.diagnose(req.error_message, req.code_context)
        return DiagnoseResponse(
            diagnosis=result["diagnosis"],
            fix_suggestions=result["fix_suggestions"],
            related_docs=result["related_docs"],
        )
    except Exception as e:
        logger.error(f"Diagnose error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
