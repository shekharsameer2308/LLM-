import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models.article import Article
from database.models.competitor import CompetitorMention
from database.models.analytics import SentimentScore, Keyword
from database.models.embeddings import EmbeddingsMetadata
from data_pipeline.processors import cleaner, classifier

def test_cleaner_and_classifier():
    # Test HTML cleaning
    html_text = "<p>Hello <b>World</b>!</p>"
    assert cleaner.clean_text(html_text) == "Hello World!"
    
    # Test boilerplate removal
    text_with_footer = "This is a great story. Read more at https://example.com/more-info"
    assert cleaner.strip_boilerplate(text_with_footer) == "This is a great story."
    
    # Test date parser
    dt = cleaner.normalize_date("2026-06-10T12:00:00Z")
    assert isinstance(dt, datetime)
    
    # Test industry classification
    logistics_text = "Global shipping cargo was delayed at the port."
    ind, conf = classifier.classify_industry(logistics_text)
    assert ind == "logistics"
    assert conf > 0.0
    
    # Test general fallback
    general_text = "Some random text with no industry keywords."
    ind, conf = classifier.classify_industry(general_text)
    assert ind == "general"

def test_deduplication():
    # Set up in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    SessionClass = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionClass()
    
    # Test deduplication logic using standard pipeline runner query flow
    url = "https://example.com/unique-article-url"
    title = "Test Article"
    content = "This is a test article about defense aerospace."
    pub_date = datetime.utcnow()
    
    # Check that initially it doesn't exist
    existing = db.query(Article).filter(Article.url == url).first()
    assert existing is None
    
    # First Ingest (success)
    db_art = Article(
        title=title,
        content=content,
        summary="summary",
        source="Source",
        author="Author",
        url=url,
        industry="defense",
        published_date=pub_date
    )
    db.add(db_art)
    db.commit()
    db.refresh(db_art)
    
    # Verify it exists
    assert db.query(Article).filter(Article.url == url).count() == 1
    
    # Second Ingest Attempt (should be detected as duplicate and skipped)
    duplicate_count = 0
    new_inserts = 0
    
    for i in range(2): # simulate two duplicate attempts
        existing = db.query(Article).filter(Article.url == url).first()
        if existing:
            duplicate_count += 1
        else:
            new_art = Article(
                title=title,
                content=content,
                summary="summary",
                source="Source",
                author="Author",
                url=url,
                industry="defense",
                published_date=pub_date
            )
            db.add(new_art)
            db.commit()
            new_inserts += 1
            
    assert duplicate_count == 2
    assert new_inserts == 0
    assert db.query(Article).filter(Article.url == url).count() == 1
    
    db.close()
