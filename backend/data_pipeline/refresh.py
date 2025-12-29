import logging
from sqlalchemy.orm import Session
from .collectors import (
    crime_collector,
    infrastructure_collector,
    demographics_collector,
    sentiment_collector
)
from .calculator import calculate_profitability_scores

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_refresh_pipeline(db: Session):
    """Orchestrate the complete data refresh pipeline"""
    logger.info("=" * 60)
    logger.info("Starting Housefly data refresh pipeline")
    logger.info("=" * 60)
    
    try:
        # Step 1: Collect crime data
        logger.info("\n[1/4] Collecting crime data...")
        crime_collector.collect_crime_data(db, limit=10000)
        
        # Step 2: Collect infrastructure data
        logger.info("\n[2/4] Collecting infrastructure data...")
        infrastructure_collector.collect_infrastructure_data(db, limit=10000)
        
        # Step 3: Collect demographics data
        logger.info("\n[3/4] Collecting demographics data...")
        demographics_collector.collect_demographics_data(db)
        
        # Step 4: Collect sentiment data
        logger.info("\n[4/4] Collecting sentiment data...")
        sentiment_collector.collect_sentiment_data(db, days_back=180)
        
        # Step 5: Calculate scores
        logger.info("\n[5/5] Calculating profitability scores...")
        calculate_profitability_scores(db)
        
        logger.info("=" * 60)
        logger.info("Data refresh pipeline completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in refresh pipeline: {e}", exc_info=True)
        db.rollback()
        raise

