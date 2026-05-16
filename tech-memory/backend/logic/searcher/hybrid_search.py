"""ハイブリッド検索ロジック（キーワード + ベクトル検索）."""

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import SearchFilters, TechnologySearchResult
from db.models.technology import TechnologyBenefit, TechnologyDrawback, TechnologyItem
from logic.embedder.openai_embedder import generate_embedding

KEYWORD_WEIGHT = 0.3
VECTOR_WEIGHT = 0.7


async def hybrid_search(
    db: AsyncSession,
    query: str,
    mode: str = "keyword",
    filters: SearchFilters | None = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[TechnologySearchResult], int]:
    """ハイブリッド検索でtechnology_itemsを検索する."""
    if mode == "keyword":
        return await _keyword_search(db, query, filters, limit, offset)
    elif mode in ("problem_search", "condition"):
        return await _vector_search(db, query, filters, limit, offset)
    elif mode == "domain":
        return await _domain_search(db, query, filters, limit, offset)
    else:
        return await _keyword_search(db, query, filters, limit, offset)


async def _keyword_search(
    db: AsyncSession,
    query: str,
    filters: SearchFilters | None,
    limit: int,
    offset: int,
) -> tuple[list[TechnologySearchResult], int]:
    """PostgreSQL全文検索（tsvector）でハイブリッド検索."""
    # Full-text search
    ts_query = func.plainto_tsquery("english", query)
    stmt = (
        select(TechnologyItem)
        .where(TechnologyItem.tsv.op("@@")(ts_query))
    )
    stmt = _apply_filters(stmt, filters)

    count_result = await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )
    total = count_result.scalar_one()

    stmt = stmt.order_by(
        func.ts_rank(TechnologyItem.tsv, ts_query).desc()
    ).limit(limit).offset(offset)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return await _build_results(db, items, query), total


async def _vector_search(
    db: AsyncSession,
    query: str,
    filters: SearchFilters | None,
    limit: int,
    offset: int,
) -> tuple[list[TechnologySearchResult], int]:
    """pgvectorコサイン類似度検索."""
    try:
        embedding = await generate_embedding(query)
    except Exception:
        # Fall back to keyword search if embedding fails
        return await _keyword_search(db, query, filters, limit, offset)

    embedding_str = f"[{','.join(str(v) for v in embedding)}]"

    stmt = (
        select(TechnologyItem)
        .where(TechnologyItem.embedding.isnot(None))
    )
    stmt = _apply_filters(stmt, filters)

    count_result = await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )
    total = count_result.scalar_one()

    # Cosine distance ordering (pgvector operator: <=>)
    stmt = stmt.order_by(
        text(f"embedding <=> '{embedding_str}'::vector")
    ).limit(limit).offset(offset)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return await _build_results(db, items, query), total


async def _domain_search(
    db: AsyncSession,
    query: str,
    filters: SearchFilters | None,
    limit: int,
    offset: int,
) -> tuple[list[TechnologySearchResult], int]:
    """ドメインフィルタ検索."""
    stmt = select(TechnologyItem).where(TechnologyItem.domains.any(query))
    stmt = _apply_filters(stmt, filters)

    count_result = await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )
    total = count_result.scalar_one()

    stmt = stmt.order_by(TechnologyItem.updated_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return await _build_results(db, items, query), total


def _apply_filters(stmt, filters: SearchFilters | None):
    if filters is None:
        return stmt
    if filters.domains:
        for domain in filters.domains:
            stmt = stmt.where(TechnologyItem.domains.any(domain))
    if filters.maturity_level:
        stmt = stmt.where(TechnologyItem.maturity_level == filters.maturity_level)
    if filters.max_implementation_cost:
        cost_order = {"low": 1, "medium": 2, "high": 3}
        max_cost_val = cost_order.get(filters.max_implementation_cost, 3)
        allowed = [k for k, v in cost_order.items() if v <= max_cost_val]
        stmt = stmt.where(TechnologyItem.cost_level.in_(allowed))
    if filters.item_types:
        stmt = stmt.where(TechnologyItem.item_type.in_(filters.item_types))
    return stmt


async def _build_results(
    db: AsyncSession,
    items: list[TechnologyItem],
    query: str,
) -> list[TechnologySearchResult]:
    """検索結果をTechnologySearchResult形式に変換する."""
    results = []
    for item in items:
        # Load benefits and drawbacks for summary
        benefits_result = await db.execute(
            select(TechnologyBenefit).where(
                TechnologyBenefit.technology_id == item.id
            ).limit(3)
        )
        benefits = [b.benefit for b in benefits_result.scalars().all()]

        drawbacks_result = await db.execute(
            select(TechnologyDrawback).where(
                TechnologyDrawback.technology_id == item.id
            ).limit(3)
        )
        drawbacks = [d.drawback for d in drawbacks_result.scalars().all()]

        results.append(
            TechnologySearchResult(
                technology_id=str(item.id),
                name=item.name,
                fit_score=0.8,  # Placeholder; real scoring requires query embedding
                summary=item.summary,
                why_relevant=f"Matches query: {query}",
                benefits=benefits,
                drawbacks=drawbacks,
                alternatives=[],
                domains=item.domains or [],
                item_type=item.item_type,
                maturity_level=item.maturity_level,
            )
        )
    return results
