import re
from datetime import datetime
import dateutil.parser
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Removes HTML tags and normalizes whitespace."""
    if not text:
        return ""
    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", "", text)
    # Normalize whitespaces (tabs, newlines, multiple spaces) to a single space
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def strip_boilerplate(text: str) -> str:
    """Removes common news footers and boilerplate text."""
    if not text:
        return ""
    
    # Common boilerplate regular expression patterns (case-insensitive)
    patterns = [
        r"(?i)read\s+more\s+at\s*[:\-\s]+.*",
        r"(?i)subscribe\s+to\s+.*",
        r"(?i)click\s+here\s+to\s+.*",
        r"(?i)sign\s+up\s+for\s+our\s+newsletter.*",
        r"(?i)follow\s+us\s+on\s+(twitter|facebook|linkedin).*",
        r"(?i)copyright\s+\(c\)\s+\d{4}.*",
        r"(?i)all\s+rights\s+reserved.*",
        r"(?i)this\s+article\s+was\s+originally\s+published.*"
    ]
    
    cleaned = text
    for pattern in patterns:
        # Split text on pattern and keep the first part (pre-boilerplate)
        parts = re.split(pattern, cleaned)
        if parts:
            cleaned = parts[0]
            
    return cleaned.strip()

def normalize_date(date_str: str) -> datetime:
    """Parses various date string formats into a datetime object."""
    if not date_str:
        return datetime.utcnow()
    try:
        return dateutil.parser.parse(date_str)
    except Exception as e:
        logger.warning(f"[Cleaner] Failed to parse date '{date_str}': {e}. Defaulting to current UTC time.")
        return datetime.utcnow()

def truncate(text: str, max_chars: int = 5000) -> str:
    """Truncates text to a maximum length to avoid token bloat."""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].strip()

def detect_mentions(content: str, companies: List[str]) -> List[Dict[str, Any]]:
    """Detects company mentions, counts them, and extracts context snippets."""
    if not content or not companies:
        return []
        
    mentions = []
    content_lower = content.lower()
    
    for company in companies:
        company_lower = company.lower()
        start_idx = 0
        indices = []
        
        # Case-insensitive search for all occurrences
        while True:
            idx = content_lower.find(company_lower, start_idx)
            if idx == -1:
                break
            indices.append(idx)
            start_idx = idx + len(company_lower)
            
        if indices:
            count = len(indices)
            first_idx = indices[0]
            # Extract a 200-char window (approx 100 before, 100 after)
            snippet_start = max(0, first_idx - 100)
            snippet_end = min(len(content), first_idx + len(company) + 100)
            snippet = content[snippet_start:snippet_end].strip()
            
            mentions.append({
                "company_name": company,
                "mention_count": count,
                "context_snippet": snippet
            })
            
    return mentions

def process_batch(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Cleans and processes a list of raw article dicts in-place."""
    processed = []
    for art in articles:
        # Clean title
        title = clean_text(art.get("title") or "")
        
        # Clean content
        content = art.get("content") or ""
        cleaned_content = clean_text(content)
        cleaned_content = strip_boilerplate(cleaned_content)
        cleaned_content = truncate(cleaned_content)
        
        # Normalize date
        pub_date = normalize_date(art.get("published_date") or "")
        
        # Update dict in-place
        art["title"] = title
        art["content"] = cleaned_content
        art["published_date"] = pub_date
        
        processed.append(art)
        
    return processed
