"""Technologies CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.schemas import (
    ApiResponse,
    ApiResponsePaginated,
    BenefitSchema,
    DrawbackSchema,
    PurposeSchema,
    RelationSchema,
    SourceRefSchema,
    TechnologiesListResponseData,
    TechnologyDetailSchema,
    TechnologyListItem,
    TradeoffSchema,
)
from db.models.technology import TechnologyCondition, TechnologyItem, TechnologyRelation
from db.models.sources import Source
from db.session import get_db

router = APIRouter()


@router.get("", response_model=ApiResponsePaginated[TechnologiesListResponseData])
async def list_technologies(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    domain: str | None = Query(default=None),
    item_type: str | None = Query(default=None),
    maturity_level: str | None = Query(default=None),
    difficulty_level: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> ApiResponsePaginated[TechnologiesListResponseData]:
    """技術一覧を取得する（ページング対応）."""
    stmt = select(TechnologyItem)

    if domain:
        stmt = stmt.where(TechnologyItem.domains.any(domain))
    if item_type:
        stmt = stmt.where(TechnologyItem.item_type == item_type)
    if maturity_level:
        stmt = stmt.where(TechnologyItem.maturity_level == maturity_level)
    if difficulty_level:
        stmt = stmt.where(TechnologyItem.difficulty_level == difficulty_level)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = stmt.order_by(TechnologyItem.updated_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return ApiResponsePaginated(
        success=True,
        data=TechnologiesListResponseData(
            items=[
                TechnologyListItem(
                    id=str(item.id),
                    name=item.name,
                    item_type=item.item_type,
                    summary=item.summary,
                    domains=item.domains or [],
                    maturity_level=item.maturity_level,
                    difficulty_level=item.difficulty_level,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in items
            ],
            total=total,
        ),
        meta={"page": offset // limit + 1, "total": total},
    )


@router.get("/{technology_id}", response_model=ApiResponse[TechnologyDetailSchema])
async def get_technology(
    technology_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TechnologyDetailSchema]:
    """技術カードの詳細を取得する."""
    stmt = (
        select(TechnologyItem)
        .where(TechnologyItem.id == technology_id)
        .options(
            selectinload(TechnologyItem.purposes),
            selectinload(TechnologyItem.benefits),
            selectinload(TechnologyItem.drawbacks),
            selectinload(TechnologyItem.tradeoffs),
            selectinload(TechnologyItem.conditions),
            selectinload(TechnologyItem.relations_as_subject).selectinload(
                TechnologyRelation.object_technology
            ),
            selectinload(TechnologyItem.evidence_list).selectinload(
                # type: ignore[attr-defined]
                type(None)  # placeholder
            ),
        )
    )

    result = await db.execute(stmt)
    tech = result.scalar_one_or_none()

    if tech is None:
        raise HTTPException(status_code=404, detail="Technology not found")

    # Extract conditions by type
    works_when = [
        c.description for c in tech.conditions if c.condition_type == "works_when"
    ]
    fails_when = [
        c.description for c in tech.conditions if c.condition_type == "fails_when"
    ]
    avoid_when = [
        c.description for c in tech.conditions if c.condition_type == "avoid_when"
    ]

    # Build relations with name
    relations = [
        RelationSchema(
            id=str(r.id),
            relation_type=r.relation_type,
            technology_id=str(r.object_technology_id),
            name=r.object_technology.name if r.object_technology else "",
            strength=float(r.strength) if r.strength else None,
        )
        for r in tech.relations_as_subject
    ]

    # Build source refs via evidence
    seen_source_ids: set[str] = set()
    sources: list[SourceRefSchema] = []
    for ev in tech.evidence_list:
        sid = str(ev.source_id)
        if sid not in seen_source_ids and ev.source:
            seen_source_ids.add(sid)
            sources.append(
                SourceRefSchema(
                    source_id=sid,
                    title=ev.source.title,
                    url=ev.source.url,
                    source_type=ev.source.source_type,
                )
            )

    return ApiResponse(
        success=True,
        data=TechnologyDetailSchema(
            id=str(tech.id),
            name=tech.name,
            item_type=tech.item_type,
            aliases=tech.aliases or [],
            summary=tech.summary,
            core_mechanism=tech.core_mechanism,
            abstract_principle=tech.abstract_principle,
            domains=tech.domains or [],
            categories=tech.categories or [],
            problem_structures=tech.problem_structures or [],
            purposes=[
                PurposeSchema(
                    id=str(p.id),
                    purpose=p.purpose,
                    condition=p.condition,
                    abstraction_level=p.abstraction_level,
                )
                for p in tech.purposes
            ],
            benefits=[
                BenefitSchema(
                    id=str(b.id),
                    benefit=b.benefit,
                    condition=b.condition,
                    confidence_score=float(b.confidence_score) if b.confidence_score else None,
                )
                for b in tech.benefits
            ],
            drawbacks=[
                DrawbackSchema(
                    id=str(d.id),
                    drawback=d.drawback,
                    condition=d.condition,
                    severity=d.severity,
                    confidence_score=float(d.confidence_score) if d.confidence_score else None,
                )
                for d in tech.drawbacks
            ],
            tradeoffs=[
                TradeoffSchema(
                    id=str(t.id),
                    gain=t.gain,
                    cost=t.cost,
                    condition=t.condition,
                )
                for t in tech.tradeoffs
            ],
            works_when=works_when,
            fails_when=fails_when,
            avoid_when=avoid_when,
            relations=relations,
            sources=sources,
            maturity_level=tech.maturity_level,
            difficulty_level=tech.difficulty_level,
            cost_level=tech.cost_level,
            known_applications=tech.known_applications or [],
            transfer_questions=tech.transfer_questions or [],
            created_at=tech.created_at,
            updated_at=tech.updated_at,
        ),
    )
