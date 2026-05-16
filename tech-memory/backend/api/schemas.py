"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None


class ApiResponsePaginated(ApiResponse[T], Generic[T]):
    meta: dict[str, Any] | None = None


# --- Ingest URL ---

class IngestUrlRequest(BaseModel):
    url: str = Field(..., max_length=1000)
    collection_mode: str = Field(default="standard")
    tags: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("collection_mode")
    @classmethod
    def validate_collection_mode(cls, v: str) -> str:
        if v not in ("light", "standard", "deep"):
            raise ValueError("collection_mode must be light, standard, or deep")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if len(tag) > 50:
                raise ValueError("Each tag must be 50 characters or less")
        return v


class IngestUrlResponseData(BaseModel):
    source_id: str
    detected_technologies: list[str]
    created_items: list[str]
    updated_items: list[str]
    summary: str


# --- Ingest Search ---

class IngestSearchRequest(BaseModel):
    query: str
    sources: list[str] = Field(default_factory=lambda: ["web"])
    max_results: int = Field(default=20, ge=1, le=100)
    deep_analysis_limit: int = Field(default=3, ge=0, le=10)


class IngestSearchResponseData(BaseModel):
    collected_count: int
    created_items: list[str]
    updated_items: list[str]


# --- Ingest Memo ---

class IngestMemoRequest(BaseModel):
    memo: str = Field(..., min_length=10)
    tags: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if len(tag) > 50:
                raise ValueError("Each tag must be 50 characters or less")
        return v


# --- Search Technologies ---

class SearchFilters(BaseModel):
    domains: list[str] | None = None
    max_implementation_cost: str | None = None
    maturity_level: str | None = None
    item_types: list[str] | None = None


class SearchTechnologiesRequest(BaseModel):
    query: str = Field(..., min_length=1)
    filters: SearchFilters | None = None
    mode: str = Field(default="keyword")
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in ("keyword", "problem_search", "domain", "condition"):
            raise ValueError("Invalid search mode")
        return v


class TechnologySearchResult(BaseModel):
    technology_id: str
    name: str
    fit_score: float
    summary: str | None
    why_relevant: str
    benefits: list[str]
    drawbacks: list[str]
    alternatives: list[str]
    domains: list[str]
    item_type: str
    maturity_level: str | None


class SearchTechnologiesResponseData(BaseModel):
    results: list[TechnologySearchResult]
    total: int
    query: str


# --- Technologies List ---

class TechnologyListItem(BaseModel):
    id: str
    name: str
    item_type: str
    summary: str | None
    domains: list[str]
    maturity_level: str | None
    difficulty_level: str | None
    created_at: datetime
    updated_at: datetime


class TechnologiesListResponseData(BaseModel):
    items: list[TechnologyListItem]
    total: int


# --- Technology Detail ---

class PurposeSchema(BaseModel):
    id: str
    purpose: str
    condition: str | None
    abstraction_level: str | None


class BenefitSchema(BaseModel):
    id: str
    benefit: str
    condition: str | None
    confidence_score: float | None


class DrawbackSchema(BaseModel):
    id: str
    drawback: str
    condition: str | None
    severity: str | None
    confidence_score: float | None


class TradeoffSchema(BaseModel):
    id: str
    gain: str
    cost: str
    condition: str | None


class RelationSchema(BaseModel):
    id: str
    relation_type: str
    technology_id: str
    name: str
    strength: float | None


class SourceRefSchema(BaseModel):
    source_id: str
    title: str
    url: str | None
    source_type: str


class TechnologyDetailSchema(BaseModel):
    id: str
    name: str
    item_type: str
    aliases: list[str]
    summary: str | None
    core_mechanism: str | None
    abstract_principle: str | None
    domains: list[str]
    categories: list[str]
    problem_structures: list[str]
    purposes: list[PurposeSchema]
    benefits: list[BenefitSchema]
    drawbacks: list[DrawbackSchema]
    tradeoffs: list[TradeoffSchema]
    works_when: list[str]
    fails_when: list[str]
    avoid_when: list[str]
    relations: list[RelationSchema]
    sources: list[SourceRefSchema]
    maturity_level: str | None
    difficulty_level: str | None
    cost_level: str | None
    known_applications: list[str]
    transfer_questions: list[str]
    created_at: datetime
    updated_at: datetime


# --- Compare ---

class CompareRequest(BaseModel):
    technologies: list[str] = Field(..., min_length=2, max_length=10)
    criteria: list[str] | None = None


class TechnologyComparisonScore(BaseModel):
    name: str
    technology_id: str | None
    scores: dict[str, float]
    summary: str


class CompareResponseData(BaseModel):
    comparison_table: list[TechnologyComparisonScore]
    criteria: list[str]
    recommendation: str | None


# --- Recommend ---

class RecommendRequest(BaseModel):
    problem_description: str = Field(..., min_length=10)
    constraints: list[str] | None = None
    domains: list[str] | None = None
    limit: int = Field(default=5, ge=1, le=20)


class RecommendationItem(BaseModel):
    technology_id: str
    name: str
    fit_score: float
    reasoning: str
    implementation_suggestion: str | None


class RecommendResponseData(BaseModel):
    recommendations: list[RecommendationItem]
    problem_summary: str


# --- Health ---

class HealthResponseData(BaseModel):
    status: str
    db: str
    version: str
