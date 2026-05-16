from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime


class PurposeItem(BaseModel):
    description: str
    condition: Optional[str] = None


class BenefitItem(BaseModel):
    benefit: str
    condition: Optional[str] = None
    confidence: float = 0.5


class DrawbackItem(BaseModel):
    drawback: str
    condition: Optional[str] = None
    severity: Literal["low", "medium", "high"] = "medium"
    evidence_type: Literal["observed", "inferred", "unknown"] = "inferred"


class TradeoffItem(BaseModel):
    gain: str
    cost: str
    condition: Optional[str] = None


class RelationItem(BaseModel):
    name: str
    relation_type: str
    reason: Optional[str] = None


# LLMが返す技術カード
class TechnologyCardExtracted(BaseModel):
    name: str
    item_type: str = Field(
        default="technique",
        description="technique, algorithm, architecture, design_pattern, tool, library, framework, protocol, evaluation_method"
    )
    aliases: list[str] = []
    summary: str
    core_mechanism: str
    abstract_principle: str
    domains: list[str] = []
    problem_structures: list[str] = []
    inputs: list[str] = []
    outputs: list[str] = []
    purpose: list[PurposeItem] = []
    benefits: list[BenefitItem] = []
    drawbacks: list[DrawbackItem] = []
    tradeoffs: list[TradeoffItem] = []
    works_when: list[str] = []
    fails_when: list[str] = []
    avoid_when: list[str] = []
    alternatives: list[str] = []
    complements: list[str] = []
    known_applications: list[str] = []
    maturity_level: Optional[str] = None
    difficulty_level: Optional[str] = None
    cost_level: Optional[str] = None


# API レスポンス
class TechnologyItemOut(BaseModel):
    id: UUID
    name: str
    item_type: str
    summary: Optional[str]
    domains: list[str]
    aliases: list[str]
    maturity_level: Optional[str]
    difficulty_level: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TechnologyDetailOut(TechnologyItemOut):
    core_mechanism: Optional[str]
    abstract_principle: Optional[str]
    problem_structures: list[str]
    inputs: list[str]
    outputs: list[str]
    purposes: list[dict] = []
    benefits: list[dict] = []
    drawbacks: list[dict] = []
    tradeoffs: list[dict] = []
    conditions: list[dict] = []
    relations: list[dict] = []
    sources: list[dict] = []


# 検索
class SearchRequest(BaseModel):
    query: str
    mode: Literal["keyword", "problem", "domain", "transfer"] = "keyword"
    domains: list[str] = []
    limit: int = Field(default=10, le=50)


class SearchResult(BaseModel):
    technology_id: UUID
    name: str
    item_type: str
    summary: Optional[str]
    domains: list[str]
    fit_score: float
    why_relevant: Optional[str] = None
    benefits: list[str] = []
    drawbacks: list[str] = []
    alternatives: list[str] = []


class SearchResponse(BaseModel):
    query: str
    mode: str
    results: list[SearchResult]


# 収集
class IngestUrlRequest(BaseModel):
    url: str
    collection_mode: Literal["light", "standard", "deep"] = "standard"
    tags: list[str] = []


class IngestResponse(BaseModel):
    source_id: UUID
    source_title: str
    detected_technologies: list[str]
    created_items: list[TechnologyItemOut]
    updated_items: list[TechnologyItemOut]
    message: str
