"""URL収集ロジック — arXiv / GitHub / 一般Webページのコンテンツ取得."""

import hashlib
import re
from datetime import UTC, datetime

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import IngestUrlResponseData
from db.models.sources import Source
from db.models.technology import TechnologyItem
from logic.extractor.llm_extractor import extract_technologies
from logic.embedder.openai_embedder import generate_embedding
from logic.normalizer.deduplicator import upsert_technology

TIMEOUT_SECONDS = 60


async def collect_url(
    db: AsyncSession,
    url: str,
    collection_mode: str = "standard",
    tags: list[str] | None = None,
) -> IngestUrlResponseData:
    """URLからコンテンツを取得し技術カードを生成・保存する."""
    tags = tags or []

    # Check for duplicate source by URL
    canonical = _normalize_url(url)
    existing_source = await db.execute(
        select(Source).where(Source.canonical_url == canonical)
    )
    source = existing_source.scalar_one_or_none()

    # Fetch content
    content_text, title, source_type = await _fetch_content(url, collection_mode)
    content_hash = hashlib.md5(content_text.encode()).hexdigest()

    if source is None:
        source = Source(
            source_type=source_type,
            title=title,
            url=url,
            canonical_url=canonical,
            retrieved_at=datetime.now(UTC),
            content_hash=content_hash,
            access_status="ok",
            tags=tags,
        )
        db.add(source)
    else:
        source.content_hash = content_hash
        source.retrieved_at = datetime.now(UTC)
        source.tags = list(set(source.tags + tags))

    await db.flush()

    # Extract technologies via LLM
    tech_cards = await extract_technologies(content_text, title, url, collection_mode)

    created_items: list[str] = []
    updated_items: list[str] = []
    detected_names: list[str] = []

    for card in tech_cards:
        detected_names.append(card["name"])
        tech, was_created = await upsert_technology(db, card, str(source.id))
        if was_created:
            created_items.append(str(tech.id))
        else:
            updated_items.append(str(tech.id))

    return IngestUrlResponseData(
        source_id=str(source.id),
        detected_technologies=detected_names,
        created_items=created_items,
        updated_items=updated_items,
        summary=f"{source_type}: {title}",
    )


async def _fetch_content(url: str, mode: str) -> tuple[str, str, str]:
    """URLからテキストを取得し (content, title, source_type) を返す."""
    if "arxiv.org" in url:
        return await _fetch_arxiv(url)
    if "github.com" in url:
        return await _fetch_github(url)
    return await _fetch_web(url)


async def _fetch_arxiv(url: str) -> tuple[str, str, str]:
    """arXiv論文を取得する."""
    import arxiv

    # Extract arxiv ID from URL
    arxiv_id = re.search(r"arxiv\.org/abs/([^\s/]+)", url)
    if not arxiv_id:
        return await _fetch_web(url)

    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id.group(1)])
    results = list(client.results(search))

    if not results:
        return await _fetch_web(url)

    paper = results[0]
    content = f"Title: {paper.title}\n\nAbstract: {paper.summary}"
    return content, paper.title, "paper"


async def _fetch_github(url: str) -> tuple[str, str, str]:
    """GitHub READMEを取得する."""
    # Convert github.com/owner/repo to API endpoint
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url)
    if not match:
        return await _fetch_web(url)

    owner, repo = match.group(1), match.group(2)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.get(api_url, headers={"Accept": "application/vnd.github.raw"})

    if resp.status_code != 200:
        return await _fetch_web(url)

    content = resp.text
    title = f"{owner}/{repo}"
    return content, title, "github_repository"


async def _fetch_web(url: str) -> tuple[str, str, str]:
    """一般WebページのHTMLを取得してテキスト抽出する."""
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
        resp = await client.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (tech-memory-bot)"},
        )
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    # Extract main text
    main = soup.find("main") or soup.find("article") or soup.body
    text = main.get_text(separator="\n", strip=True) if main else soup.get_text()

    # Truncate to ~8000 chars to stay within LLM context
    return text[:8000], title, "web_article"


def _normalize_url(url: str) -> str:
    """URLを正規化して重複判定に使用する."""
    url = url.rstrip("/")
    url = re.sub(r"#.*$", "", url)
    url = re.sub(r"\?utm_[^&]*(&|$)", "", url)
    return url
