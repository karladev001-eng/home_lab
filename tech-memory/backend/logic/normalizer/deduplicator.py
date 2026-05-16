"""技術名の正規化と重複排除ロジック."""

import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.technology import (
    TechnologyBenefit,
    TechnologyCondition,
    TechnologyDrawback,
    TechnologyItem,
    TechnologyPurpose,
    TechnologyRelation,
    TechnologyTradeoff,
)
from db.models.use_cases import Evidence
from logic.embedder.openai_embedder import build_embedding_text, generate_embedding


def normalize_name(name: str) -> str:
    """技術名を正規化する（小文字・記号除去）."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9぀-鿿]", "", name)
    return name.strip()


async def upsert_technology(
    db: AsyncSession,
    card: dict,
    source_id: str,
) -> tuple[TechnologyItem, bool]:
    """技術カードをDBにupsertする. (tech, was_created) を返す."""
    name_normalized = normalize_name(card["name"])

    # Find existing by normalized name
    stmt = select(TechnologyItem).where(TechnologyItem.name_normalized == name_normalized)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    was_created = existing is None

    if existing is None:
        # Generate embedding
        embedding_text = build_embedding_text(card)
        try:
            embedding = await generate_embedding(embedding_text)
        except Exception:
            embedding = None

        tech = TechnologyItem(
            item_type=card.get("item_type", "technique"),
            name=card["name"],
            name_normalized=name_normalized,
            aliases=card.get("aliases", []),
            summary=card.get("summary"),
            core_mechanism=card.get("core_mechanism"),
            abstract_principle=card.get("abstract_principle"),
            domains=card.get("domains", []),
            categories=card.get("categories", []),
            problem_structures=card.get("problem_structures", []),
            known_applications=card.get("known_applications", []),
            maturity_level=card.get("maturity_level"),
            difficulty_level=card.get("difficulty_level"),
            cost_level=card.get("cost_level"),
            embedding=embedding,
        )
        db.add(tech)
        await db.flush()
    else:
        tech = existing
        # Merge non-empty values
        if card.get("summary") and not tech.summary:
            tech.summary = card["summary"]
        if card.get("core_mechanism") and not tech.core_mechanism:
            tech.core_mechanism = card["core_mechanism"]
        if card.get("abstract_principle") and not tech.abstract_principle:
            tech.abstract_principle = card["abstract_principle"]
        # Merge lists
        for field in ("aliases", "domains", "categories", "known_applications"):
            existing_list = getattr(tech, field) or []
            new_items = card.get(field, [])
            merged = list(set(existing_list + new_items))
            setattr(tech, field, merged)

    # Add purposes
    for purpose_data in card.get("purposes", []):
        db.add(TechnologyPurpose(
            technology_id=tech.id,
            purpose=purpose_data["purpose"],
            condition=purpose_data.get("condition"),
            abstraction_level=purpose_data.get("abstraction_level"),
        ))

    # Add benefits
    for benefit_data in card.get("benefits", []):
        db.add(TechnologyBenefit(
            technology_id=tech.id,
            benefit=benefit_data["benefit"],
            condition=benefit_data.get("condition"),
        ))

    # Add drawbacks
    for drawback_data in card.get("drawbacks", []):
        db.add(TechnologyDrawback(
            technology_id=tech.id,
            drawback=drawback_data["drawback"],
            condition=drawback_data.get("condition"),
            severity=drawback_data.get("severity"),
        ))

    # Add tradeoffs
    for tradeoff_data in card.get("tradeoffs", []):
        db.add(TechnologyTradeoff(
            technology_id=tech.id,
            gain=tradeoff_data["gain"],
            cost=tradeoff_data["cost"],
            condition=tradeoff_data.get("condition"),
        ))

    # Add conditions
    for cond_data in card.get("conditions", []):
        db.add(TechnologyCondition(
            technology_id=tech.id,
            condition_type=cond_data["condition_type"],
            description=cond_data["description"],
        ))

    # Add evidence link
    db.add(Evidence(
        source_id=uuid.UUID(source_id),
        technology_id=tech.id,
        evidence_type="inferred",
    ))

    await db.flush()
    return tech, was_created
