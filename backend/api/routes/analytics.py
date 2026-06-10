from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from backend.schemas.analytics import SentimentSummaryItem, SentimentTrendItem, KeywordOut, TopicOut, TopicVelocityItem, CompetitorSummaryItem, CompetitorMentionDetail
from backend.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/sentiment", response_model=List[SentimentSummaryItem])
async def get_sentiment_summary(industry: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns overall sentiment summary (count and percentage)."""
    return analytics_service.sentiment_summary(db, industry=industry)

@router.get("/sentiment-trend", response_model=List[SentimentTrendItem])
async def get_sentiment_trend(days: int = 30, db: Session = Depends(get_db)):
    """Returns daily sentiment timeline counts over a given number of days."""
    return analytics_service.sentiment_over_time(db, days=days)

@router.get("/keywords", response_model=List[KeywordOut])
async def get_trending_keywords(days: int = 7, db: Session = Depends(get_db)):
    """Returns top trending keywords sorted by average relevance score."""
    return analytics_service.trending_keywords(db, days=days)

@router.get("/topics", response_model=List[TopicOut])
async def get_top_topics(limit: int = 10, db: Session = Depends(get_db)):
    """Returns top dynamically identified topics."""
    return analytics_service.top_topics(db, limit=limit)

@router.get("/topics/velocity", response_model=List[TopicVelocityItem])
async def get_topic_velocity(days: int = 7, db: Session = Depends(get_db)):
    """Returns topic velocity trends (frequency shift in last N days vs previous N days)."""
    return analytics_service.topic_velocity(db, days=days)

@router.get("/competitors", response_model=List[CompetitorSummaryItem])
async def get_competitor_summaries(db: Session = Depends(get_db)):
    """Returns overall summaries of tracked competitors (mention volume, industry/sentiment splits)."""
    return analytics_service.get_competitor_summaries(db)

@router.get("/competitors/{company_name}", response_model=List[CompetitorMentionDetail])
async def get_competitor_mentions(company_name: str, db: Session = Depends(get_db)):
    """Returns list of all article mentions for a specific competitor."""
    return analytics_service.get_competitor_mentions(db, company_name=company_name)
