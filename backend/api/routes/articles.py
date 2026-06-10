from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models.article import Article
from backend.schemas.article import ArticleOut

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=List[ArticleOut])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    industry: Optional[str] = None,
    topic: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Article)
    if industry:
        query = query.filter(Article.industry == industry)
    if topic:
        query = query.filter(Article.topic_name == topic)
    if search:
        # ilike is case-insensitive search
        query = query.filter(
            (Article.title.ilike(f"%{search}%")) | (Article.content.ilike(f"%{search}%"))
        )
    articles = query.order_by(Article.published_date.desc()).offset(skip).limit(limit).all()
    return articles



@router.get("/fetch-internet")
async def fetch_internet_articles(q: str):
    """Fetches articles for a custom product query from Google News RSS feed,
    performs real-time brand detection and lexical sentiment analysis, and aggregates stats.
    """
    import feedparser
    import requests
    import re
    
    if not q:
        return {"articles": [], "stats": {}}
        
    query_encoded = requests.utils.quote(q)
    feed_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-US&gl=US&ceid=US:en"
    
    # Common brands for matching
    BRANDS = [
        "Apple", "Samsung", "Google", "Microsoft", "Dell", "HP", "Lenovo", "Asus", 
        "Acer", "Huawei", "Xiaomi", "Sony", "LG", "Tesla", "BYD", "Nvidia", "Intel", 
        "AMD", "Amazon", "Meta", "Toyota", "Ford", "GM", "Reliance"
    ]
    
    # Lexical lists
    POSITIVE_WORDS = {
        "innovative", "innovation", "growth", "breakthrough", "record", "profit", 
        "surpasses", "succeed", "popular", "advanced", "leadership", "excellent", 
        "rise", "gains", "partnership", "collaboration", "upgrade", "success", "boost", 
        "revenue", "demand", "unveiled", "unveils", "strong", "best", "leading"
    }
    NEGATIVE_WORDS = {
        "decline", "layoff", "layoffs", "drop", "deficit", "regulatory", "lawsuit", 
        "delay", "crash", "recall", "fail", "plunge", "loss", "warning", "decrease", 
        "lawsuits", "investigation", "fined", "dip", "falls", "slump", "cuts", "debt"
    }
    
    articles = []
    stats = {}
    
    try:
        # Fetch RSS
        response = requests.get(feed_url, timeout=8)
        feed = feedparser.parse(response.content)
        
        for entry in feed.entries[:40]: # limit to 40 articles
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            url = entry.get("link", "")
            source = entry.get("source", {}).get("name", "Google News")
            pub_date = entry.get("published", "")
            
            # 1. Clean HTML from summary
            clean_summary = re.sub(r'<[^>]*>', '', summary)
            
            # 2. Match brands
            matched_brands = []
            text_to_scan = f"{title} {clean_summary}".lower()
            for brand in BRANDS:
                if re.search(r'\b' + re.escape(brand.lower()) + r'\b', text_to_scan):
                    matched_brands.append(brand)
                    
            # 3. Sentiment analysis (lexical)
            words = re.findall(r'\b\w+\b', text_to_scan)
            pos_score = sum(1 for w in words if w in POSITIVE_WORDS)
            neg_score = sum(1 for w in words if w in NEGATIVE_WORDS)
            
            if pos_score > neg_score:
                sentiment = "positive"
            elif neg_score > pos_score:
                sentiment = "negative"
            else:
                sentiment = "neutral"
                
            if not matched_brands:
                matched_brands = ["General"]
                
            articles.append({
                "title": title,
                "summary": clean_summary[:400] + "..." if len(clean_summary) > 400 else clean_summary,
                "url": url,
                "source": source,
                "published_date": pub_date,
                "sentiment": sentiment,
                "brands": matched_brands
            })
            
            # 4. Aggregated stats
            for brand in matched_brands:
                if brand == "General":
                    continue
                if brand not in stats:
                    stats[brand] = {
                        "mentions": 0,
                        "positive": 0,
                        "negative": 0,
                        "neutral": 0
                    }
                stats[brand]["mentions"] += 1
                stats[brand][sentiment] += 1
                
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to fetch live RSS feeds for {q}: {e}")
        return {"articles": [], "stats": {}, "error": str(e)}
        
    return {
        "articles": articles,
        "stats": stats
    }

@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(article_id: UUID, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

