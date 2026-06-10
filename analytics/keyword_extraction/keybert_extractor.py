import logging
import re
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import not_
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from database.models.article import Article
from database.models.analytics import Keyword

logger = logging.getLogger(__name__)

# Lazy singleton KeyBERT model reference
_keybert_model = None

def get_keybert() -> KeyBERT:
    """Lazy-loads and returns the KeyBERT model initialized with all-MiniLM-L6-v2."""
    global _keybert_model
    if _keybert_model is None:
        logger.info("[KeyBERT] Loading KeyBERT with all-MiniLM-L6-v2...")
        # Use sentence-transformers explicitly
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        _keybert_model = KeyBERT(model=embedding_model)
        logger.info("[KeyBERT] Model loaded successfully.")
    return _keybert_model

def extract_keywords(article: Article, db: Session) -> List[Keyword]:
    """Extracts keywords/keyphrases for an article using KeyBERT and stores them in the DB."""
    try:
        # Check if keywords already exist
        existing = db.query(Keyword).filter(Keyword.article_id == article.id).all()
        if existing:
            return existing
            
        kw_model = get_keybert()
        
        # Combine title and content to give model context
        text = f"{article.title}. {article.content or ''}"
        
        # Extract keywords using Maximal Marginal Relevance (MMR)
        extracted = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            use_mmr=True,
            diversity=0.5,
            top_n=8
        )
        
        db_keywords = []
        for word, score in extracted:
            kw = Keyword(
                article_id=article.id,
                keyword=word.strip(),
                score=float(score)
            )
            db.add(kw)
            db_keywords.append(kw)
            
        db.commit()
        logger.debug(f"[KeyBERT] Extracted {len(db_keywords)} keywords for: '{article.title[:30]}'")
        return db_keywords
    except Exception as e:
        logger.error(f"[KeyBERT] Error extracting keywords for article {article.id}: {e}")
        db.rollback()
        raise e

if __name__ == "__main__":
    from database.connection import SessionLocal
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger.info("Starting KeyBERT Keyword Extraction CLI...")
    
    db = SessionLocal()
    try:
        # Query articles that don't have any keywords yet
        articles_with_kws = db.query(Keyword.article_id).distinct().subquery()
        articles_to_process = db.query(Article).filter(not_(Article.id.in_(articles_with_kws))).all()
        
        logger.info(f"Found {len(articles_to_process)} articles with no keywords. Starting extraction...")
        
        for idx, art in enumerate(articles_to_process):
            try:
                extract_keywords(art, db)
                if (idx + 1) % 50 == 0 or (idx + 1) == len(articles_to_process):
                    logger.info(f"Processed {idx + 1}/{len(articles_to_process)} articles.")
            except Exception as ex:
                logger.error(f"Error processing article '{art.title[:30]}': {ex}")
                
        logger.info("Keyword extraction complete.")
    finally:
        db.close()
