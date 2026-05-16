// Auto-generated from data_model.json
// Entities for tech-memory system

export type SourceType =
  | "paper"
  | "web_article"
  | "documentation"
  | "github_repository"
  | "blog"
  | "memo"
  | "specification";

export type AccessStatus = "ok" | "failed" | "paywalled" | "not_found";

export interface Source {
  id: string; // uuid
  source_type: SourceType;
  title: string;
  url: string | null;
  canonical_url: string | null;
  author: string | null;
  organization: string | null;
  published_at: string | null; // ISO 8601
  retrieved_at: string; // ISO 8601
  source_reliability: number | null; // 0.0-1.0
  license: string | null;
  content_hash: string | null;
  access_status: AccessStatus | null;
  metadata_json: Record<string, unknown> | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export type ItemType =
  | "technique"
  | "algorithm"
  | "architecture"
  | "architecture_pattern"
  | "design_pattern"
  | "implementation_pattern"
  | "tool"
  | "library"
  | "framework"
  | "protocol"
  | "evaluation_method"
  | "method_family";

export type MaturityLevel = "experimental" | "emerging" | "mature" | "legacy";
export type DifficultyLevel = "low" | "medium" | "high";
export type CostLevel = "low" | "medium" | "high";

export interface TechnologyItem {
  id: string; // uuid
  item_type: ItemType;
  name: string;
  name_normalized: string;
  aliases: string[];
  summary: string | null;
  core_mechanism: string | null;
  abstract_principle: string | null;
  domains: string[];
  categories: string[];
  problem_structures: string[];
  inputs: string[];
  outputs: string[];
  constraints: string[];
  maturity_level: MaturityLevel | null;
  difficulty_level: DifficultyLevel | null;
  cost_level: CostLevel | null;
  known_applications: string[];
  evaluation_metrics: string[];
  transfer_questions: string[];
  // embedding is not included in API responses (server-side only)
  last_seen_at: string | null;
  created_at: string;
  updated_at: string;
}

export type AbstractionLevel = "concrete" | "abstract" | "principle";

export interface TechnologyPurpose {
  id: string;
  technology_id: string;
  purpose: string;
  condition: string | null;
  abstraction_level: AbstractionLevel | null;
  created_at: string;
}

export interface TechnologyBenefit {
  id: string;
  technology_id: string;
  benefit: string;
  condition: string | null;
  evidence_source_id: string | null;
  confidence_score: number | null; // 0.0-1.0
  created_at: string;
}

export type SeverityLevel = "low" | "medium" | "high";
export type EvidenceType = "observed" | "inferred" | "unknown";

export interface TechnologyDrawback {
  id: string;
  technology_id: string;
  drawback: string;
  condition: string | null;
  severity: SeverityLevel | null;
  evidence_type: EvidenceType | null;
  evidence_source_id: string | null;
  confidence_score: number | null;
  created_at: string;
}

export interface TechnologyTradeoff {
  id: string;
  technology_id: string;
  gain: string;
  cost: string;
  condition: string | null;
  created_at: string;
}

export type ConditionType = "works_when" | "fails_when" | "avoid_when" | "requires";

export interface TechnologyCondition {
  id: string;
  technology_id: string;
  condition_type: ConditionType;
  description: string;
  evidence_source_id: string | null;
  confidence_score: number | null;
  created_at: string;
}

export type RelationType =
  | "similar_to"
  | "alternative_to"
  | "combines_with"
  | "depends_on"
  | "implements"
  | "used_in"
  | "transfers_to"
  | "solves_same_problem_as"
  | "more_general_than"
  | "more_specific_than"
  | "improves"
  | "replaces";

export interface TechnologyRelation {
  id: string;
  subject_technology_id: string;
  relation_type: RelationType;
  object_technology_id: string;
  strength: number | null; // 0.0-1.0
  reason: string | null;
  evidence_source_id: string | null;
  created_at: string;
}

export interface UseCase {
  id: string;
  title: string;
  domain: string | null;
  problem_description: string | null;
  requirements: string[];
  constraints: string[];
  evaluation_metrics: string[];
  created_at: string;
  updated_at: string;
}

export interface UseCaseTechnology {
  id: string;
  use_case_id: string;
  technology_id: string;
  fit_score: number | null; // 0.000-1.000
  reason: string | null;
  implementation_note: string | null;
  evidence_source_id: string | null;
  created_at: string;
}

export interface Evidence {
  id: string;
  source_id: string;
  technology_id: string | null;
  evidence_type: EvidenceType | null;
  short_quote: string | null;
  paraphrase: string | null;
  locator: string | null;
  confidence_score: number | null;
  created_at: string;
}
