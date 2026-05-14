from src.core.llm_provider import get_llm_provider

CODEGEN_SYSTEM_PROMPT = """你是一位 HarmonyOS 开发专家，擅长 ArkTS/ArkUI 编程。
请根据用户需求生成可运行的 ArkTS 代码。

要求：
1. 使用 HarmonyOS NEXT API（API 12+）
2. 遵循 ArkTS 语法规范（严格模式）
3. 包含必要的 import 语句
4. 代码结构清晰，有简要注释
5. 如果需要多个文件，用 === FILE: filename === 分隔"""


async def generate(requirement: str, language: str = "ArkTS", include_tests: bool = False) -> dict:
    """根据需求生成 ArkTS 代码"""
    llm_provider = get_llm_provider()

    prompt = f"请用 {language} 实现以下需求：\n\n{requirement}"
    if include_tests:
        prompt += "\n\n请同时生成单元测试代码。"

    messages = [
        {"role": "system", "content": CODEGEN_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    result = await llm_provider.chat(messages)

    # 解析多文件输出
    files = _parse_files(result)

    return {
        "code": result,
        "files": files,
        "explanation": f"根据需求生成了 {len(files)} 个文件" if files else "生成完成",
    }


def _parse_files(content: str) -> list[dict]:
    """解析 === FILE: xxx === 格式的多文件输出"""
    files = []
    parts = content.split("=== FILE:")
    if len(parts) <= 1:
        return [{"filename": "main.ets", "content": content}]

    for part in parts[1:]:
        if "===" in part:
            filename, file_content = part.split("===" , 1)
            files.append({
                "filename": filename.strip(),
                "content": file_content.strip(),
            })
    return files
