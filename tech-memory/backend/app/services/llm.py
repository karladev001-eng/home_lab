"""LLM abstraction: Claude or OpenAI, selected via LLM_PROVIDER env var."""
import json
from typing import Any
from app.config import settings


EXTRACTION_SYSTEM_PROMPT = """You are a technical knowledge extraction expert.
Extract technology information from the provided text and return structured JSON.

Rules:
- Focus on the technology itself, not the document
- abstract_principle must be domain-agnostic (applicable across fields)
- benefits and drawbacks must include conditions
- If information is not found in the text, use reasonable inferences but mark confidence lower
- Support both English and Japanese input
- Always respond in English for field values (except when values are proper nouns)
"""

EXTRACTION_USER_TEMPLATE = """Extract all technologies, algorithms, architectures, design patterns, and tools mentioned in the following text.
For each technology found, return a complete technology card in JSON format matching this schema:

{{
  "technologies": [
    {{
      "name": "Technology Name",
      "item_type": "technique|algorithm|architecture|design_pattern|tool|library|framework|protocol|evaluation_method",
      "aliases": [],
      "summary": "one sentence description",
      "core_mechanism": "how it works at its core",
      "abstract_principle": "domain-agnostic reusable principle",
      "domains": ["domain1", "domain2"],
      "problem_structures": ["what kind of problem it solves"],
      "inputs": [],
      "outputs": [],
      "purpose": [{{"description": "...", "condition": "..."}}],
      "benefits": [{{"benefit": "...", "condition": "...", "confidence": 0.8}}],
      "drawbacks": [{{"drawback": "...", "condition": "...", "severity": "low|medium|high", "evidence_type": "observed|inferred|unknown"}}],
      "tradeoffs": [{{"gain": "...", "cost": "...", "condition": "..."}}],
      "works_when": [],
      "fails_when": [],
      "avoid_when": [],
      "alternatives": ["TechA", "TechB"],
      "complements": ["TechC"],
      "known_applications": ["app1", "app2"],
      "maturity_level": "experimental|emerging|established|mature|legacy",
      "difficulty_level": "low|medium|high",
      "cost_level": "low|medium|high"
    }}
  ]
}}

Text to analyze:
{text}

Source URL: {url}
"""

SEARCH_SYSTEM_PROMPT = """You are a technical knowledge search assistant.
Given a user query and a list of technologies from the database, rank them by relevance and explain why each is relevant.
Consider the abstract principles and problem structures, not just surface-level keyword matching.
Respond in the same language as the query.
"""


async def extract_technologies(text: str, url: str) -> list[dict]:
    prompt = EXTRACTION_USER_TEMPLATE.format(text=text[:8000], url=url)

    if settings.llm_provider == "claude":
        return await _extract_with_claude(prompt)
    else:
        return await _extract_with_openai(prompt)


async def _extract_with_claude(prompt: str) -> list[dict]:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    message = await client.messages.create(
        model=settings.claude_model,
        max_tokens=8192,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text
    return _parse_technologies_json(content)


async def _extract_with_openai(prompt: str) -> list[dict]:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return _parse_technologies_json(content)


def _parse_technologies_json(content: str) -> list[dict]:
    try:
        # Extract JSON from possible markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)
        return data.get("technologies", [])
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


async def get_embedding(text: str) -> list[float]:
    if settings.embedding_provider == "claude":
        return await _embed_with_openai(text)  # Claude doesn't have embedding API yet
    return await _embed_with_openai(text)


async def _embed_with_openai(text: str) -> list[float]:
    if not settings.openai_api_key:
        # Return zero vector if no embedding provider is configured
        return [0.0] * settings.embedding_dim

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text[:8000],
    )
    return response.data[0].embedding


async def rerank_with_llm(query: str, candidates: list[dict]) -> list[dict]:
    """Use LLM to add relevance explanation and rerank results."""
    if not candidates:
        return candidates

    candidate_text = "\n".join([
        f"{i+1}. {c['name']}: {c.get('summary', '')} | abstract_principle: {c.get('abstract_principle', '')}"
        for i, c in enumerate(candidates[:20])
    ])

    prompt = f"""Query: {query}

Candidate technologies:
{candidate_text}

For each candidate, provide:
1. fit_score (0.0-1.0): how well it matches the query
2. why_relevant: one sentence explanation in the query's language

Return JSON:
{{"rankings": [{{"rank": 1, "name": "...", "fit_score": 0.95, "why_relevant": "..."}}]}}
"""

    try:
        if settings.llm_provider == "claude":
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            message = await client.messages.create(
                model=settings.claude_model,
                max_tokens=2048,
                system=SEARCH_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            content = message.content[0].text
        else:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        rankings = json.loads(content).get("rankings", [])
        score_map = {r["name"]: r for r in rankings}

        for c in candidates:
            ranking = score_map.get(c["name"], {})
            c["fit_score"] = ranking.get("fit_score", c.get("fit_score", 0.5))
            c["why_relevant"] = ranking.get("why_relevant")

        candidates.sort(key=lambda x: x.get("fit_score", 0), reverse=True)
    except Exception:
        pass

    return candidates
