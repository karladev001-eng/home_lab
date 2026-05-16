"""Extract, normalize, deduplicate, and store technology cards."""
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models import (
    Source, TechnologyItem, TechnologyPurpose, TechnologyBenefit,
    TechnologyDrawback, TechnologyTradeoff, TechnologyCondition,
    TechnologyRelation, TechnologySource,
)
from app.services.llm import extract_technologies, get_embedding
from app.services.collector import FetchedContent


async def ingest_content(content: FetchedContent, db: AsyncSession, tags: list[str] = []) -> dict:
    """Full ingestion pipeline: store source → extract → normalize → store tech cards."""

    # Store source
    source = await _upsert_source(content, db)

    # Extract technology cards via LLM
    raw_cards = await extract_technologies(content.text, content.url)

    created = []
    updated = []

    for card in raw_cards:
        tech, is_new = await _upsert_technology(card, source.id, db)
        if is_new:
            created.append(tech)
        else:
            updated.append(tech)

    await db.commit()

    return {
        "source": source,
        "created": created,
        "updated": updated,
        "detected_names": [c.get("name", "") for c in raw_cards],
    }


async def _upsert_source(content: FetchedContent, db: AsyncSession) -> Source:
    content_hash = hashlib.md5(content.text.encode()).hexdigest()

    # Check if source already exists by URL
    result = await db.execute(select(Source).where(Source.url == content.url))
    existing = result.scalar_one_or_none()

    if existing:
        existing.content_hash = content_hash
        existing.title = content.title
        return existing

    source = Source(
        source_type=content.source_type,
        title=content.title,
        url=content.url,
        canonical_url=content.canonical_url,
        author=content.author,
        organization=content.organization,
        content_hash=content_hash,
        metadata_json=content.metadata or {},
    )
    db.add(source)
    await db.flush()
    return source


async def _upsert_technology(card: dict, source_id, db: AsyncSession) -> tuple[TechnologyItem, bool]:
    name = card.get("name", "").strip()
    if not name:
        return None, False

    # Normalize name for lookup
    normalized = name.lower().strip()
    aliases = [a.lower() for a in card.get("aliases", [])]

    # Check for existing tech by name or alias
    result = await db.execute(
        select(TechnologyItem).where(
            func.lower(TechnologyItem.name) == normalized
        )
    )
    existing = result.scalar_one_or_none()

    is_new = existing is None

    if existing:
        tech = existing
        # Merge new information
        _merge_tech(tech, card)
    else:
        tech = TechnologyItem(
            item_type=card.get("item_type", "technique"),
            name=name,
            aliases=card.get("aliases", []),
            summary=card.get("summary"),
            core_mechanism=card.get("core_mechanism"),
            abstract_principle=card.get("abstract_principle"),
            domains=card.get("domains", []),
            problem_structures=card.get("problem_structures", []),
            inputs=card.get("inputs", []),
            outputs=card.get("outputs", []),
            maturity_level=card.get("maturity_level"),
            difficulty_level=card.get("difficulty_level"),
            cost_level=card.get("cost_level"),
        )
        db.add(tech)
        await db.flush()

        # Generate embedding for semantic search
        embed_text = f"{name} {card.get('summary', '')} {card.get('abstract_principle', '')}"
        embedding = await get_embedding(embed_text)
        if any(v != 0.0 for v in embedding):
            tech.embedding = embedding

        # Store child records
        await _store_children(tech.id, card, source_id, db)

    # Link source
    await _link_source(tech.id, source_id, db)

    return tech, is_new


def _merge_tech(tech: TechnologyItem, card: dict):
    # Merge domains and aliases without duplicating
    existing_domains = set(tech.domains or [])
    new_domains = set(card.get("domains", []))
    tech.domains = list(existing_domains | new_domains)

    existing_aliases = set(tech.aliases or [])
    new_aliases = set(card.get("aliases", []))
    tech.aliases = list(existing_aliases | new_aliases)

    # Update fields only if currently empty
    if not tech.summary and card.get("summary"):
        tech.summary = card["summary"]
    if not tech.abstract_principle and card.get("abstract_principle"):
        tech.abstract_principle = card["abstract_principle"]
    if not tech.core_mechanism and card.get("core_mechanism"):
        tech.core_mechanism = card["core_mechanism"]


async def _store_children(tech_id, card: dict, source_id, db: AsyncSession):
    for p in card.get("purpose", []):
        db.add(TechnologyPurpose(
            technology_id=tech_id,
            purpose=p.get("description", ""),
            condition=p.get("condition"),
        ))

    for b in card.get("benefits", []):
        db.add(TechnologyBenefit(
            technology_id=tech_id,
            benefit=b.get("benefit", ""),
            condition=b.get("condition"),
            confidence_score=b.get("confidence", 0.5),
            evidence_source_id=source_id,
        ))

    for d in card.get("drawbacks", []):
        db.add(TechnologyDrawback(
            technology_id=tech_id,
            drawback=d.get("drawback", ""),
            condition=d.get("condition"),
            severity=d.get("severity", "medium"),
            evidence_type=d.get("evidence_type", "inferred"),
            evidence_source_id=source_id,
        ))

    for t in card.get("tradeoffs", []):
        db.add(TechnologyTradeoff(
            technology_id=tech_id,
            gain=t.get("gain", ""),
            cost=t.get("cost", ""),
            condition=t.get("condition"),
        ))

    for ctype, items in [
        ("works_when", card.get("works_when", [])),
        ("fails_when", card.get("fails_when", [])),
        ("avoid_when", card.get("avoid_when", [])),
    ]:
        for desc in items:
            db.add(TechnologyCondition(
                technology_id=tech_id,
                condition_type=ctype,
                description=desc,
                evidence_source_id=source_id,
            ))


async def _link_source(tech_id, source_id, db: AsyncSession):
    result = await db.execute(
        select(TechnologySource).where(
            TechnologySource.technology_id == tech_id,
            TechnologySource.source_id == source_id,
        )
    )
    if not result.scalar_one_or_none():
        db.add(TechnologySource(technology_id=tech_id, source_id=source_id))
