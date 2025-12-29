from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.orm import Session
from app.models import NewsArticle, Neighborhood
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)

analyzer = SentimentIntensityAnalyzer()


def match_article_to_neighborhood(article: NewsArticle, neighborhood: Neighborhood) -> bool:
    """Match article to neighborhood using keyword matching"""
    text = f"{article.title or ''} {article.content or ''}".lower()
    neighborhood_name = neighborhood.name.lower()
    
    # Check if neighborhood name appears in article
    if neighborhood_name in text:
        return True
    
    # Check for common variations
    variations = [
        neighborhood_name.replace(' ', '-'),
        neighborhood_name.replace(' ', ''),
    ]
    
    for variation in variations:
        if variation in text:
            return True
    
    return False


def calculate_sentiment_score(neighborhood_id: int, db: Session) -> float:
    """Calculate sentiment score for a neighborhood (0-1, higher = better)"""
    neighborhood = db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()
    if not neighborhood:
        return 0.5
    
    # Get articles from last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    articles = db.query(NewsArticle).filter(
        NewsArticle.published_at >= six_months_ago
    ).all()
    
    # Match articles to neighborhood
    matched_articles = []
    for article in articles:
        if match_article_to_neighborhood(article, neighborhood):
            matched_articles.append(article)
    
    if not matched_articles:
        # No articles = neutral score
        return 0.5
    
    # Calculate sentiment for each article
    sentiments = []
    for article in matched_articles:
        text = f"{article.title or ''} {article.content or ''}"
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        
        # Store sentiment score if not already calculated
        if article.sentiment_score is None:
            article.sentiment_score = compound
            db.add(article)
        
        sentiments.append(compound)
    
    db.commit()
    
    # Average sentiment
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    # Normalize from [-1, 1] to [0, 1]
    normalized_score = (avg_sentiment + 1.0) / 2.0
    
    return max(0.0, min(1.0, normalized_score))


def process_all_sentiment_scores(db: Session) -> dict:
    """Process sentiment scores for all neighborhoods"""
    logger.info("Processing sentiment scores for all neighborhoods")
    
    neighborhoods = db.query(Neighborhood).all()
    scores = {}
    
    for neighborhood in neighborhoods:
        score = calculate_sentiment_score(neighborhood.id, db)
        scores[neighborhood.id] = score
        logger.debug(f"Neighborhood {neighborhood.name}: sentiment_score = {score:.3f}")
    
    logger.info(f"Processed sentiment scores for {len(scores)} neighborhoods")
    return scores

