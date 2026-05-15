import logging
import httpx
from src.core.config import get_settings

logger = logging.getLogger(__name__)
CSDN_API_BASE = "https://bizapi.csdn.net/blog-console-api/v3"


async def publish(
    title: str, content: str, tags: list[str], categories: list[str]
) -> dict:
    """发布文章到 CSDN 草稿箱"""
    settings = get_settings()

    if not settings.csdn_cookie:
        logger.warning("CSDN cookie not configured, returning simulated result")
        return {
            "article_id": "",
            "url": "",
            "status": "not_configured",
        }

    try:
        headers = {
            "Cookie": settings.csdn_cookie,
            "Content-Type": "application/json",
        }

        payload = {
            "title": title,
            "content": content,
            "tags": ",".join(tags) if tags else "",
            "categories": ",".join(categories) if categories else "HarmonyOS",
            "type": "original",
            "status": 0,  # 0=草稿, 1=发布
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CSDN_API_BASE}/post/saveArticle",
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

        article_id = str(data.get("data", {}).get("article_id", ""))

        logger.info(f"Article saved to CSDN draft: {article_id}")
        return {
            "article_id": article_id,
            "url": f"https://blog.csdn.net/weixin_43726381/article/details/{article_id}",
            "status": "draft",
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"CSDN API error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"CSDN publish failed: {e}", exc_info=True)
        raise
