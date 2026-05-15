import pytest
from unittest.mock import AsyncMock, patch

from src.migrate.service import migrate


@pytest.mark.asyncio
async def test_migrate_returns_code():
    with patch("src.migrate.service.get_llm_provider") as mock_llm:
        mock_llm.return_value.chat = AsyncMock(
            return_value=(
                "// 迁移注意：Activity → @Entry @Component\n"
                "@Entry\n@Component\nstruct Main {\n"
                "  build() { Text('Hello') }\n"
                "}"
            )
        )

        result = await migrate("class MainActivity : AppCompatActivity()", "Kotlin")

        assert "migrated_code" in result
        assert "migration_notes" in result
        assert "before_after" in result
        assert "迁移注意" in result["migration_notes"][0]


@pytest.mark.asyncio
async def test_migrate_java_code():
    with patch("src.migrate.service.get_llm_provider") as mock_llm:
        mock_llm.return_value.chat = AsyncMock(return_value="@Component\nstruct Main {}")

        result = await migrate("public class MainActivity {}", "Java")

        assert result["before_after"]["before"] == "public class MainActivity {}"
        assert result["before_after"]["after"] == "@Component\nstruct Main {}"


@pytest.mark.asyncio
async def test_migrate_handles_errors():
    with patch("src.migrate.service.get_llm_provider") as mock_llm:
        mock_llm.return_value.chat = AsyncMock(side_effect=Exception("API error"))

        result = await migrate("some code")

        assert result["migrated_code"] == ""
        assert result["migration_notes"] == []
