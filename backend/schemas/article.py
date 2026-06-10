from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    url: str
    industry: str
    published_date: datetime
    topic_name: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleOut(ArticleBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
