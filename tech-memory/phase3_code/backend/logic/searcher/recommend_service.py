"""技術推薦サービス — 課題・制約から最適な技術を推薦."""

from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import RecommendResponseData, RecommendationItem
from logic.searcher.hybrid_search import hybrid_search


async def recommend_technologies(
    db: AsyncSession,
    problem_description: str,
    constraints: list[str],
    domains: list[str],
    limit: int = 5,
) -> RecommendResponseData:
    """課題記述からベクトル検索で技術を推薦する."""
    from api.schemas import SearchFilters

    filters = SearchFilters(domains=domains if domains else None)

    results, _ = await hybrid_search(
        db=db,
        query=problem_description,
        mode="problem_search",
        filters=filters,
        limit=limit,
        offset=0,
    )

    recommendations = [
        RecommendationItem(
            technology_id=r.technology_id,
            name=r.name,
            fit_score=r.fit_score,
            reasoning=r.why_relevant,
            implementation_suggestion=None,
        )
        for r in results
    ]

    # Summarize the problem
    problem_summary = problem_description[:200]

    return RecommendResponseData(
        recommendations=recommendations,
        problem_summary=problem_summary,
    )
