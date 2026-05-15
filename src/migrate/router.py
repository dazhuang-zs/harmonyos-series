import logging
from fastapi import APIRouter, HTTPException

from src.migrate.schemas import MigrateRequest, MigrateResponse
from src.migrate import service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/migrate", tags=["代码迁移"])


@router.post("/", response_model=MigrateResponse)
async def migrate_code(req: MigrateRequest):
    """Android 代码迁移为 ArkTS"""
    try:
        result = await service.migrate(req.android_code, req.source_language, req.target_framework)
        return MigrateResponse(
            migrated_code=result["migrated_code"],
            migration_notes=result["migration_notes"],
            before_after=result["before_after"],
        )
    except Exception as e:
        logger.error(f"Migrate error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
