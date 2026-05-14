from fastapi import APIRouter

from src.migrate.schemas import MigrateRequest, MigrateResponse
from src.migrate import service

router = APIRouter(prefix="/api/v1/migrate", tags=["代码迁移"])


@router.post("/", response_model=MigrateResponse)
async def migrate_code(req: MigrateRequest):
    """Android 代码迁移为 ArkTS"""
    result = await service.migrate(req.android_code, req.source_language, req.target_framework)
    return MigrateResponse(
        migrated_code=result["migrated_code"],
        migration_notes=result["migration_notes"],
        before_after=result["before_after"],
    )
