import logging
import os
import shutil
from sqlalchemy import not_
from database.connection import SessionLocal
from database.models.article import Article
from database.models.analytics import Topic

# Configure logging
logger = logging.getLogger(__name__)

def run_topic_modeling():
    """Run BERTopic modeling on all articles, update the database, and save the model."""
    logger.info("Starting topic modeling batch job...")
    
    db = SessionLocal()
    try:
        # 1. Fetch articles from DB
        articles = db.query(Article).order_by(Article.published_date).all()
        n_articles = len(articles)
        
        if n_articles < 50:
            logger.warning(
                f"Not enough articles to run topic modeling (found {n_articles}, need >= 50). "
                "Exiting batch job."
            )
            return
            
        logger.info(f"Loaded {n_articles} articles for topic modeling clustering.")
        
        # 2. Combine title and content to provide richer context for modeling
        docs = []
        for art in articles:
            title = art.title if art.title else ""
            content = art.content if art.content else ""
            docs.append(f"{title}. {content}")
            
        # 3. Import ML dependencies inside function to support lazy loading
        logger.info("Loading ML models for BERTopic (SentenceTransformers, UMAP, HDBSCAN)...")
        from bertopic import BERTopic
        from umap import UMAP
        from hdbscan import HDBSCAN
        from sentence_transformers import SentenceTransformer
        from sklearn.feature_extraction.text import CountVectorizer
        
        # Configure the BERTopic pipeline components for reproducible results
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        umap_model = UMAP(
            n_components=5,
            n_neighbors=15,
            min_dist=0.0,
            random_state=42
        )
        
        hdbscan_model = HDBSCAN(
            min_cluster_size=10,
            metric='euclidean',
            cluster_selection_method='eom',
            prediction_data=True
        )
        
        vectorizer_model = CountVectorizer(stop_words="english")
        
        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            calculate_probabilities=True,
            verbose=True
        )
        
        # Fit topic model
        logger.info("Fitting BERTopic model on articles...")
        topics, probs = topic_model.fit_transform(docs)
        
        # Reduce topic count to 20
        logger.info("Reducing topic count to maximum 20...")
        topics = topic_model.reduce_topics(docs, nr_topics=20)
        
        # Reload final topics after reduction
        final_topics = topic_model.topics_
        topic_info = topic_model.get_topic_info()
        logger.info(f"Topic modeling completed. Found {len(topic_info)} topics (including outlier -1).")
        
        # 4. Generate descriptive topic names
        # Map topic index to name: join top 3 words with '_'
        topic_name_map = {}
        for topic_idx in topic_info["Topic"]:
            if topic_idx == -1:
                topic_name_map[topic_idx] = "Outliers"
            else:
                words = [w[0] for w in topic_model.get_topic(topic_idx)[:3]]
                topic_name_map[topic_idx] = "_".join(words)
                
        logger.info(f"Generated topic mappings: {topic_name_map}")
        
        # 5. Update articles with their assigned topic names in DB
        logger.info("Updating articles in the database with assigned topic names...")
        for art, t_idx in zip(articles, final_topics):
            art.topic_name = topic_name_map.get(t_idx, "Outliers")
            
        # 6. Clear old topics in the DB and insert new ones
        logger.info("Clearing old topics from DB and inserting new topic metadata...")
        db.query(Topic).delete()
        
        for idx, row in topic_info.iterrows():
            t_idx = row["Topic"]
            # Exclude outliers from the top topics list
            if t_idx == -1:
                continue
                
            topic_name = topic_name_map[t_idx]
            freq = int(row["Count"])
            
            db_topic = Topic(
                topic_name=topic_name,
                frequency=freq
            )
            db.add(db_topic)
            
        db.commit()
        
        # 7. Save model to analytics/topic_modeling/saved_model
        save_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "saved_model"
        )
        logger.info(f"Saving BERTopic model to {save_path}...")
        
        # Clean up existing saved model directory if it exists
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
            
        os.makedirs(save_path, exist_ok=True)
        topic_model.save(save_path, serialization="safetensors", save_ctfidf=True, save_embedding_model=True)
        
        logger.info("Topic modeling batch job completed successfully.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred during topic modeling batch job: {e}", exc_info=True)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_topic_modeling()
