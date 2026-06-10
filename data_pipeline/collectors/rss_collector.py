import feedparser
import trafilatura
import logging
from typing import List, Dict, Any
from datetime import datetime
import time
import socket

# Set default socket timeout to 10 seconds to prevent feedparser from hanging
socket.setdefaulttimeout(10.0)

logger = logging.getLogger(__name__)

# Default RSS feeds per industry
DEFAULT_RSS_FEEDS = {
    "logistics": [
        "https://www.supplychainbrain.com/rss/articles",
        "https://feeds.feedburner.com/LogisticsManagement"
    ],
    "pharma": [
        "https://www.fiercepharma.com/rss/fiercepharma.xml",
        "https://www.pharmatimes.com/rss/news"
    ],
    "agriculture": [
        "https://www.sciencedaily.com/rss/plants_animals/agriculture_and_food.xml",
        "https://news.google.com/rss/search?q=agriculture&hl=en-US&gl=US&ceid=US:en"
    ],
    "defense": [
        "https://www.defensenews.com/arc/outboundfeeds/rss/category/home/?size=30",
        "https://news.google.com/rss/search?q=defense+industry&hl=en-US&gl=US&ceid=US:en"
    ]
}

def fetch_rss_feed(feed_url: str, industry: str) -> List[Dict[str, Any]]:
    """Fetches and normalizes articles from a single RSS feed."""
    logger.info(f"[RSS] Parsing feed: {feed_url}")
    articles = []
    
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            # Note: bozo might be 1 for minor XML validation warnings, so we still try to read entries
            logger.warning(f"[RSS] Non-fatal validation warning parsing {feed_url}")
            
        success_count = 0
        failure_count = 0
        
        for entry in feed.entries:
            try:
                # Basic metadata extraction
                title = entry.get("title") or "No Title"
                url = entry.get("link") or ""
                author = entry.get("author") or entry.get("publisher") or "Unknown"
                
                # Check for published date
                published_str = ""
                if "published" in entry:
                    published_str = entry.published
                elif "updated" in entry:
                    published_str = entry.updated
                    
                summary = entry.get("summary") or entry.get("description") or ""
                
                # Fallback to trafilatura if summary is short
                content = summary
                if len(summary) < 200 and url:
                    logger.debug(f"[Trafilatura] Fetching full content for short summary: {url}")
                    try:
                        downloaded = trafilatura.fetch_url(url)
                        if downloaded:
                            extracted = trafilatura.extract(downloaded)
                            if extracted:
                                content = extracted
                                logger.debug(f"[Trafilatura] Extracted {len(content)} chars.")
                    except Exception as te:
                        logger.warning(f"[Trafilatura] Failed to fetch full content from {url}: {te}")
                
                articles.append({
                    "title": title,
                    "content": content,
                    "summary": summary[:500] if summary else None,
                    "source": feed.feed.get("title") or "RSS Feed",
                    "author": author,
                    "url": url,
                    "published_date": published_str,
                    "industry": industry
                })
                success_count += 1
            except Exception as entry_error:
                logger.error(f"[RSS] Error parsing feed entry: {entry_error}")
                failure_count += 1
                
        logger.info(f"[RSS] Feed {feed_url} completed. Success: {success_count}, Failures: {failure_count}")
    except Exception as e:
        logger.error(f"[RSS] Failed to process feed {feed_url}: {e}")
        
    return articles

def fetch_all_rss(feeds_dict: Dict[str, List[str]] = None) -> List[Dict[str, Any]]:
    """Fetches articles from all configured feeds across industries."""
    feeds = feeds_dict or DEFAULT_RSS_FEEDS
    all_articles = []
    
    for industry, feed_urls in feeds.items():
        logger.info(f"[RSS] Processing {len(feed_urls)} feeds for industry: {industry}")
        for url in feed_urls:
            feed_articles = fetch_rss_feed(url, industry)
            all_articles.extend(feed_articles)
            
    return all_articles
