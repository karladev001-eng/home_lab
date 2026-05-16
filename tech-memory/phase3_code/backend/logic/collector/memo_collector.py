"""メモ入力からの技術カード生成ロジック."""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import IngestUrlResponseData
from db.models.sources import Source
from logic.extractor.llm_extractor import extract_technologies
from logic.normalizer.deduplicator import upsert_technology


async def collect_memo(
    db: AsyncSession,
    memo: str,
    tags: list[str] | None = None,
) -> IngestUrlResponseData:
    """手入力メモから技術カードを生成・保存する."""
    tags = tags or []

    source = Source(
        source_type="memo",
        title=f"Memo: {memo[:50]}...",
        url=None,
        canonical_url=None,
        retrieved_at=datetime.now(UTC),
        access_status="ok",
        tags=tags,
    )
    db.add(source)
    await db.flush()

    tech_cards = await extract_technologies(memo, "User Memo", None, "standard")

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
        summary=f"memo: {memo[:80]}",
    )
