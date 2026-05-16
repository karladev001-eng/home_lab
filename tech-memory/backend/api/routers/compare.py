"""Compare endpoint — 複数技術の比較."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import ApiResponse, CompareRequest, CompareResponseData
from db.session import get_db
from logic.searcher.compare_service import compare_technologies

router = APIRouter()

DEFAULT_CRITERIA = [
    "debuggability",
    "scalability",
    "implementation_cost",
    "maturity",
]


@router.post("/compare", response_model=ApiResponse[CompareResponseData])
async def compare(
    request: CompareRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CompareResponseData]:
    """複数の技術を指定された評価軸で比較する."""
    criteria = request.criteria or DEFAULT_CRITERIA
    try:
        result = await compare_technologies(
            db=db,
            technologies=request.technologies,
            criteria=criteria,
        )
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compare failed: {e}") from e
