from pydantic import BaseModel


class PublishRequest(BaseModel):
    title: str
    content: str  # Markdown 格式
    tags: list[str] = []
    categories: list[str] = ["HarmonyOS"]


class PublishResponse(BaseModel):
    article_id: str
    url: str
    status: str  # draft / published
