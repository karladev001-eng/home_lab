"""Initial schema with pgvector extensions.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-05-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # sources
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("source_type", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("canonical_url", sa.Text, nullable=True),
        sa.Column("author", sa.Text, nullable=True),
        sa.Column("organization", sa.Text, nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_reliability", sa.Numeric(3, 2), nullable=True),
        sa.Column("license", sa.Text, nullable=True),
        sa.Column("content_hash", sa.Text, nullable=True),
        sa.Column("access_status", sa.Text, nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_sources_canonical_url", "sources", ["canonical_url"],
                    unique=True, postgresql_where=sa.text("canonical_url IS NOT NULL"))
    op.create_index("idx_sources_source_type", "sources", ["source_type"])
    op.create_index("idx_sources_retrieved_at", "sources", [sa.text("retrieved_at DESC")])

    # technology_items
    op.create_table(
        "technology_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("item_type", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("name_normalized", sa.Text, nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("core_mechanism", sa.Text, nullable=True),
        sa.Column("abstract_principle", sa.Text, nullable=True),
        sa.Column("domains", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("categories", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("problem_structures", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("inputs", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("outputs", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("constraints", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("maturity_level", sa.Text, nullable=True),
        sa.Column("difficulty_level", sa.Text, nullable=True),
        sa.Column("cost_level", sa.Text, nullable=True),
        sa.Column("known_applications", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("evaluation_metrics", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("transfer_questions", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("embedding", sa.Text, nullable=True),  # placeholder; real type set below
        sa.Column("tsv", postgresql.TSVECTOR, nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    # Alter embedding column to real vector type
    op.execute("ALTER TABLE technology_items ALTER COLUMN embedding TYPE vector(1536) USING NULL")
    op.create_index("idx_tech_name_normalized", "technology_items", ["name_normalized"], unique=True)
    op.create_index("idx_tech_embedding", "technology_items", ["embedding"],
                    postgresql_using="ivfflat",
                    postgresql_ops={"embedding": "vector_cosine_ops"},
                    postgresql_with={"lists": 100})
    op.create_index("idx_tech_tsv", "technology_items", ["tsv"], postgresql_using="gin")
    op.create_index("idx_tech_domains", "technology_items", ["domains"], postgresql_using="gin")
    op.create_index("idx_tech_item_type", "technology_items", ["item_type"])
    op.create_index("idx_tech_maturity", "technology_items", ["maturity_level"])

    # technology_purposes
    op.create_table(
        "technology_purposes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=True),
        sa.Column("abstraction_level", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_purposes_technology_id", "technology_purposes", ["technology_id"])

    # technology_benefits
    op.create_table(
        "technology_benefits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("benefit", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=True),
        sa.Column("evidence_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_benefits_technology_id", "technology_benefits", ["technology_id"])

    # technology_drawbacks
    op.create_table(
        "technology_drawbacks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("drawback", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=True),
        sa.Column("severity", sa.Text, nullable=True),
        sa.Column("evidence_type", sa.Text, nullable=True),
        sa.Column("evidence_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_drawbacks_technology_id", "technology_drawbacks", ["technology_id"])

    # technology_tradeoffs
    op.create_table(
        "technology_tradeoffs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gain", sa.Text, nullable=False),
        sa.Column("cost", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_tradeoffs_technology_id", "technology_tradeoffs", ["technology_id"])

    # technology_conditions
    op.create_table(
        "technology_conditions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("condition_type", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("evidence_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_conditions_technology_id", "technology_conditions", ["technology_id"])
    op.create_index("idx_conditions_type", "technology_conditions", ["condition_type"])

    # technology_relations
    op.create_table(
        "technology_relations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("subject_technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation_type", sa.Text, nullable=False),
        sa.Column("object_technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("strength", sa.Numeric(3, 2), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("evidence_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("subject_technology_id", "relation_type", "object_technology_id", name="uq_tech_relation_pair"),
    )
    op.create_index("idx_relations_subject", "technology_relations", ["subject_technology_id"])
    op.create_index("idx_relations_object", "technology_relations", ["object_technology_id"])
    op.create_index("idx_relations_type", "technology_relations", ["relation_type"])

    # use_cases
    op.create_table(
        "use_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("domain", sa.Text, nullable=True),
        sa.Column("problem_description", sa.Text, nullable=True),
        sa.Column("requirements", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("constraints", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("evaluation_metrics", postgresql.ARRAY(sa.Text), nullable=False, server_default="'{}'"),
        sa.Column("embedding", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.execute("ALTER TABLE use_cases ALTER COLUMN embedding TYPE vector(1536) USING NULL")
    op.create_index("idx_use_cases_embedding", "use_cases", ["embedding"],
                    postgresql_using="ivfflat",
                    postgresql_ops={"embedding": "vector_cosine_ops"},
                    postgresql_with={"lists": 100})
    op.create_index("idx_use_cases_domain", "use_cases", ["domain"])

    # use_case_technologies
    op.create_table(
        "use_case_technologies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("use_case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("use_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fit_score", sa.Numeric(4, 3), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("implementation_note", sa.Text, nullable=True),
        sa.Column("evidence_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("use_case_id", "technology_id", name="uq_uc_tech_pair"),
    )
    op.create_index("idx_uc_tech_use_case", "use_case_technologies", ["use_case_id"])
    op.create_index("idx_uc_tech_technology", "use_case_technologies", ["technology_id"])

    # evidence
    op.create_table(
        "evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_items.id", ondelete="CASCADE"), nullable=True),
        sa.Column("evidence_type", sa.Text, nullable=True),
        sa.Column("short_quote", sa.Text, nullable=True),
        sa.Column("paraphrase", sa.Text, nullable=True),
        sa.Column("locator", sa.Text, nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_evidence_source", "evidence", ["source_id"])
    op.create_index("idx_evidence_technology", "evidence", ["technology_id"])


def downgrade() -> None:
    op.drop_table("evidence")
    op.drop_table("use_case_technologies")
    op.drop_table("use_cases")
    op.drop_table("technology_relations")
    op.drop_table("technology_conditions")
    op.drop_table("technology_tradeoffs")
    op.drop_table("technology_drawbacks")
    op.drop_table("technology_benefits")
    op.drop_table("technology_purposes")
    op.drop_table("technology_items")
    op.drop_table("sources")
