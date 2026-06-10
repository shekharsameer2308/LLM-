from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SentimentSummaryItem(BaseModel):
    sentiment: str
    count: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)

class TopicOut(BaseModel):
    topic_name: str
    frequency: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)

class KeywordOut(BaseModel):
    keyword: str
    score: float

    model_config = ConfigDict(from_attributes=True)

class SentimentTrendItem(BaseModel):
    date: str
    positive: int
    negative: int
    neutral: int

    model_config = ConfigDict(from_attributes=True)

class TopicVelocityItem(BaseModel):
    topic_name: str
    current_count: int
    previous_count: int
    velocity_pct: float

    model_config = ConfigDict(from_attributes=True)

class CompetitorSummaryItem(BaseModel):
    company_name: str
    total_mentions: int
    industry_breakdown: dict
    sentiment_breakdown: dict

    model_config = ConfigDict(from_attributes=True)

class CompetitorMentionDetail(BaseModel):
    article_title: str
    article_url: str
    sentiment: str
    mention_count: int
    context_snippet: str
    published_date: datetime

    model_config = ConfigDict(from_attributes=True)
