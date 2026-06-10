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

@router.post("/ingest-keyword")
async def ingest_keyword(q: str, db: Session = Depends(get_db)):
    """Fetches articles from Google News search feed matching q,
    cleans them, normalizes them, and runs the full pipeline (FinBERT, KeyBERT, Qdrant, Competitors).
    """
    import feedparser
    import requests
    import re
    import trafilatura
    import logging
    from database.models.competitor import CompetitorMention
    from database.models.analytics import SentimentScore, Keyword
    from database.models.embeddings import EmbeddingsMetadata
    from data_pipeline.processors import cleaner, classifier
    from analytics.sentiment.finbert import analyze_sentiment
    from analytics.keyword_extraction.keybert_extractor import extract_keywords
    from rag.embedding import embed_and_store
    from data_pipeline.scheduler.pipeline_runner import WATCHLIST
    
    logger = logging.getLogger(__name__)
    
    if not q:
        raise HTTPException(status_code=400, detail="Search query parameter 'q' is required")
        
    query_encoded = requests.utils.quote(q)
    feed_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-US&gl=US&ceid=US:en"
    
    articles_fetched = 0
    new_ingested = 0
    duplicates_skipped = 0
    errors = 0
    
    ingested_details = []
    
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        # Ingest top 15 entries
        for entry in feed.entries[:15]:
            articles_fetched += 1
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "") or entry.get("description") or ""
            source = entry.get("source", {}).get("name") if entry.get("source") else "Google News"
            pub_date_str = entry.get("published", "")
            
            # 1. Clean HTML from summary
            clean_summary = cleaner.clean_text(summary)
            clean_summary = cleaner.strip_boilerplate(clean_summary)
            
            # 2. Check for duplicate URL in DB
            existing = db.query(Article).filter(Article.url == url).first()
            if existing:
                duplicates_skipped += 1
                continue
                
            # 3. Extract full content using trafilatura
            content = clean_summary
            if url:
                try:
                    downloaded = trafilatura.fetch_url(url)
                    if downloaded:
                        extracted = trafilatura.extract(downloaded)
                        if extracted:
                            content = cleaner.clean_text(extracted)
                            content = cleaner.strip_boilerplate(content)
                            content = cleaner.truncate(content)
                except Exception as te:
                    logger.warning(f"Trafilatura failed for {url}: {te}")
                    
            # Normalize pub date
            published_date = cleaner.normalize_date(pub_date_str)
            
            # 4. Classify industry
            industry, confidence = classifier.classify_industry(content or title)
            
            try:
                # 5. Insert Article
                db_article = Article(
                    title=title,
                    content=content,
                    summary=clean_summary[:400] + "..." if len(clean_summary) > 400 else clean_summary,
                    source=source,
                    author="Google News RSS Scraper",
                    url=url,
                    industry=industry,
                    published_date=published_date
                )
                db.add(db_article)
                db.commit()
                db.refresh(db_article)
                
                # 6. Analyze Sentiment
                db_sentiment = analyze_sentiment(db_article, db)
                sentiment_val = db_sentiment.sentiment if db_sentiment else "neutral"
                
                # 7. Extract Keywords
                db_kws = extract_keywords(db_article, db)
                kws_list = [k.keyword for k in db_kws] if db_kws else []
                
                # 8. Embed and Store in Qdrant (RAG index)
                embed_and_store(db_article, db)
                
                # 9. Detect competitor mentions
                mentions = cleaner.detect_mentions(content, WATCHLIST)
                if mentions:
                    for mention in mentions:
                        db_mention = CompetitorMention(
                            article_id=db_article.id,
                            company_name=mention["company_name"],
                            mention_count=mention["mention_count"],
                            context_snippet=mention["context_snippet"]
                        )
                        db.add(db_mention)
                    db.commit()
                    
                new_ingested += 1
                
                ingested_details.append({
                    "id": str(db_article.id),
                    "title": db_article.title,
                    "url": db_article.url,
                    "source": db_article.source,
                    "industry": db_article.industry,
                    "sentiment": sentiment_val,
                    "keywords": kws_list[:5]
                })
                
            except Exception as e:
                logger.error(f"Failed to ingest article '{title[:30]}': {e}")
                errors += 1
                db.rollback()
                
    except Exception as e:
        logger.error(f"Error fetching Google News feed for query '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Google News feed: {str(e)}")
        
    return {
        "status": "success",
        "stats": {
            "total_fetched": articles_fetched,
            "new_ingested": new_ingested,
            "duplicates_skipped": duplicates_skipped,
            "errors": errors
        },
        "articles": ingested_details
    }

@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(article_id: UUID, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

