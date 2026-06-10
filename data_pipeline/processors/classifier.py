import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Keywords associated with each tracked industry
INDUSTRY_KEYWORDS = {
    "logistics": [
        "supply chain", "shipping", "freight", "cargo", "warehouse", 
        "delivery", "distribution", "trucking", "maritime", "port", 
        "transport", "logistics", "carrier", "fulfillment", "fleet"
    ],
    "pharma": [
        "pharma", "biotech", "drug", "oncology", "clinical trial", 
        "therapeutic", "vaccine", "medicine", "pharmaceutical", "fda", 
        "biotechnology", "clinical trials", "pathogen", "therapies"
    ],
    "agriculture": [
        "agriculture", "crops", "farming", "harvest", "irrigation", 
        "soil", "livestock", "agtech", "yield", "cultivation", 
        "farmers", "fertilizer", "crop", "agribusiness", "agrarian"
    ],
    "defense": [
        "defense", "military", "weapon", "stealth", "uav", "cyber defense", 
        "aerospace", "pentagon", "contractor", "army", "navy", 
        "air force", "warfare", "munitions", "defense industry"
    ]
}

def classify_industry(text: str) -> Tuple[str, float]:
    """Classifies the industry of a text block based on keyword occurrence counts.
    
    Returns a tuple of (industry, confidence).
    If confidence is < 0.2, returns ('general', confidence).
    """
    if not text:
        return ("general", 0.0)
        
    text_lower = text.lower()
    scores = {}
    
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        matched_count = 0
        for kw in keywords:
            # Check if keyword is present in the text
            if kw in text_lower:
                matched_count += 1
        scores[industry] = matched_count
        
    # Determine the winning industry
    winning_industry = "general"
    max_matches = 0
    confidence = 0.0
    
    for industry, matched in scores.items():
        if matched > max_matches:
            max_matches = matched
            winning_industry = industry
            total_kws = len(INDUSTRY_KEYWORDS[industry])
            confidence = matched / total_kws if total_kws > 0 else 0.0
            
    # Fallback to general if confidence is low or no keywords matched
    if max_matches == 0 or confidence < 0.2:
        return ("general", confidence)
        
    return (winning_industry, confidence)
