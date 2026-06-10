import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, UUID
from sqlalchemy.orm import relationship
from database.connection import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    published_date = Column(DateTime, nullable=False, index=True)
    topic_name = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sentiment_score = relationship("SentimentScore", uselist=False, back_populates="article", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="article", cascade="all, delete-orphan")
    embeddings_metadata = relationship("EmbeddingsMetadata", uselist=False, back_populates="article", cascade="all, delete-orphan")
    competitor_mentions = relationship("CompetitorMention", back_populates="article", cascade="all, delete-orphan")
