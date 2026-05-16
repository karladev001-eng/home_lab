"""技術比較サービス."""

import json

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.schemas import CompareResponseData, TechnologyComparisonScore
from db.models.technology import TechnologyItem
from logic.normalizer.deduplicator import normalize_name


async def compare_technologies(
    db: AsyncSession,
    technologies: list[str],
    criteria: list[str],
) -> CompareResponseData:
    """技術リストを評価軸で比較する."""
    # Resolve technology names to items
    tech_items: list[TechnologyItem] = []
    for name in technologies:
        normalized = normalize_name(name)
        result = await db.execute(
            select(TechnologyItem).where(TechnologyItem.name_normalized == normalized)
        )
        tech = result.scalar_one_or_none()
        if tech is None:
            # Try partial match on name
            result = await db.execute(
                select(TechnologyItem).where(
                    TechnologyItem.name.ilike(f"%{name}%")
                ).limit(1)
            )
            tech = result.scalar_one_or_none()
        if tech:
            tech_items.append(tech)

    if not tech_items:
        raise ValueError("No technologies found in database")

    # Build comparison context
    tech_summaries = "\n\n".join([
        f"## {t.name}\n{t.summary or ''}\nCore: {t.core_mechanism or ''}"
        for t in tech_items
    ])

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""以下の技術を {', '.join(criteria)} の観点で比較してください。
各技術について各評価軸のスコア(0.0-1.0)と100字以内のサマリーをJSON形式で返してください。

技術一覧:
{tech_summaries}

評価軸: {', '.join(criteria)}

出力形式（JSON）:
{{
  "comparison": [
    {{
      "name": "技術名",
      "scores": {{{', '.join([f'"{c}": 0.0' for c in criteria])}}},
      "summary": "...",
      "technology_id": "id"
    }}
  ],
  "recommendation": "...",
}}"""
        }],
    )

    # Parse response
    try:
        content = response.content[0].text
        # Extract JSON from response
        import re
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            comparisons = data.get("comparison", [])
            recommendation = data.get("recommendation")
        else:
            comparisons = []
            recommendation = None
    except Exception:
        comparisons = []
        recommendation = None

    # Map tech IDs
    tech_id_map = {normalize_name(t.name): str(t.id) for t in tech_items}

    table = [
        TechnologyComparisonScore(
            name=c.get("name", ""),
            technology_id=tech_id_map.get(normalize_name(c.get("name", "")), c.get("technology_id")),
            scores={k: float(v) for k, v in c.get("scores", {}).items()},
            summary=c.get("summary", ""),
        )
        for c in comparisons
    ]

    return CompareResponseData(
        comparison_table=table,
        criteria=criteria,
        recommendation=recommendation,
    )
