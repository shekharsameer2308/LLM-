import logging
from sqlalchemy.orm import Session
from database.models.article import Article
from database.models.analytics import SentimentScore

logger = logging.getLogger(__name__)

def analyze_sentiment(article: Article, db: Session) -> SentimentScore:
    """Mock implementation of FinBERT sentiment analysis for pipeline integration."""
    try:
        # Check if score already exists
        existing = db.query(SentimentScore).filter(SentimentScore.article_id == article.id).first()
        if existing:
            return existing
            
        # Basic heuristic for mock sentiment
        content_lower = article.content.lower()
        if any(w in content_lower for w in ["growth", "success", "breakthrough", "smart", "climb"]):
            sentiment = "positive"
            score = 0.85
        elif any(w in content_lower for w in ["decline", "challenges", "disruption", "delay", "failed"]):
            sentiment = "negative"
            score = 0.78
        else:
            sentiment = "neutral"
            score = 0.65
            
        db_score = SentimentScore(
            article_id=article.id,
            sentiment=sentiment,
            score=score
        )
        db.add(db_score)
        db.commit()
        logger.debug(f"[Sentiment Mock] Analyzed article: {article.title[:30]}... Result: {sentiment} ({score})")
        return db_score
    except Exception as e:
        logger.error(f"[Sentiment Mock] Error analyzing article {article.id}: {e}")
        db.rollback()
        raise e

def analyze_batch(articles: list, db: Session):
    """Stub for batch sentiment analysis."""
    for art in articles:
        analyze_sentiment(art, db)
