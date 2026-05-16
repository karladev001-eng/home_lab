"""Search endpoints — 技術ハイブリッド検索."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import (
    ApiResponsePaginated,
    SearchTechnologiesRequest,
    SearchTechnologiesResponseData,
)
from db.session import get_db
from logic.searcher.hybrid_search import hybrid_search

router = APIRouter()


@router.post("/technologies", response_model=ApiResponsePaginated[SearchTechnologiesResponseData])
async def search_technologies(
    request: SearchTechnologiesRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponsePaginated[SearchTechnologiesResponseData]:
    """課題・キーワードから技術をハイブリッド検索する."""
    try:
        results, total = await hybrid_search(
            db=db,
            query=request.query,
            mode=request.mode,
            filters=request.filters,
            limit=request.limit,
            offset=request.offset,
        )
        page = request.offset // request.limit + 1
        return ApiResponsePaginated(
            success=True,
            data=SearchTechnologiesResponseData(
                results=results,
                total=total,
                query=request.query,
            ),
            meta={"page": page, "total": total},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}") from e
