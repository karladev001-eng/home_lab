/**
 * Type-safe API client for tech-memory backend.
 * Uses native fetch with typed responses.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1`
  : "/api/v1";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new ApiError(res.status, data.detail || data.error || "Request failed");
  }

  return data as T;
}

// --- Types (mirrors backend schemas) ---

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

export interface PaginatedResponse<T> extends ApiResponse<T> {
  meta: { page: number; total: number } | null;
}

// Ingest
export interface IngestUrlRequest {
  url: string;
  collection_mode?: "light" | "standard" | "deep";
  tags?: string[];
}

export interface IngestUrlResponseData {
  source_id: string;
  detected_technologies: string[];
  created_items: string[];
  updated_items: string[];
  summary: string;
}

export interface IngestSearchRequest {
  query: string;
  sources?: string[];
  max_results?: number;
  deep_analysis_limit?: number;
}

export interface IngestMemoRequest {
  memo: string;
  tags?: string[];
}

// Search
export interface SearchFilters {
  domains?: string[];
  max_implementation_cost?: "low" | "medium" | "high" | null;
  maturity_level?: string | null;
  item_types?: string[];
}

export interface SearchRequest {
  query: string;
  filters?: SearchFilters;
  mode?: "keyword" | "problem_search" | "domain" | "condition";
  limit?: number;
  offset?: number;
}

export interface TechnologySearchResult {
  technology_id: string;
  name: string;
  fit_score: number;
  summary: string | null;
  why_relevant: string;
  benefits: string[];
  drawbacks: string[];
  alternatives: string[];
  domains: string[];
  item_type: string;
  maturity_level: string | null;
}

export interface SearchResponseData {
  results: TechnologySearchResult[];
  total: number;
  query: string;
}

// Technologies
export interface TechnologyListItem {
  id: string;
  name: string;
  item_type: string;
  summary: string | null;
  domains: string[];
  maturity_level: string | null;
  difficulty_level: string | null;
  created_at: string;
  updated_at: string;
}

export interface TechnologyListResponseData {
  items: TechnologyListItem[];
  total: number;
}

export interface TechnologyDetail {
  id: string;
  name: string;
  item_type: string;
  aliases: string[];
  summary: string | null;
  core_mechanism: string | null;
  abstract_principle: string | null;
  domains: string[];
  categories: string[];
  problem_structures: string[];
  purposes: Array<{ id: string; purpose: string; condition: string | null; abstraction_level: string | null }>;
  benefits: Array<{ id: string; benefit: string; condition: string | null; confidence_score: number | null }>;
  drawbacks: Array<{ id: string; drawback: string; condition: string | null; severity: string | null; confidence_score: number | null }>;
  tradeoffs: Array<{ id: string; gain: string; cost: string; condition: string | null }>;
  works_when: string[];
  fails_when: string[];
  avoid_when: string[];
  relations: Array<{ id: string; relation_type: string; technology_id: string; name: string; strength: number | null }>;
  sources: Array<{ source_id: string; title: string; url: string | null; source_type: string }>;
  maturity_level: string | null;
  difficulty_level: string | null;
  cost_level: string | null;
  known_applications: string[];
  transfer_questions: string[];
  created_at: string;
  updated_at: string;
}

// Compare
export interface CompareRequest {
  technologies: string[];
  criteria?: string[];
}

export interface CompareResponseData {
  comparison_table: Array<{
    name: string;
    technology_id: string | null;
    scores: Record<string, number>;
    summary: string;
  }>;
  criteria: string[];
  recommendation: string | null;
}

// Recommend
export interface RecommendRequest {
  problem_description: string;
  constraints?: string[];
  domains?: string[];
  limit?: number;
}

export interface RecommendResponseData {
  recommendations: Array<{
    technology_id: string;
    name: string;
    fit_score: number;
    reasoning: string;
    implementation_suggestion: string | null;
  }>;
  problem_summary: string;
}

// Health
export interface HealthData {
  status: "ok" | "degraded" | "down";
  db: "ok" | "error";
  version: string;
}

// --- API functions ---

export const api = {
  health: () =>
    fetchApi<ApiResponse<HealthData>>("/health"),

  ingest: {
    url: (req: IngestUrlRequest) =>
      fetchApi<ApiResponse<IngestUrlResponseData>>("/ingest/url", {
        method: "POST",
        body: JSON.stringify(req),
      }),
    search: (req: IngestSearchRequest) =>
      fetchApi<ApiResponse<{ collected_count: number; created_items: string[]; updated_items: string[] }>>("/ingest/search", {
        method: "POST",
        body: JSON.stringify(req),
      }),
    memo: (req: IngestMemoRequest) =>
      fetchApi<ApiResponse<IngestUrlResponseData>>("/ingest/memo", {
        method: "POST",
        body: JSON.stringify(req),
      }),
  },

  search: {
    technologies: (req: SearchRequest) =>
      fetchApi<PaginatedResponse<SearchResponseData>>("/search/technologies", {
        method: "POST",
        body: JSON.stringify(req),
      }),
  },

  technologies: {
    list: (params?: { limit?: number; offset?: number; domain?: string; item_type?: string }) => {
      const query = new URLSearchParams(
        Object.entries(params || {})
          .filter(([, v]) => v !== undefined)
          .map(([k, v]) => [k, String(v)]),
      ).toString();
      return fetchApi<PaginatedResponse<TechnologyListResponseData>>(
        `/technologies${query ? `?${query}` : ""}`,
      );
    },
    get: (id: string) =>
      fetchApi<ApiResponse<TechnologyDetail>>(`/technologies/${id}`),
  },

  compare: (req: CompareRequest) =>
    fetchApi<ApiResponse<CompareResponseData>>("/compare", {
      method: "POST",
      body: JSON.stringify(req),
    }),

  recommend: (req: RecommendRequest) =>
    fetchApi<ApiResponse<RecommendResponseData>>("/recommend", {
      method: "POST",
      body: JSON.stringify(req),
    }),
};
