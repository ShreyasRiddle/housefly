import requests
from sqlalchemy.orm import Session
from app.models import DemographicsProfile, Neighborhood
import logging

logger = logging.getLogger(__name__)

DEMOGRAPHICS_URL = "https://data.buffalony.gov/stories/s/Neighborhood-Population-Profile/cry5-9ict"


def collect_demographics_data(db: Session):
    """Collect demographics data from Buffalo Open Data"""
    logger.info("Starting demographics data collection")
    
    try:
        # The demographics data might be in a different format (story/page)
        # We'll need to scrape or use a different endpoint
        # For now, create a placeholder that can be extended
        
        # Try to find the actual API endpoint or data export
        # This is a placeholder - actual implementation depends on data format
        
        neighborhoods = db.query(Neighborhood).all()
        updated_count = 0
        
        for neighborhood in neighborhoods:
            # Check if profile exists
            profile = db.query(DemographicsProfile).filter(
                DemographicsProfile.neighborhood_id == neighborhood.id
            ).first()
            
            if not profile:
                # Create placeholder profile (will be updated with real data)
                profile = DemographicsProfile(
                    neighborhood_id=neighborhood.id,
                    raw_data={}
                )
                db.add(profile)
            else:
                # Update existing
                pass
            
            updated_count += 1
        
        db.commit()
        logger.info(f"Demographics data collection complete: {updated_count} profiles processed")
        logger.warning("Note: Actual demographics data collection needs to be implemented based on data source format")
        return updated_count
    
    except Exception as e:
        logger.error(f"Error in demographics collection: {e}")
        db.rollback()
        raise

