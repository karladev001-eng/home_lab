"""Hybrid search: keyword + vector + metadata filter."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, or_
from app.models import TechnologyItem, TechnologyBenefit, TechnologyDrawback, TechnologyRelation
from app.services.llm import get_embedding, rerank_with_llm


async def search_technologies(
    query: str,
    mode: str,
    domains: list[str],
    limit: int,
    db: AsyncSession,
) -> list[dict]:

    if mode == "keyword":
        candidates = await _keyword_search(query, domains, limit * 2, db)
    elif mode in ("problem", "transfer"):
        candidates = await _semantic_search(query, domains, limit * 2, db)
    elif mode == "domain":
        candidates = await _domain_search(query, limit * 2, db)
    else:
        candidates = await _keyword_search(query, domains, limit * 2, db)

    # Enrich with benefit/drawback info
    for c in candidates:
        c["benefits"], c["drawbacks"], c["alternatives"] = await _get_quick_info(c["id"], db)

    # LLM reranking for semantic modes
    if mode in ("problem", "transfer") and candidates:
        candidates = await rerank_with_llm(query, candidates)

    return candidates[:limit]


async def _keyword_search(query: str, domains: list[str], limit: int, db: AsyncSession) -> list[dict]:
    stmt = (
        select(
            TechnologyItem,
            func.ts_rank(
                func.to_tsvector("english", func.coalesce(TechnologyItem.name, "") + " " + func.coalesce(TechnologyItem.summary, "")),
                func.plainto_tsquery("english", query),
            ).label("rank"),
        )
        .where(
            or_(
                func.lower(TechnologyItem.name).contains(query.lower()),
                func.to_tsvector("english", func.coalesce(TechnologyItem.name, "") + " " + func.coalesce(TechnologyItem.summary, "")).op("@@")(
                    func.plainto_tsquery("english", query)
                ),
            )
        )
        .order_by(text("rank DESC"))
        .limit(limit)
    )

    if domains:
        stmt = stmt.where(TechnologyItem.domains.overlap(domains))

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": str(row.TechnologyItem.id),
            "name": row.TechnologyItem.name,
            "item_type": row.TechnologyItem.item_type,
            "summary": row.TechnologyItem.summary,
            "abstract_principle": row.TechnologyItem.abstract_principle,
            "domains": row.TechnologyItem.domains or [],
            "fit_score": float(row.rank) if row.rank else 0.5,
        }
        for row in rows
    ]


async def _semantic_search(query: str, domains: list[str], limit: int, db: AsyncSession) -> list[dict]:
    embedding = await get_embedding(query)

    # If no embedding (zero vector), fall back to keyword search
    if not any(v != 0.0 for v in embedding):
        return await _keyword_search(query, domains, limit, db)

    embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"

    stmt = text("""
        SELECT id, name, item_type, summary, abstract_principle, domains,
               1 - (embedding <=> :embedding::vector) AS similarity
        FROM technology_items
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> :embedding::vector
        LIMIT :limit
    """)

    result = await db.execute(stmt, {"embedding": embedding_str, "limit": limit})
    rows = result.mappings().all()

    return [
        {
            "id": str(row["id"]),
            "name": row["name"],
            "item_type": row["item_type"],
            "summary": row["summary"],
            "abstract_principle": row["abstract_principle"],
            "domains": row["domains"] or [],
            "fit_score": float(row["similarity"]) if row["similarity"] else 0.5,
        }
        for row in rows
    ]


async def _domain_search(domain: str, limit: int, db: AsyncSession) -> list[dict]:
    stmt = (
        select(TechnologyItem)
        .where(TechnologyItem.domains.any(func.lower(text("value")) == domain.lower()))
        .limit(limit)
    )

    # Use contains-like search for domain
    stmt = select(TechnologyItem).where(
        func.array_to_string(TechnologyItem.domains, ",").ilike(f"%{domain}%")
    ).limit(limit)

    result = await db.execute(stmt)
    techs = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "name": t.name,
            "item_type": t.item_type,
            "summary": t.summary,
            "abstract_principle": t.abstract_principle,
            "domains": t.domains or [],
            "fit_score": 0.7,
        }
        for t in techs
    ]


async def _get_quick_info(tech_id: str, db: AsyncSession) -> tuple[list[str], list[str], list[str]]:
    benefits_result = await db.execute(
        select(TechnologyBenefit.benefit).where(TechnologyBenefit.technology_id == tech_id).limit(3)
    )
    benefits = [r[0] for r in benefits_result]

    drawbacks_result = await db.execute(
        select(TechnologyDrawback.drawback).where(TechnologyDrawback.technology_id == tech_id).limit(3)
    )
    drawbacks = [r[0] for r in drawbacks_result]

    alternatives_result = await db.execute(
        select(TechnologyItem.name)
        .join(TechnologyRelation, TechnologyRelation.object_technology_id == TechnologyItem.id)
        .where(
            TechnologyRelation.subject_technology_id == tech_id,
            TechnologyRelation.relation_type == "alternative_to",
        )
        .limit(3)
    )
    alternatives = [r[0] for r in alternatives_result]

    return benefits, drawbacks, alternatives
