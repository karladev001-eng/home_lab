"""キーワード検索による外部収集ロジック."""

from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import IngestSearchResponseData
from logic.collector.url_collector import collect_url


async def collect_search(
    db: AsyncSession,
    query: str,
    sources: list[str],
    max_results: int = 20,
    deep_analysis_limit: int = 3,
) -> IngestSearchResponseData:
    """キーワードで外部を検索し、上位結果から技術カードを収集する."""
    urls = await _search_urls(query, sources, max_results)

    created_items: list[str] = []
    updated_items: list[str] = []

    for i, url in enumerate(urls):
        mode = "deep" if i < deep_analysis_limit else "light"
        try:
            result = await collect_url(db=db, url=url, collection_mode=mode)
            created_items.extend(result.created_items)
            updated_items.extend(result.updated_items)
        except Exception:
            # Skip failed URLs
            continue

    return IngestSearchResponseData(
        collected_count=len(urls),
        created_items=created_items,
        updated_items=updated_items,
    )


async def _search_urls(query: str, sources: list[str], max_results: int) -> list[str]:
    """検索クエリからURLリストを生成する（MVP: GitHub検索のみ）."""
    urls: list[str] = []

    if "github" in sources:
        urls.extend(await _search_github(query, min(max_results, 5)))

    if "arxiv" in sources:
        urls.extend(await _search_arxiv(query, min(max_results, 5)))

    return urls[:max_results]


async def _search_github(query: str, limit: int) -> list[str]:
    """GitHub APIで検索する."""
    import httpx

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "per_page": limit},
            headers={"Accept": "application/vnd.github.v3+json"},
        )

    if resp.status_code != 200:
        return []

    data = resp.json()
    return [item["html_url"] for item in data.get("items", [])]


async def _search_arxiv(query: str, limit: int) -> list[str]:
    """arXiv APIで検索する."""
    import arxiv

    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=limit)
    results = list(client.results(search))
    return [r.entry_id for r in results]
