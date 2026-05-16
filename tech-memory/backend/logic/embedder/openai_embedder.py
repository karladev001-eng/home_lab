"""OpenAI Embedding APIを使ったベクトル生成."""

from openai import AsyncOpenAI

from api.config import settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


async def generate_embedding(text: str) -> list[float]:
    """テキストをvector(1536)に変換する."""
    client = _get_client()
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def build_embedding_text(tech: dict) -> str:
    """技術カードのembedding用テキストを構築する."""
    parts = []
    if tech.get("name"):
        parts.append(tech["name"])
    if tech.get("summary"):
        parts.append(tech["summary"])
    if tech.get("core_mechanism"):
        parts.append(tech["core_mechanism"])
    if tech.get("abstract_principle"):
        parts.append(tech["abstract_principle"])
    return " ".join(parts)
