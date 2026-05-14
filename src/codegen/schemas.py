from pydantic import BaseModel


class CodeGenRequest(BaseModel):
    requirement: str
    language: str = "ArkTS"  # ArkTS / ArkUI
    include_tests: bool = False


class CodeGenResponse(BaseModel):
    code: str
    files: list[dict]  # [{filename, content}]
    explanation: str
