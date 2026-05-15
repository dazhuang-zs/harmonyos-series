"""
华为开发者文档爬虫（Playwright + BeautifulSoup）

用法：
    python scripts/crawl_huawei_docs.py
    python scripts/crawl_huawei_docs.py --ingest  # 爬取后直接入库

说明：
    华为文档站是 SPA（单页应用），需要 Playwright 渲染后提取内容。
    M1 阶段手动维护 URL 列表，后续扩展为自动发现。
"""

import argparse
import asyncio
import hashlib
import json
import re
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
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-component-development-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-common-events-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-data-management-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-network-management-V5",
    "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-custom-components-V5",
]

OUTPUT_DIR = Path("data/docs")
CHUNKS_DIR = Path("data/chunks")


async def crawl_page(url: str, page) -> dict:
    """爬取单个页面，提取正文内容并转为 Markdown"""
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        content_el = (
            soup.select_one(".doc-content")
            or soup.select_one("article")
            or soup.select_one("main")
            or soup.select_one(".markdown-body")
        )

        if not content_el:
            return {"url": url, "title": "", "content": "", "markdown": "", "error": "content not found"}

        title = soup.title.string if soup.title else url.split("/")[-1]
        title = title.replace(" | HarmonyOS", "").replace(" - 华为开发者", "").strip()

        # 转为 Markdown
        markdown = html_to_markdown(content_el)
        content = content_el.get_text(separator="\n", strip=True)

        return {"url": url, "title": title, "content": content, "markdown": markdown}
    except Exception as e:
        return {"url": url, "title": "", "content": "", "markdown": "", "error": str(e)}


def html_to_markdown(element) -> str:
    """将 HTML 元素转换为 Markdown 格式"""
    lines = []

    for child in element.children:
        if not hasattr(child, "name"):
            text = str(child).strip()
            if text:
                lines.append(text)
            continue

        tag = child.name

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            text = child.get_text(strip=True)
            lines.append(f"\n{'#' * level} {text}\n")

        elif tag == "p":
            text = child.get_text(strip=True)
            if text:
                lines.append(f"\n{text}\n")

        elif tag in ("pre", "code"):
            code_el = child.find("code") if tag == "pre" else child
            code_text = code_el.get_text() if code_el else child.get_text()
            lang = ""
            if code_el and code_el.get("class"):
                for cls in code_el["class"]:
                    if cls.startswith("language-"):
                        lang = cls[9:]
                        break
            lines.append(f"\n```{lang}\n{code_text.strip()}\n```\n")

        elif tag == "ul":
            for li in child.find_all("li", recursive=False):
                lines.append(f"- {li.get_text(strip=True)}")

        elif tag == "ol":
            for i, li in enumerate(child.find_all("li", recursive=False), 1):
                lines.append(f"{i}. {li.get_text(strip=True)}")

        elif tag == "table":
            rows = child.find_all("tr")
            for i, row in enumerate(rows):
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                lines.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    lines.append("| " + " | ".join(["---"] * len(cells)) + " |")

        elif tag == "blockquote":
            text = child.get_text(strip=True)
            lines.append(f"\n> {text}\n")

        elif tag in ("div", "section", "article"):
            lines.append(html_to_markdown(child))

        else:
            text = child.get_text(strip=True)
            if text:
                lines.append(text)

    return "\n".join(lines)


def chunk_markdown(markdown: str, source: str, title: str = "") -> list[dict]:
    """按标题层级切分 Markdown 为 chunks"""
    chunks = []
    current_chunk = []
    current_heading = title
    heading_chain = [title] if title else []

    for line in markdown.split("\n"):
        # 检测标题
        heading_match = re.match(r"^(#{1,6})\s+(.+)", line)
        if heading_match:
            # 保存当前 chunk
            if current_chunk:
                text = "\n".join(current_chunk).strip()
                if len(text) > 50:  # 过短的跳过
                    chunks.append({
                        "text": text,
                        "source": source,
                        "heading": current_heading,
                        "heading_chain": " > ".join(heading_chain),
                        "token_count": estimate_tokens(text),
                    })

            level = len(heading_match.group(1))
            current_heading = heading_match.group(2).strip()

            # 更新标题链
            if level <= len(heading_chain):
                heading_chain = heading_chain[:level - 1] + [current_heading]
            else:
                heading_chain.append(current_heading)

            current_chunk = [line]
        else:
            current_chunk.append(line)

    # 最后一个 chunk
    if current_chunk:
        text = "\n".join(current_chunk).strip()
        if len(text) > 50:
            chunks.append({
                "text": text,
                "source": source,
                "heading": current_heading,
                "heading_chain": " > ".join(heading_chain),
                "token_count": estimate_tokens(text),
            })

    # 合并过短的 chunks，拆分过长的 chunks
    merged = []
    for chunk in chunks:
        if chunk["token_count"] < 200 and merged:
            # 合并到前一个
            merged[-1]["text"] += "\n\n" + chunk["text"]
            merged[-1]["token_count"] += chunk["token_count"]
        elif chunk["token_count"] > 1000:
            # 拆分
            sub_chunks = split_long_chunk(chunk)
            merged.extend(sub_chunks)
        else:
            merged.append(chunk)

    return merged


def split_long_chunk(chunk: dict, max_tokens: int = 800) -> list[dict]:
    """拆分过长的 chunk"""
    text = chunk["text"]
    parts = []
    current = []

    for line in text.split("\n"):
        current.append(line)
        if estimate_tokens("\n".join(current)) > max_tokens:
            parts.append("\n".join(current))
            current = []

    if current:
        parts.append("\n".join(current))

    result = []
    for i, part in enumerate(parts):
        result.append({
            **chunk,
            "text": part,
            "heading": f"{chunk['heading']} ({i + 1}/{len(parts)})",
        })
    return result


def estimate_tokens(text: str) -> int:
    """简单 Token 估算"""
    return len(text) * 2


async def main():
    parser = argparse.ArgumentParser(description="华为文档爬虫")
    parser.add_argument("--ingest", action="store_true", help="爬取后直接入库")
    parser.add_argument("--max-pages", type=int, default=len(SEED_URLS), help="最大爬取页面数")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    urls = SEED_URLS[: args.max_pages]
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for url in urls:
            print(f"爬取: {url}")
            result = await crawl_page(url, page)
            results.append(result)

            if result.get("error"):
                print(f"  失败: {result['error']}")
            else:
                print(f"  成功: {len(result['content'])} 字符")

        await browser.close()

    # 保存原始结果
    output_file = OUTPUT_DIR / "crawled_docs.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n原始文档已保存到 {output_file}")

    # 分块处理
    all_chunks = []
    for doc in results:
        if doc.get("error") or not doc.get("markdown"):
            continue
        chunks = chunk_markdown(doc["markdown"], doc["url"], doc["title"])
        all_chunks.extend(chunks)

    # 保存 chunks
    chunks_file = CHUNKS_DIR / "chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"分块完成: {len(all_chunks)} 个 chunks，保存到 {chunks_file}")

    # 统计
    total_tokens = sum(c["token_count"] for c in all_chunks)
    print(f"总 Token 数: {total_tokens}")
    print(f"平均 chunk 大小: {total_tokens // len(all_chunks) if all_chunks else 0} tokens")

    # 入库
    if args.ingest:
        print("\n开始入库...")
        try:
            from scripts.ingest_chunks import ingest_all
            await ingest_all(str(chunks_file))
            print("入库完成！")
        except ImportError:
            print("入库脚本不存在，请手动运行: python scripts/ingest_chunks.py")


if __name__ == "__main__":
    asyncio.run(main())
