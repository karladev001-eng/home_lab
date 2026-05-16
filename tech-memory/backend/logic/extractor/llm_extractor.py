"""LLM (Claude API) を使った技術カード構造化抽出."""

import json

import anthropic

from api.config import settings

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


EXTRACTION_TOOL = {
    "name": "extract_technologies",
    "description": "テキストから技術・アルゴリズム・設計パターン等を抽出して構造化する",
    "input_schema": {
        "type": "object",
        "properties": {
            "technologies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "item_type": {
                            "type": "string",
                            "enum": [
                                "technique", "algorithm", "architecture",
                                "architecture_pattern", "design_pattern",
                                "implementation_pattern", "tool", "library",
                                "framework", "protocol", "evaluation_method",
                                "method_family",
                            ],
                        },
                        "aliases": {"type": "array", "items": {"type": "string"}},
                        "summary": {"type": "string"},
                        "core_mechanism": {"type": "string"},
                        "abstract_principle": {"type": "string"},
                        "domains": {"type": "array", "items": {"type": "string"}},
                        "categories": {"type": "array", "items": {"type": "string"}},
                        "problem_structures": {"type": "array", "items": {"type": "string"}},
                        "known_applications": {"type": "array", "items": {"type": "string"}},
                        "maturity_level": {
                            "type": "string",
                            "enum": ["experimental", "emerging", "mature", "legacy"],
                        },
                        "difficulty_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                        "cost_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                        "purposes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "purpose": {"type": "string"},
                                    "condition": {"type": "string"},
                                    "abstraction_level": {
                                        "type": "string",
                                        "enum": ["concrete", "abstract", "principle"],
                                    },
                                },
                                "required": ["purpose"],
                            },
                        },
                        "benefits": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "benefit": {"type": "string"},
                                    "condition": {"type": "string"},
                                },
                                "required": ["benefit"],
                            },
                        },
                        "drawbacks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "drawback": {"type": "string"},
                                    "condition": {"type": "string"},
                                    "severity": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high"],
                                    },
                                },
                                "required": ["drawback"],
                            },
                        },
                        "tradeoffs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "gain": {"type": "string"},
                                    "cost": {"type": "string"},
                                    "condition": {"type": "string"},
                                },
                                "required": ["gain", "cost"],
                            },
                        },
                        "conditions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "condition_type": {
                                        "type": "string",
                                        "enum": ["works_when", "fails_when", "avoid_when", "requires"],
                                    },
                                    "description": {"type": "string"},
                                },
                                "required": ["condition_type", "description"],
                            },
                        },
                        "relations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "relation_type": {
                                        "type": "string",
                                        "enum": [
                                            "similar_to", "alternative_to", "combines_with",
                                            "depends_on", "implements", "used_in",
                                        ],
                                    },
                                    "target_name": {"type": "string"},
                                    "reason": {"type": "string"},
                                },
                                "required": ["relation_type", "target_name"],
                            },
                        },
                    },
                    "required": ["name", "item_type", "summary"],
                },
            }
        },
        "required": ["technologies"],
    },
}

SYSTEM_PROMPT = """あなたは技術情報の構造化エキスパートです。
与えられたテキストから技術・アルゴリズム・設計パターン・ツールを抽出し、
条件付きのメリット・デメリット・トレードオフとともに構造化してください。

重要な原則:
- 技術を特定用途に閉じ込めない（抽象原理ベースで記述する）
- メリット・デメリットは「条件付き」で記述する
- 1つの記事から通常1〜3つの技術を抽出する（多すぎない）
- 確信のない情報は含めない
"""


async def extract_technologies(
    text: str,
    title: str,
    url: str | None,
    mode: str = "standard",
) -> list[dict]:
    """テキストから技術情報を抽出してdict形式で返す."""
    client = _get_client()

    model = "claude-haiku-4-5-20251001" if mode == "light" else "claude-sonnet-4-6"
    max_tokens = 2000 if mode == "light" else 4000

    prompt = f"""以下のコンテンツから技術情報を抽出してください。

Source: {title}
URL: {url or "N/A"}

Content:
{text[:6000]}
"""

    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_technologies"},
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_technologies":
            return block.input.get("technologies", [])

    return []
