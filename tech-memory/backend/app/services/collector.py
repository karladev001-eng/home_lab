"""Fetch content from URLs: web articles, arXiv, GitHub."""
import re
import httpx
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class FetchedContent:
    url: str
    canonical_url: str
    title: str
    text: str
    source_type: str
    author: str | None = None
    organization: str | None = None
    published_at: str | None = None
    metadata: dict | None = None


async def fetch_url(url: str) -> FetchedContent:
    url = url.strip()

    if _is_arxiv(url):
        return await _fetch_arxiv(url)
    if _is_github(url):
        return await _fetch_github(url)
    return await _fetch_web(url)


def _is_arxiv(url: str) -> bool:
    return "arxiv.org" in url


def _is_github(url: str) -> bool:
    return "github.com" in url


async def _fetch_arxiv(url: str) -> FetchedContent:
    arxiv_id = _extract_arxiv_id(url)
    if not arxiv_id:
        return await _fetch_web(url)

    api_url = f"https://export.arxiv.org/abs/{arxiv_id}"
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(api_url)
        resp.raise_for_status()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    title = soup.find("h1", class_="title")
    title_text = title.get_text(strip=True).replace("Title:", "").strip() if title else arxiv_id

    abstract = soup.find("blockquote", class_="abstract")
    abstract_text = abstract.get_text(strip=True).replace("Abstract:", "").strip() if abstract else ""

    authors_tag = soup.find("div", class_="authors")
    authors = authors_tag.get_text(strip=True).replace("Authors:", "").strip() if authors_tag else None

    return FetchedContent(
        url=url,
        canonical_url=f"https://arxiv.org/abs/{arxiv_id}",
        title=title_text,
        text=f"{title_text}\n\n{abstract_text}",
        source_type="paper",
        author=authors,
        organization="arXiv",
        metadata={"arxiv_id": arxiv_id},
    )


def _extract_arxiv_id(url: str) -> str | None:
    patterns = [
        r"arxiv\.org/abs/(\d+\.\d+)",
        r"arxiv\.org/pdf/(\d+\.\d+)",
        r"arxiv:(\d+\.\d+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


async def _fetch_github(url: str) -> FetchedContent:
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        return await _fetch_web(url)

    owner, repo = parts[0], parts[1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    headers = {"Accept": "application/vnd.github.v3+json"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        repo_resp = await client.get(api_url, headers=headers)
        readme_resp = await client.get(readme_url, headers=headers)

    repo_data = repo_resp.json() if repo_resp.status_code == 200 else {}
    readme_data = readme_resp.json() if readme_resp.status_code == 200 else {}

    title = repo_data.get("full_name", f"{owner}/{repo}")
    description = repo_data.get("description", "")

    # Decode README
    readme_text = ""
    if "content" in readme_data:
        import base64
        try:
            readme_text = base64.b64decode(readme_data["content"]).decode("utf-8")[:4000]
        except Exception:
            pass

    text = f"{title}\n\n{description}\n\n{readme_text}"

    return FetchedContent(
        url=url,
        canonical_url=f"https://github.com/{owner}/{repo}",
        title=title,
        text=text,
        source_type="github_repository",
        organization=owner,
        metadata={
            "stars": repo_data.get("stargazers_count"),
            "language": repo_data.get("language"),
            "topics": repo_data.get("topics", []),
        },
    )


async def _fetch_web(url: str) -> FetchedContent:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TechMemoryBot/1.0; research purpose)"
    }
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    # Try to find main content
    main = (
        soup.find("article")
        or soup.find("main")
        or soup.find(id="content")
        or soup.find(class_="content")
        or soup.find("body")
    )
    text = main.get_text(separator="\n", strip=True)[:6000] if main else ""

    # Detect source type
    source_type = _detect_source_type(url, soup)

    return FetchedContent(
        url=url,
        canonical_url=url,
        title=title,
        text=text,
        source_type=source_type,
    )


def _detect_source_type(url: str, soup) -> str:
    if any(x in url for x in ["zenn.dev", "qiita.com", "dev.to", "medium.com"]):
        return "blog"
    if any(x in url for x in ["docs.", "/docs/", "documentation"]):
        return "documentation"
    if "github.com" in url:
        return "github_repository"
    return "web_article"
