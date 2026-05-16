// Shared constants for tech-memory system

export const COLLECTION_MODES = ["light", "standard", "deep"] as const;
export type CollectionModeConst = (typeof COLLECTION_MODES)[number];

export const SEARCH_MODES = [
  "keyword",
  "problem_search",
  "domain",
  "condition",
] as const;
export type SearchModeConst = (typeof SEARCH_MODES)[number];

export const ITEM_TYPES = [
  "technique",
  "algorithm",
  "architecture",
  "architecture_pattern",
  "design_pattern",
  "implementation_pattern",
  "tool",
  "library",
  "framework",
  "protocol",
  "evaluation_method",
  "method_family",
] as const;
export type ItemTypeConst = (typeof ITEM_TYPES)[number];

export const SOURCE_TYPES = [
  "paper",
  "web_article",
  "documentation",
  "github_repository",
  "blog",
  "memo",
  "specification",
] as const;
export type SourceTypeConst = (typeof SOURCE_TYPES)[number];

export const MATURITY_LEVELS = [
  "experimental",
  "emerging",
  "mature",
  "legacy",
] as const;
export type MaturityLevelConst = (typeof MATURITY_LEVELS)[number];

export const DIFFICULTY_LEVELS = ["low", "medium", "high"] as const;
export type DifficultyLevelConst = (typeof DIFFICULTY_LEVELS)[number];

export const RELATION_TYPES = [
  "similar_to",
  "alternative_to",
  "combines_with",
  "depends_on",
  "implements",
  "used_in",
  "transfers_to",
  "solves_same_problem_as",
  "more_general_than",
  "more_specific_than",
  "improves",
  "replaces",
] as const;
export type RelationTypeConst = (typeof RELATION_TYPES)[number];

export const CONDITION_TYPES = [
  "works_when",
  "fails_when",
  "avoid_when",
  "requires",
] as const;
export type ConditionTypeConst = (typeof CONDITION_TYPES)[number];

export const SEARCH_SOURCES = ["web", "github", "arxiv"] as const;
export type SearchSourceConst = (typeof SEARCH_SOURCES)[number];

// API limits
export const API_LIMITS = {
  MAX_TAGS_PER_REQUEST: 20,
  MAX_TAG_LENGTH: 50,
  MAX_URL_LENGTH: 1000,
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  DEFAULT_INGEST_SEARCH_MAX_RESULTS: 20,
  DEFAULT_INGEST_SEARCH_DEEP_LIMIT: 3,
  DEFAULT_COMPARE_CRITERIA: [
    "debuggability",
    "scalability",
    "implementation_cost",
    "maturity",
  ],
  INGEST_TIMEOUT_SECONDS: 60,
} as const;

// API base URL (used in frontend)
export const API_BASE_PATH = "/api/v1" as const;

export const API_PATHS = {
  INGEST_URL: `${API_BASE_PATH}/ingest/url`,
  INGEST_SEARCH: `${API_BASE_PATH}/ingest/search`,
  INGEST_MEMO: `${API_BASE_PATH}/ingest/memo`,
  SEARCH_TECHNOLOGIES: `${API_BASE_PATH}/search/technologies`,
  TECHNOLOGIES: `${API_BASE_PATH}/technologies`,
  TECHNOLOGY_DETAIL: (id: string) => `${API_BASE_PATH}/technologies/${id}`,
  COMPARE: `${API_BASE_PATH}/compare`,
  RECOMMEND: `${API_BASE_PATH}/recommend`,
  HEALTH: `${API_BASE_PATH}/health`,
} as const;
