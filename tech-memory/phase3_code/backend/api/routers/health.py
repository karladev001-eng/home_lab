"""Health check endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import ApiResponse, HealthResponseData
from db.session import get_db

router = APIRouter()


@router.get("/health", response_model=ApiResponse[HealthResponseData])
async def health_check(db: AsyncSession = Depends(get_db)) -> ApiResponse[HealthResponseData]:
    """Returns API and DB health status."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    status = "ok" if db_status == "ok" else "degraded"

    return ApiResponse(
        success=True,
        data=HealthResponseData(
            status=status,
            db=db_status,
            version="0.1.0",
        ),
    )
