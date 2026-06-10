import os
import time
import logging
from typing import List, Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# Load env variables
load_dotenv()

logger = logging.getLogger(__name__)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_URL = "https://newsapi.org/v2/everything"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=True
)
def _fetch_page(query: str, api_key: str, page: int = 1) -> Dict[str, Any]:
    """Fetches a single page of results from NewsAPI with retries."""
    params = {
        "q": query,
        "apiKey": api_key,
        "language": "en",
        "pageSize": 50,
        "page": page
    }
    response = requests.get(NEWSAPI_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def fetch_industry_articles(industry: str) -> List[Dict[str, Any]]:
    """Fetches articles for a specific industry from NewsAPI."""
    if not NEWSAPI_KEY or NEWSAPI_KEY in ["mock_key", "your_newsapi_key_here"]:
        logger.warning(f"[NewsAPI] No valid API key found. Returning mock data for {industry}.")
        return _get_mock_articles(industry)

    logger.info(f"[NewsAPI] Fetching articles for industry: {industry}")
    try:
        data = _fetch_page(industry, NEWSAPI_KEY, page=1)
        raw_articles = data.get("articles", [])
        normalized = []
        for art in raw_articles:
            # Skip removed articles
            if art.get("title") == "[Removed]":
                continue
            
            normalized.append({
                "title": art.get("title") or "",
                "content": art.get("content") or art.get("description") or "",
                "source": art.get("source", {}).get("name") if art.get("source") else "Unknown",
                "author": art.get("author") or "Unknown",
                "url": art.get("url") or "",
                "published_date": art.get("publishedAt") or "",
                "industry": industry
            })
        
        logger.info(f"[NewsAPI] Fetched {len(normalized)} articles for {industry}")
        return normalized
    except Exception as e:
        logger.error(f"[NewsAPI] Error fetching articles for {industry}: {e}")
        return []

def fetch_all_industries(industries: List[str]) -> List[Dict[str, Any]]:
    """Fetches articles for multiple industries, respecting rate limits."""
    all_articles = []
    for idx, industry in enumerate(industries):
        if idx > 0:
            # Respect rate limit by sleeping between requests
            time.sleep(1.0)
        
        articles = fetch_industry_articles(industry)
        all_articles.extend(articles)
        
    return all_articles

def _get_mock_articles(industry: str) -> List[Dict[str, Any]]:
    """Generates mock articles for development and dry run testing."""
    from datetime import datetime, timedelta
    import random
    
    mock_templates = {
        "logistics": [
            ("Global Supply Chain Disruptions Loom", "Major delays are expected across maritime shipping lanes due to new port restrictions."),
            ("Autonomous Trucks Enter Cargo Fleet", "A leading logistics provider rolls out a fleet of autonomous heavy trucks for interstate freight transport.")
        ],
        "pharma": [
            ("Breakthrough Drug Approval by FDA", "A new oncology therapeutic has received expedited approval, promising improved patient outcomes."),
            ("Biotech Sector Faces Funding Challenges", "Early stage drug discovery startups report tightening venture capital markets this quarter.")
        ],
        "agriculture": [
            ("Climate-Resilient Crops Show High Yields", "Agricultural science labs report success with genetically edited drought-tolerant wheat varieties."),
            ("Smart Irrigation Adoption Spikes", "Farmers adopt automated IoT-based soil moisture tracking systems to save water usage.")
        ],
        "defense": [
            ("Cyber Defense Alliances Formed", "Multinational cybersecurity pacts are signed to protect satellite communications networks."),
            ("Next-Gen Unmanned Aerial Vehicles Unveiled", "A top contractor demonstrates stealth capabilities of autonomous intelligence UAVs.")
        ],
        "general": [
            ("Market Trends Overview", "Experts discuss interest rate dynamics and their impact on global manufacturing and tech indices."),
            ("Corporate Sustainability Reports Rise", "More corporations disclose carbon accounting metrics in response to regulatory audits.")
        ]
    }
    
    templates = mock_templates.get(industry, mock_templates["general"])
    mock_results = []
    
    for i, (title, desc) in enumerate(templates):
        pub_time = (datetime.utcnow() - timedelta(days=random.randint(0, 5))).isoformat() + "Z"
        mock_results.append({
            "title": f"[Mock] {title} in {industry.capitalize()}",
            "content": f"{desc} This full article text contains additional mock descriptions regarding market research inside the field of {industry}.",
            "source": "Mock Source News",
            "author": "Mock Journalist",
            "url": f"https://mocknewsapi.com/{industry}/{i}",
            "published_date": pub_time,
            "industry": industry
        })
        
    return mock_results
