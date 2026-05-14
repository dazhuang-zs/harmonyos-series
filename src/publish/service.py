import httpx
from src.core.config import get_settings

CSDN_API_BASE = "https://bizapi.csdn.net/blog-console-api/v3"


async def publish(title: str, content: str, tags: list[str], categories: list[str]) -> dict:
    """发布文章到 CSDN 草稿箱"""
    settings = get_settings()

    headers = {
        "Cookie": settings.csdn_cookie,
        "Content-Type": "application/json",
    }

    payload = {
        "title": title,
        "content": content,
        "tags": ",".join(tags),
        "categories": ",".join(categories),
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

    return {
        "article_id": article_id,
        "url": f"https://blog.csdn.net/weixin_43726381/article/details/{article_id}",
        "status": "draft",
    }
