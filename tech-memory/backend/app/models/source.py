from sqlalchemy import Column, String, Text, Numeric, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text)
    canonical_url = Column(Text)
    author = Column(Text)
    organization = Column(Text)
    published_at = Column(TIMESTAMP)
    retrieved_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    source_reliability = Column(Numeric)
    license = Column(Text)
    content_hash = Column(Text)
    access_status = Column(Text, default="accessible")
    metadata_json = Column(JSONB, default={})
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
