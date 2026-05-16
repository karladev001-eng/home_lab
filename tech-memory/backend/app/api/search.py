from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import SearchRequest, SearchResponse, SearchResult
from app.services.search import search_technologies
import uuid

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/technologies", response_model=SearchResponse)
async def search(req: SearchRequest, db: AsyncSession = Depends(get_db)):
    results = await search_technologies(
        query=req.query,
        mode=req.mode,
        domains=req.domains,
        limit=req.limit,
        db=db,
    )

    return SearchResponse(
        query=req.query,
        mode=req.mode,
        results=[
            SearchResult(
                technology_id=uuid.UUID(r["id"]),
                name=r["name"],
                item_type=r["item_type"],
                summary=r.get("summary"),
                domains=r.get("domains", []),
                fit_score=r.get("fit_score", 0.5),
                why_relevant=r.get("why_relevant"),
                benefits=r.get("benefits", []),
                drawbacks=r.get("drawbacks", []),
                alternatives=r.get("alternatives", []),
            )
            for r in results
        ],
    )
