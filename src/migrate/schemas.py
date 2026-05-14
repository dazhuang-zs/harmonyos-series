from pydantic import BaseModel


class MigrateRequest(BaseModel):
    android_code: str
    source_language: str = "Kotlin"  # Kotlin / Java
    target_framework: str = "ArkTS"


class MigrateResponse(BaseModel):
    migrated_code: str
    migration_notes: list[str]
    before_after: dict  # {before: str, after: str}
