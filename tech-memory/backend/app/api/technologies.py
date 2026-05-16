from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models import (
    TechnologyItem, TechnologyPurpose, TechnologyBenefit, TechnologyDrawback,
    TechnologyTradeoff, TechnologyCondition, TechnologyRelation, TechnologySource, Source
)
from app.schemas import TechnologyItemOut, TechnologyDetailOut

router = APIRouter(prefix="/api/technologies", tags=["technologies"])


@router.get("", response_model=list[TechnologyItemOut])
async def list_technologies(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TechnologyItem).order_by(TechnologyItem.created_at.desc()).limit(limit).offset(offset)
    )
    techs = result.scalars().all()
    return [
        TechnologyItemOut(
            id=t.id, name=t.name, item_type=t.item_type, summary=t.summary,
            domains=t.domains or [], aliases=t.aliases or [],
            maturity_level=t.maturity_level, difficulty_level=t.difficulty_level,
            created_at=t.created_at,
        )
        for t in techs
    ]


@router.get("/{tech_id}", response_model=TechnologyDetailOut)
async def get_technology(tech_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TechnologyItem).where(TechnologyItem.id == tech_id))
    tech = result.scalar_one_or_none()
    if not tech:
        raise HTTPException(status_code=404, detail="Technology not found")

    purposes = (await db.execute(select(TechnologyPurpose).where(TechnologyPurpose.technology_id == tech_id))).scalars().all()
    benefits = (await db.execute(select(TechnologyBenefit).where(TechnologyBenefit.technology_id == tech_id))).scalars().all()
    drawbacks = (await db.execute(select(TechnologyDrawback).where(TechnologyDrawback.technology_id == tech_id))).scalars().all()
    tradeoffs = (await db.execute(select(TechnologyTradeoff).where(TechnologyTradeoff.technology_id == tech_id))).scalars().all()
    conditions = (await db.execute(select(TechnologyCondition).where(TechnologyCondition.technology_id == tech_id))).scalars().all()

    relations_result = await db.execute(
        select(TechnologyRelation, TechnologyItem)
        .join(TechnologyItem, TechnologyRelation.object_technology_id == TechnologyItem.id)
        .where(TechnologyRelation.subject_technology_id == tech_id)
    )
    relations = [
        {"relation_type": r.TechnologyRelation.relation_type, "name": r.TechnologyItem.name, "reason": r.TechnologyRelation.reason}
        for r in relations_result
    ]

    sources_result = await db.execute(
        select(Source)
        .join(TechnologySource, TechnologySource.source_id == Source.id)
        .where(TechnologySource.technology_id == tech_id)
    )
    sources = [{"title": s.title, "url": s.url, "source_type": s.source_type} for s in sources_result.scalars()]

    return TechnologyDetailOut(
        id=tech.id, name=tech.name, item_type=tech.item_type, summary=tech.summary,
        domains=tech.domains or [], aliases=tech.aliases or [],
        maturity_level=tech.maturity_level, difficulty_level=tech.difficulty_level,
        created_at=tech.created_at,
        core_mechanism=tech.core_mechanism, abstract_principle=tech.abstract_principle,
        problem_structures=tech.problem_structures or [],
        inputs=tech.inputs or [], outputs=tech.outputs or [],
        purposes=[{"purpose": p.purpose, "condition": p.condition} for p in purposes],
        benefits=[{"benefit": b.benefit, "condition": b.condition, "confidence": float(b.confidence_score or 0.5)} for b in benefits],
        drawbacks=[{"drawback": d.drawback, "condition": d.condition, "severity": d.severity} for d in drawbacks],
        tradeoffs=[{"gain": t.gain, "cost": t.cost, "condition": t.condition} for t in tradeoffs],
        conditions=[{"type": c.condition_type, "description": c.description} for c in conditions],
        relations=relations,
        sources=sources,
    )
