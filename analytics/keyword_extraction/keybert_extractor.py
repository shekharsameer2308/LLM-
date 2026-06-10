import logging
import re
from sqlalchemy.orm import Session
from database.models.article import Article
from database.models.analytics import Keyword

logger = logging.getLogger(__name__)

def extract_keywords(article: Article, db: Session) -> list:
    """Mock implementation of KeyBERT keyword extraction for pipeline integration."""
    try:
        # Check if keywords already exist
        existing = db.query(Keyword).filter(Keyword.article_id == article.id).all()
        if existing:
            return existing
            
        # Basic mock keyword extraction (extract capitalized words or nouns from title/content)
        words = re.findall(r"\b[a-zA-Z]{5,15}\b", f"{article.title} {article.content}")
        # Unique list
        unique_words = list(set([w.lower() for w in words]))
        
        # Pick top 5-8 words
        keywords_to_add = unique_words[:8]
        db_keywords = []
        
        for i, word in enumerate(keywords_to_add):
            kw = Keyword(
                article_id=article.id,
                keyword=word,
                score=round(0.9 - (i * 0.05), 2)
            )
            db.add(kw)
            db_keywords.append(kw)
            
        db.commit()
        logger.debug(f"[Keyword Mock] Extracted {len(db_keywords)} keywords for article: {article.title[:30]}...")
        return db_keywords
    except Exception as e:
        logger.error(f"[Keyword Mock] Error extracting keywords for article {article.id}: {e}")
        db.rollback()
        raise e

if __name__ == "__main__":
    print("Keyword extraction stub runner active.")
