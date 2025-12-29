import requests
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import NewsArticle
import logging

logger = logging.getLogger(__name__)

GNEWS_API_URL = "https://gnews.io/api/v4/search"


def collect_sentiment_data(db: Session, days_back: int = 180):
    """Collect news articles from GNews API for sentiment analysis"""
    logger.info("Starting sentiment data collection")
    
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        logger.warning("GNEWS_API_KEY not set, using fallback data")
        return collect_fallback_sentiment_data(db)
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            'q': 'Buffalo NY OR Buffalo, New York',
            'lang': 'en',
            'country': 'us',
            'max': 100,  # Free tier limit
            'apikey': api_key,
            'from': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'to': end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        response = requests.get(GNEWS_API_URL, params=params, timeout=30)
        
        if response.status_code == 429:
            logger.warning("GNews API rate limit exceeded, using fallback data")
            return collect_fallback_sentiment_data(db)
        
        response.raise_for_status()
        data = response.json()
        
        articles = data.get('articles', [])
        logger.info(f"Fetched {len(articles)} news articles")
        
        added_count = 0
        skipped_count = 0
        
        for article in articles:
            try:
                article_id = article.get('url') or article.get('title', '')[:100]
                if not article_id:
                    skipped_count += 1
                    continue
                
                # Check if already exists
                existing = db.query(NewsArticle).filter(
                    NewsArticle.article_id == article_id
                ).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # Parse date
                date_str = article.get('publishedAt')
                if date_str:
                    try:
                        published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        published_at = datetime.now()
                else:
                    published_at = datetime.now()
                
                # Create article record
                news_article = NewsArticle(
                    article_id=article_id,
                    title=article.get('title'),
                    content=article.get('description') or article.get('content'),
                    published_at=published_at,
                    source=article.get('source', {}).get('name'),
                    url=article.get('url'),
                    raw_data=article
                )
                
                db.add(news_article)
                added_count += 1
            
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                skipped_count += 1
                continue
        
        db.commit()
        logger.info(f"Sentiment data collection complete: {added_count} added, {skipped_count} skipped")
        return added_count
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news data: {e}")
        logger.warning("Falling back to cached/sample data")
        return collect_fallback_sentiment_data(db)
    except Exception as e:
        logger.error(f"Unexpected error in sentiment collection: {e}")
        db.rollback()
        return collect_fallback_sentiment_data(db)


def collect_fallback_sentiment_data(db: Session):
    """Fallback: Use cached or sample sentiment data"""
    logger.info("Using fallback sentiment data")
    # In a real implementation, this would load from a cached file
    # For now, we'll just return 0 and let the processor handle missing data
    return 0

