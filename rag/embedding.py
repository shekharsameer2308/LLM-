import logging
import uuid
from sqlalchemy.orm import Session
from database.models.article import Article
from database.models.embeddings import EmbeddingsMetadata
from database.connection import SessionLocal

logger = logging.getLogger(__name__)

def embed_and_store(article: Article, db: Session = None) -> EmbeddingsMetadata:
    """Mock implementation of embedding and storing in Qdrant."""
    db_created = False
    if db is None:
        db = SessionLocal()
        db_created = True
        
    try:
        # Check if already embedded
        existing = db.query(EmbeddingsMetadata).filter(EmbeddingsMetadata.article_id == article.id).first()
        if existing:
            return existing
            
        vector_id = str(uuid.uuid4())
        
        metadata = EmbeddingsMetadata(
            article_id=article.id,
            vector_id=vector_id
        )
        db.add(metadata)
        db.commit()
        logger.debug(f"[Embedding Mock] Generated mock vector ID {vector_id} for article: {article.title[:30]}...")
        return metadata
    except Exception as e:
        logger.error(f"[Embedding Mock] Error creating embedding metadata for article {article.id}: {e}")
        db.rollback()
        raise e
    finally:
        if db_created:
            db.close()

def embed_batch(articles: list):
    """Stub for batch embedding."""
    db = SessionLocal()
    try:
        for art in articles:
            embed_and_store(art, db)
    finally:
        db.close()
