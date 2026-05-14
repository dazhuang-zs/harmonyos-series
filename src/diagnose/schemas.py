from pydantic import BaseModel


class DiagnoseRequest(BaseModel):
    error_message: str
    code_context: str = ""  # 可选：出错的代码片段


class DiagnoseResponse(BaseModel):
    diagnosis: str
    fix_suggestions: list[str]
    related_docs: list[dict]
