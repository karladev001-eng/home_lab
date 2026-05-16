"""Technology models — 技術・アルゴリズム・設計パターン等."""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


class TechnologyItem(Base):
    __tablename__ = "technology_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    item_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="technique|algorithm|architecture|architecture_pattern|design_pattern|implementation_pattern|tool|library|framework|protocol|evaluation_method|method_family",
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_normalized: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_mechanism: Mapped[str | None] = mapped_column(Text, nullable=True)
    abstract_principle: Mapped[str | None] = mapped_column(Text, nullable=True)
    domains: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    categories: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    problem_structures: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    inputs: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    outputs: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    constraints: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    maturity_level: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="experimental|emerging|mature|legacy"
    )
    difficulty_level: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="low|medium|high"
    )
    cost_level: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="low|medium|high"
    )
    known_applications: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    evaluation_metrics: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    transfer_questions: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    # Vector embedding (text-embedding-3-small = 1536 dims)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    # Full-text search vector
    tsv: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    purposes = relationship(
        "TechnologyPurpose", back_populates="technology", cascade="all, delete-orphan"
    )
    benefits = relationship(
        "TechnologyBenefit", back_populates="technology", cascade="all, delete-orphan"
    )
    drawbacks = relationship(
        "TechnologyDrawback", back_populates="technology", cascade="all, delete-orphan"
    )
    tradeoffs = relationship(
        "TechnologyTradeoff", back_populates="technology", cascade="all, delete-orphan"
    )
    conditions = relationship(
        "TechnologyCondition", back_populates="technology", cascade="all, delete-orphan"
    )
    relations_as_subject = relationship(
        "TechnologyRelation",
        foreign_keys="TechnologyRelation.subject_technology_id",
        back_populates="subject_technology",
        cascade="all, delete-orphan",
    )
    relations_as_object = relationship(
        "TechnologyRelation",
        foreign_keys="TechnologyRelation.object_technology_id",
        back_populates="object_technology",
    )
    evidence_list = relationship("Evidence", back_populates="technology")
    use_case_links = relationship("UseCaseTechnology", back_populates="technology")


class TechnologyPurpose(Base):
    __tablename__ = "technology_purposes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technology_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    abstraction_level: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="concrete|abstract|principle"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    technology = relationship("TechnologyItem", back_populates="purposes")


class TechnologyBenefit(Base):
    __tablename__ = "technology_benefits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technology_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    benefit: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence_score: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    technology = relationship("TechnologyItem", back_populates="benefits")


class TechnologyDrawback(Base):
    __tablename__ = "technology_drawbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technology_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    drawback: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="low|medium|high"
    )
    evidence_type: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="observed|inferred|unknown"
    )
    evidence_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence_score: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    technology = relationship("TechnologyItem", back_populates="drawbacks")


class TechnologyTradeoff(Base):
    __tablename__ = "technology_tradeoffs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technology_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    gain: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    technology = relationship("TechnologyItem", back_populates="tradeoffs")


class TechnologyCondition(Base):
    __tablename__ = "technology_conditions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technology_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    condition_type: Mapped[str] = mapped_column(
        Text, nullable=False, comment="works_when|fails_when|avoid_when|requires"
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence_score: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    technology = relationship("TechnologyItem", back_populates="conditions")


class TechnologyRelation(Base):
    __tablename__ = "technology_relations"
    __table_args__ = (
        UniqueConstraint(
            "subject_technology_id",
            "relation_type",
            "object_technology_id",
            name="uq_tech_relation_pair",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subject_technology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technology_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    relation_type: Mapped[str] = mapped_column(Text, nullable=False)
    object_technology_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technology_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    strength: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    subject_technology = relationship(
        "TechnologyItem",
        foreign_keys=[subject_technology_id],
        back_populates="relations_as_subject",
    )
    object_technology = relationship(
        "TechnologyItem",
        foreign_keys=[object_technology_id],
        back_populates="relations_as_object",
    )
