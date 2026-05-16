// API request/response types for tech-memory
// Mirrors FastAPI Pydantic schemas

import type {
  ItemType,
  MaturityLevel,
  DifficultyLevel,
  RelationType,
  Source,
  TechnologyBenefit,
  TechnologyCondition,
  TechnologyDrawback,
  TechnologyPurpose,
  TechnologyRelation,
  TechnologyTradeoff,
} from "./entities.js";

// --- Common ---

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

export interface PaginationMeta {
  page: number;
  total: number;
}

export interface ApiResponsePaginated<T> extends ApiResponse<T> {
  meta: PaginationMeta;
}

// --- POST /api/v1/ingest/url ---

export type CollectionMode = "light" | "standard" | "deep";

export interface IngestUrlRequest {
  url: string; // http/https, max 1000 chars
  collection_mode?: CollectionMode; // default: "standard"
  tags?: string[]; // max 20 items, each max 50 chars
}

export interface IngestUrlResponseData {
  source_id: string;
  detected_technologies: string[];
  created_items: string[];
  updated_items: string[];
  summary: string;
}

export type IngestUrlResponse = ApiResponse<IngestUrlResponseData>;

// --- POST /api/v1/ingest/search ---

export type SearchSource = "web" | "github" | "arxiv";

export interface IngestSearchRequest {
  query: string;
  sources?: SearchSource[];
  max_results?: number;
  deep_analysis_limit?: number;
}

export interface IngestSearchResponseData {
  collected_count: number;
  created_items: string[];
  updated_items: string[];
}

export type IngestSearchResponse = ApiResponse<IngestSearchResponseData>;

// --- POST /api/v1/ingest/memo ---

export interface IngestMemoRequest {
  memo: string;
  tags?: string[];
}

export type IngestMemoResponseData = IngestUrlResponseData;
export type IngestMemoResponse = ApiResponse<IngestMemoResponseData>;

// --- POST /api/v1/search/technologies ---

export type SearchMode = "keyword" | "problem_search" | "domain" | "condition";

export interface SearchFilters {
  domains?: string[];
  max_implementation_cost?: CostLevel | null;
  maturity_level?: MaturityLevel | null;
  item_types?: ItemType[];
}

export type CostLevel = "low" | "medium" | "high";

export interface SearchTechnologiesRequest {
  query: string;
  filters?: SearchFilters;
  mode?: SearchMode; // default: "keyword"
  limit?: number; // default: 10
  offset?: number; // default: 0
}

export interface TechnologySearchResult {
  technology_id: string;
  name: string;
  fit_score: number; // 0.0-1.0
  summary: string | null;
  why_relevant: string;
  benefits: string[];
  drawbacks: string[];
  alternatives: string[];
  domains: string[];
  item_type: ItemType;
  maturity_level: MaturityLevel | null;
}

export interface SearchTechnologiesResponseData {
  results: TechnologySearchResult[];
  total: number;
  query: string;
}

export type SearchTechnologiesResponse = ApiResponsePaginated<SearchTechnologiesResponseData>;

// --- GET /api/v1/technologies ---

export interface TechnologiesListQuery {
  limit?: number;
  offset?: number;
  domain?: string;
  item_type?: ItemType;
  maturity_level?: MaturityLevel;
  difficulty_level?: DifficultyLevel;
}

export interface TechnologyListItem {
  id: string;
  name: string;
  item_type: ItemType;
  summary: string | null;
  domains: string[];
  maturity_level: MaturityLevel | null;
  difficulty_level: DifficultyLevel | null;
  created_at: string;
  updated_at: string;
}

export interface TechnologiesListResponseData {
  items: TechnologyListItem[];
  total: number;
}

export type TechnologiesListResponse = ApiResponsePaginated<TechnologiesListResponseData>;

// --- GET /api/v1/technologies/{id} ---

export interface TechnologyRelationWithName extends TechnologyRelation {
  name: string; // name of the related technology
}

export interface TechnologySourceRef {
  source_id: string;
  title: string;
  url: string | null;
  source_type: Source["source_type"];
}

export interface TechnologyDetail {
  id: string;
  name: string;
  item_type: ItemType;
  aliases: string[];
  summary: string | null;
  core_mechanism: string | null;
  abstract_principle: string | null;
  domains: string[];
  categories: string[];
  problem_structures: string[];
  purposes: TechnologyPurpose[];
  benefits: TechnologyBenefit[];
  drawbacks: TechnologyDrawback[];
  tradeoffs: TechnologyTradeoff[];
  works_when: string[];
  fails_when: string[];
  avoid_when: string[];
  relations: TechnologyRelationWithName[];
  sources: TechnologySourceRef[];
  maturity_level: MaturityLevel | null;
  difficulty_level: DifficultyLevel | null;
  cost_level: CostLevel | null;
  known_applications: string[];
  transfer_questions: string[];
  created_at: string;
  updated_at: string;
}

export type TechnologyDetailResponse = ApiResponse<TechnologyDetail>;

// --- POST /api/v1/compare ---

export interface CompareRequest {
  technologies: string[]; // names or UUIDs
  criteria?: string[];
}

export interface TechnologyComparisonScore {
  name: string;
  technology_id: string | null;
  scores: Record<string, number>;
  summary: string;
}

export interface CompareResponseData {
  comparison_table: TechnologyComparisonScore[];
  criteria: string[];
  recommendation: string | null;
}

export type CompareResponse = ApiResponse<CompareResponseData>;

// --- POST /api/v1/recommend ---

export interface RecommendRequest {
  problem_description: string;
  constraints?: string[];
  domains?: string[];
  limit?: number;
}

export interface RecommendationItem {
  technology_id: string;
  name: string;
  fit_score: number;
  reasoning: string;
  implementation_suggestion: string | null;
}

export interface RecommendResponseData {
  recommendations: RecommendationItem[];
  problem_summary: string;
}

export type RecommendResponse = ApiResponse<RecommendResponseData>;

// --- GET /api/v1/health ---

export interface HealthResponseData {
  status: "ok" | "degraded" | "down";
  db: "ok" | "error";
  version: string;
}

export type HealthResponse = ApiResponse<HealthResponseData>;
