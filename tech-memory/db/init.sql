CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- ソース（情報源）
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    canonical_url TEXT,
    author TEXT,
    organization TEXT,
    published_at TIMESTAMP,
    retrieved_at TIMESTAMP NOT NULL DEFAULT now(),
    source_reliability NUMERIC,
    license TEXT,
    content_hash TEXT,
    access_status TEXT DEFAULT 'accessible',
    metadata_json JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_sources_url ON sources(url);
CREATE INDEX idx_sources_source_type ON sources(source_type);
CREATE INDEX idx_sources_retrieved_at ON sources(retrieved_at DESC);

-- 技術アイテム（中心エンティティ）
CREATE TABLE technology_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_type TEXT NOT NULL,
    name TEXT NOT NULL,
    aliases TEXT[] DEFAULT '{}',
    summary TEXT,
    core_mechanism TEXT,
    abstract_principle TEXT,
    domains TEXT[] DEFAULT '{}',
    categories TEXT[] DEFAULT '{}',
    problem_structures TEXT[] DEFAULT '{}',
    inputs TEXT[] DEFAULT '{}',
    outputs TEXT[] DEFAULT '{}',
    constraints TEXT[] DEFAULT '{}',
    maturity_level TEXT,
    difficulty_level TEXT,
    cost_level TEXT,
    embedding vector(1536),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_tech_name ON technology_items(name);
CREATE INDEX idx_tech_domains ON technology_items USING GIN(domains);
CREATE INDEX idx_tech_embedding ON technology_items USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100);

-- 技術の目的
CREATE TABLE technology_purposes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL,
    condition TEXT,
    abstraction_level TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_purposes_tech ON technology_purposes(technology_id);

-- 技術のメリット
CREATE TABLE technology_benefits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    benefit TEXT NOT NULL,
    condition TEXT,
    evidence_source_id UUID REFERENCES sources(id),
    confidence_score NUMERIC DEFAULT 0.5,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_benefits_tech ON technology_benefits(technology_id);

-- 技術のデメリット
CREATE TABLE technology_drawbacks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    drawback TEXT NOT NULL,
    condition TEXT,
    severity TEXT DEFAULT 'medium',
    evidence_type TEXT DEFAULT 'inferred',
    evidence_source_id UUID REFERENCES sources(id),
    confidence_score NUMERIC DEFAULT 0.5,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_drawbacks_tech ON technology_drawbacks(technology_id);

-- トレードオフ
CREATE TABLE technology_tradeoffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    gain TEXT NOT NULL,
    cost TEXT NOT NULL,
    condition TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_tradeoffs_tech ON technology_tradeoffs(technology_id);

-- 有効条件・回避条件
CREATE TABLE technology_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    condition_type TEXT NOT NULL, -- works_when, fails_when, avoid_when, requires
    description TEXT NOT NULL,
    evidence_source_id UUID REFERENCES sources(id),
    confidence_score NUMERIC DEFAULT 0.5,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_conditions_tech ON technology_conditions(technology_id);

-- 技術関係
CREATE TABLE technology_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    object_technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    strength NUMERIC DEFAULT 0.5,
    reason TEXT,
    evidence_source_id UUID REFERENCES sources(id),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_relations_subject ON technology_relations(subject_technology_id);
CREATE INDEX idx_relations_object ON technology_relations(object_technology_id);

-- ソース↔技術の紐付け
CREATE TABLE technology_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE(technology_id, source_id)
);

-- エビデンス
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    technology_id UUID REFERENCES technology_items(id) ON DELETE CASCADE,
    evidence_type TEXT DEFAULT 'inferred',
    short_quote TEXT,
    paraphrase TEXT,
    locator TEXT,
    confidence_score NUMERIC DEFAULT 0.5,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_evidence_tech ON evidence(technology_id);
CREATE INDEX idx_evidence_source ON evidence(source_id);

-- 全文検索用
CREATE INDEX idx_tech_name_fts ON technology_items USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(abstract_principle, '')));
