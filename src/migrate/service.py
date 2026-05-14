from src.core.llm_provider import get_llm_provider

MIGRATE_SYSTEM_PROMPT = """你是 Android → HarmonyOS 迁移专家。
请将用户提供的 Android Java/Kotlin 代码转换为等价的 ArkTS 实现。

转换规则：
1. Android XML 布局 → ArkUI 声明式 UI
2. Activity/Fragment → @Component + @Entry
3. Retrofit/OkHttp → @ohos.net.http
4. SharedPreferences → @ohos.data.preferences
5. RecyclerView → List + LazyColumn 等价物
6. ViewModel → @State + AppStorage
7. Intent → router / navigation

请在代码中用注释标注关键的迁移差异。"""


async def migrate(android_code: str, source_language: str = "Kotlin", target_framework: str = "ArkTS") -> dict:
    """将 Android 代码转换为 ArkTS"""
    llm_provider = get_llm_provider()

    messages = [
        {"role": "system", "content": MIGRATE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"请将以下 {source_language} 代码转换为 {target_framework}：\n\n```{source_language.lower()}\n{android_code}\n```",
        },
    ]

    result = await llm_provider.chat(messages)

    return {
        "migrated_code": result,
        "migration_notes": _extract_notes(result),
        "before_after": {
            "before": android_code,
            "after": result,
        },
    }


def _extract_notes(code: str) -> list[str]:
    """提取代码中的迁移注释"""
    notes = []
    for line in code.split("\n"):
        if "//" in line and any(kw in line for kw in ["迁移", "注意", "差异", "对应", "替代"]):
            notes.append(line.strip())
    return notes[:10]
