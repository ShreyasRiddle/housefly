from sqlalchemy.orm import Session
from app.models import Score, ScoreHistory, Neighborhood
from app.config import load_weights_config
from .processors import (
    crime_processor,
    infrastructure_processor,
    demographics_processor,
    sentiment_processor
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def calculate_profitability_scores(db: Session):
    """Calculate profitability scores for all neighborhoods"""
    logger.info("Starting profitability score calculation")
    
    # Load weights configuration
    weights = load_weights_config()
    
    # Process all subscores
    logger.info("Processing crime scores...")
    crime_scores = crime_processor.process_all_crime_scores(db)
    
    logger.info("Processing infrastructure scores...")
    infrastructure_scores = infrastructure_processor.process_all_infrastructure_scores(db)
    
    logger.info("Processing demographic scores...")
    demographic_scores = demographics_processor.process_all_demographic_scores(db)
    
    logger.info("Processing sentiment scores...")
    sentiment_scores = sentiment_processor.process_all_sentiment_scores(db)
    
    # Calculate profitability scores
    neighborhoods = db.query(Neighborhood).all()
    
    for neighborhood in neighborhoods:
        crime_score = crime_scores.get(neighborhood.id, 0.5)
        infra_score = infrastructure_scores.get(neighborhood.id, 0.5)
        demo_score = demographic_scores.get(neighborhood.id, 0.5)
        sent_score = sentiment_scores.get(neighborhood.id, 0.5)
        
        # Apply weighted formula
        profitability_score = (
            weights.crime_weight * crime_score +
            weights.infrastructure_weight * infra_score +
            weights.demographic_weight * demo_score +
            weights.sentiment_weight * sent_score
        )
        
        # Convert to 0-100 scale
        profitability_score_100 = profitability_score * 100
        
        # Save to database
        score = Score(
            neighborhood_id=neighborhood.id,
            crime_score=crime_score,
            infrastructure_score=infra_score,
            demographic_score=demo_score,
            sentiment_score=sent_score,
            profitability_score=profitability_score_100,
            calculated_at=datetime.now()
        )
        db.add(score)
        
        # Also save to history
        history = ScoreHistory(
            neighborhood_id=neighborhood.id,
            crime_score=crime_score,
            infrastructure_score=infra_score,
            demographic_score=demo_score,
            sentiment_score=sent_score,
            profitability_score=profitability_score_100,
            calculated_at=datetime.now()
        )
        db.add(history)
        
        logger.debug(
            f"Neighborhood {neighborhood.name}: "
            f"profitability = {profitability_score_100:.1f} "
            f"(crime={crime_score:.2f}, infra={infra_score:.2f}, "
            f"demo={demo_score:.2f}, sent={sent_score:.2f})"
        )
    
    db.commit()
    logger.info(f"Calculated profitability scores for {len(neighborhoods)} neighborhoods")

