from fastapi import APIRouter

from src.publish.schemas import PublishRequest, PublishResponse
from src.publish import service

router = APIRouter(prefix="/api/v1/publish", tags=["CSDN 发布"])


@router.post("/", response_model=PublishResponse)
async def publish_article(req: PublishRequest):
    """发布文章到 CSDN 草稿箱"""
    result = await service.publish(req.title, req.content, req.tags, req.categories)
    return PublishResponse(
        article_id=result["article_id"],
        url=result["url"],
        status=result["status"],
    )
