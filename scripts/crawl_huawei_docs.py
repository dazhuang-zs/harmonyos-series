"""
华为开发者文档爬虫（Playwright + BeautifulSoup）

用法：
    python scripts/crawl_huawei_docs.py

说明：
    华为文档站是 SPA（单页应用），需要 Playwright 渲染后提取内容。
    M1 阶段手动维护 URL 列表，后续扩展为自动发现。
"""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# M1 阶段核心文档 URL（手动整理）
SEED_URLS = [
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/application-dev-guide-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-get-started-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-state-management-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-layout-development-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-page-routing-V5",
]

OUTPUT_DIR = Path("data/docs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def crawl_page(url: str, page) -> dict:
    """爬取单个页面，提取正文内容"""
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)  # 等待 SPA 渲染

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        # 提取正文（选择器需要根据实际页面结构调整）
        content_el = soup.select_one(".doc-content") or soup.select_one("article") or soup.select_one("main")

        if not content_el:
            return {"url": url, "title": "", "content": "", "error": "content not found"}

        title = soup.title.string if soup.title else url.split("/")[-1]
        content = content_el.get_text(separator="\n", strip=True)

        return {"url": url, "title": title, "content": content}
    except Exception as e:
        return {"url": url, "title": "", "content": "", "error": str(e)}


async def main():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for url in SEED_URLS:
            print(f"爬取: {url}")
            result = await crawl_page(url, page)
            results.append(result)

            if result.get("error"):
                print(f"  失败: {result['error']}")
            else:
                print(f"  成功: {len(result['content'])} 字符")

        await browser.close()

    # 保存结果
    output_file = OUTPUT_DIR / "crawled_docs.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n完成！共爬取 {len(results)} 个页面，保存到 {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
