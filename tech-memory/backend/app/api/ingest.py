from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import IngestUrlRequest, IngestResponse, TechnologyItemOut
from app.services.collector import fetch_url
from app.services.extractor import ingest_content

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/url", response_model=IngestResponse)
async def ingest_url(req: IngestUrlRequest, db: AsyncSession = Depends(get_db)):
    try:
        content = await fetch_url(req.url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e}")

    try:
        result = await ingest_content(content, db, tags=req.tags)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    created_items = [
        TechnologyItemOut(
            id=t.id,
            name=t.name,
            item_type=t.item_type,
            summary=t.summary,
            domains=t.domains or [],
            aliases=t.aliases or [],
            maturity_level=t.maturity_level,
            difficulty_level=t.difficulty_level,
            created_at=t.created_at,
        )
        for t in result["created"] if t
    ]
    updated_items = [
        TechnologyItemOut(
            id=t.id,
            name=t.name,
            item_type=t.item_type,
            summary=t.summary,
            domains=t.domains or [],
            aliases=t.aliases or [],
            maturity_level=t.maturity_level,
            difficulty_level=t.difficulty_level,
            created_at=t.created_at,
        )
        for t in result["updated"] if t
    ]

    return IngestResponse(
        source_id=result["source"].id,
        source_title=result["source"].title,
        detected_technologies=result["detected_names"],
        created_items=created_items,
        updated_items=updated_items,
        message=f"Extracted {len(created_items)} new, {len(updated_items)} updated technologies.",
    )
