"""Recommend endpoint — 課題・制約からの技術推薦."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import ApiResponse, RecommendRequest, RecommendResponseData
from db.session import get_db
from logic.searcher.recommend_service import recommend_technologies

router = APIRouter()


@router.post("/recommend", response_model=ApiResponse[RecommendResponseData])
async def recommend(
    request: RecommendRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecommendResponseData]:
    """課題と制約から最適な技術を推薦する."""
    try:
        result = await recommend_technologies(
            db=db,
            problem_description=request.problem_description,
            constraints=request.constraints or [],
            domains=request.domains or [],
            limit=request.limit,
        )
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommend failed: {e}") from e
