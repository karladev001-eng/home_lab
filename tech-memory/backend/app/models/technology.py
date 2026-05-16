from sqlalchemy import Column, String, Text, Numeric, TIMESTAMP, ARRAY, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from app.database import Base
from app.config import settings


class TechnologyItem(Base):
    __tablename__ = "technology_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    aliases = Column(ARRAY(Text), default=[])
    summary = Column(Text)
    core_mechanism = Column(Text)
    abstract_principle = Column(Text)
    domains = Column(ARRAY(Text), default=[])
    categories = Column(ARRAY(Text), default=[])
    problem_structures = Column(ARRAY(Text), default=[])
    inputs = Column(ARRAY(Text), default=[])
    outputs = Column(ARRAY(Text), default=[])
    constraints = Column(ARRAY(Text), default=[])
    maturity_level = Column(Text)
    difficulty_level = Column(Text)
    cost_level = Column(Text)
    embedding = Column(Vector(settings.embedding_dim))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())


class TechnologyPurpose(Base):
    __tablename__ = "technology_purposes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    purpose = Column(Text, nullable=False)
    condition = Column(Text)
    abstraction_level = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class TechnologyBenefit(Base):
    __tablename__ = "technology_benefits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    benefit = Column(Text, nullable=False)
    condition = Column(Text)
    evidence_source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    confidence_score = Column(Numeric, default=0.5)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class TechnologyDrawback(Base):
    __tablename__ = "technology_drawbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    drawback = Column(Text, nullable=False)
    condition = Column(Text)
    severity = Column(Text, default="medium")
    evidence_type = Column(Text, default="inferred")
    evidence_source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    confidence_score = Column(Numeric, default=0.5)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class TechnologyTradeoff(Base):
    __tablename__ = "technology_tradeoffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    gain = Column(Text, nullable=False)
    cost = Column(Text, nullable=False)
    condition = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class TechnologyCondition(Base):
    __tablename__ = "technology_conditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    condition_type = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    evidence_source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    confidence_score = Column(Numeric, default=0.5)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class TechnologyRelation(Base):
    __tablename__ = "technology_relations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    relation_type = Column(Text, nullable=False)
    object_technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    strength = Column(Numeric, default=0.5)
    reason = Column(Text)
    evidence_source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class TechnologySource(Base):
    __tablename__ = "technology_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"))
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_items.id", ondelete="CASCADE"))
    evidence_type = Column(Text, default="inferred")
    short_quote = Column(Text)
    paraphrase = Column(Text)
    locator = Column(Text)
    confidence_score = Column(Numeric, default=0.5)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
