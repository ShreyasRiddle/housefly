import numpy as np
from sqlalchemy.orm import Session
from app.models import DemographicsProfile, Neighborhood
import logging

logger = logging.getLogger(__name__)


def calculate_demographic_score(neighborhood_id: int, db: Session) -> float:
    """Calculate demographic score for a neighborhood (0-1, higher = better)"""
    profile = db.query(DemographicsProfile).filter(
        DemographicsProfile.neighborhood_id == neighborhood_id
    ).first()
    
    if not profile or not profile.raw_data:
        # No data = neutral score
        return 0.5
    
    # Get all profiles for normalization
    all_profiles = db.query(DemographicsProfile).all()
    
    # Extract metrics
    incomes = [p.income_median for p in all_profiles if p.income_median]
    ages = [p.age_median for p in all_profiles if p.age_median]
    household_sizes = [p.household_size_avg for p in all_profiles if p.household_size_avg]
    
    if not incomes:
        return 0.5
    
    # Calculate Z-scores
    income_mean = np.mean(incomes)
    income_std = np.std(incomes) or 1.0
    income_z = (profile.income_median - income_mean) / income_std if profile.income_median else 0.0
    
    age_mean = np.mean(ages) if ages else 0.0
    age_std = np.std(ages) or 1.0
    age_z = (profile.age_median - age_mean) / age_std if profile.age_median else 0.0
    
    household_mean = np.mean(household_sizes) if household_sizes else 0.0
    household_std = np.std(household_sizes) or 1.0
    household_z = (profile.household_size_avg - household_mean) / household_std if profile.household_size_avg else 0.0
    
    # Combine Z-scores (weighted)
    # Higher income = better, optimal age = better, stable household size = better
    composite_score = (
        0.5 * income_z +  # Income is most important
        0.3 * (1.0 - abs(age_z - 0.5)) +  # Age near median is good
        0.2 * (1.0 - abs(household_z))  # Household size near mean is good
    )
    
    # Normalize to [0, 1] using sigmoid
    normalized_score = 1.0 / (1.0 + np.exp(-composite_score))
    
    return max(0.0, min(1.0, normalized_score))


def process_all_demographic_scores(db: Session) -> dict:
    """Process demographic scores for all neighborhoods"""
    logger.info("Processing demographic scores for all neighborhoods")
    
    neighborhoods = db.query(Neighborhood).all()
    scores = {}
    
    for neighborhood in neighborhoods:
        score = calculate_demographic_score(neighborhood.id, db)
        scores[neighborhood.id] = score
        logger.debug(f"Neighborhood {neighborhood.name}: demographic_score = {score:.3f}")
    
    logger.info(f"Processed demographic scores for {len(scores)} neighborhoods")
    return scores

