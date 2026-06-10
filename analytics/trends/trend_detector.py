from datetime import datetime, timedelta
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.models.article import Article

logger = logging.getLogger(__name__)

def get_topic_velocity(db: Session, days: int = 7) -> list:
    """Calculates the velocity percentage for each clustered topic over the last N days.
    
    velocity_pct = ((current - previous) / max(previous, 1)) * 100
    """
    logger.info(f"Calculating topic velocity for days={days}...")
    
    now = datetime.utcnow()
    cutoff_current = now - timedelta(days=days)
    cutoff_previous = now - timedelta(days=2 * days)
    
    # 1. Fetch current period counts (last N days)
    current_counts = db.query(
        Article.topic_name,
        func.count(Article.id).label("count")
    ).filter(
        Article.published_date >= cutoff_current,
        Article.topic_name != None,
        Article.topic_name != "Outliers"
    ).group_by(Article.topic_name).all()
    
    # 2. Fetch previous period counts (N to 2N days ago)
    previous_counts = db.query(
        Article.topic_name,
        func.count(Article.id).label("count")
    ).filter(
        Article.published_date >= cutoff_previous,
        Article.published_date < cutoff_current,
        Article.topic_name != None,
        Article.topic_name != "Outliers"
    ).group_by(Article.topic_name).all()
    
    # Map to dicts for easy lookup
    current_dict = {topic_name: count for topic_name, count in current_counts if topic_name}
    previous_dict = {topic_name: count for topic_name, count in previous_counts if topic_name}
    
    # Union of all topic names
    all_topics = set(current_dict.keys()) | set(previous_dict.keys())
    
    velocity_list = []
    for topic_name in all_topics:
        current = current_dict.get(topic_name, 0)
        previous = previous_dict.get(topic_name, 0)
        
        # Calculate velocity percentage
        velocity_pct = ((current - previous) / max(previous, 1)) * 100
        
        velocity_list.append({
            "topic_name": topic_name,
            "current_count": current,
            "previous_count": previous,
            "velocity_pct": round(velocity_pct, 2)
        })
        
    # Sort by velocity percentage descending
    velocity_list = sorted(velocity_list, key=lambda x: x["velocity_pct"], reverse=True)
    
    logger.info(f"Successfully calculated velocity for {len(velocity_list)} topics.")
    return velocity_list
