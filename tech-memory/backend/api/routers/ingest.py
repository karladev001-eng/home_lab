"""Ingest endpoints — URL収集・検索収集・メモ収集."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import (
    ApiResponse,
    IngestMemoRequest,
    IngestSearchRequest,
    IngestSearchResponseData,
    IngestUrlRequest,
    IngestUrlResponseData,
)
from db.session import get_db
from logic.collector.url_collector import collect_url
from logic.collector.search_collector import collect_search
from logic.collector.memo_collector import collect_memo

router = APIRouter()


@router.post("/url", response_model=ApiResponse[IngestUrlResponseData])
async def ingest_url(
    request: IngestUrlRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[IngestUrlResponseData]:
    """URLから技術カードを生成・保存する."""
    try:
        result = await collect_url(
            db=db,
            url=request.url,
            collection_mode=request.collection_mode,
            tags=request.tags,
        )
        return ApiResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail="Collection timed out") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {e}") from e


@router.post("/search", response_model=ApiResponse[IngestSearchResponseData])
async def ingest_search(
    request: IngestSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[IngestSearchResponseData]:
    """キーワードで外部収集する."""
    try:
        result = await collect_search(
            db=db,
            query=request.query,
            sources=request.sources,
            max_results=request.max_results,
            deep_analysis_limit=request.deep_analysis_limit,
        )
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search collection failed: {e}") from e


@router.post("/memo", response_model=ApiResponse[IngestUrlResponseData])
async def ingest_memo(
    request: IngestMemoRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[IngestUrlResponseData]:
    """手入力メモから技術カードを生成・保存する."""
    try:
        result = await collect_memo(
            db=db,
            memo=request.memo,
            tags=request.tags,
        )
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memo ingest failed: {e}") from e
