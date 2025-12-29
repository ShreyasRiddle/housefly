import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import CrimeIncident, Neighborhood
import logging

logger = logging.getLogger(__name__)


def calculate_crime_score(neighborhood_id: int, db: Session) -> float:
    """Calculate crime score for a neighborhood (0-1, higher = better)"""
    # Get all crimes for this neighborhood
    crimes = db.query(CrimeIncident).filter(
        CrimeIncident.neighborhood_id == neighborhood_id
    ).all()
    
    if not crimes:
        # No crime data = perfect score
        return 1.0
    
    # Time decay: more recent crimes weighted higher
    now = datetime.now()
    time_decay_factor = 0.1  # Crimes older than ~2 years have minimal weight
    
    # Severity weights
    severity_weights = {
        'violent': 3.0,
        'property': 1.5,
        'other': 1.0
    }
    
    weighted_crime_count = 0.0
    
    for crime in crimes:
        # Time decay: exponential decay
        days_ago = (now - crime.date).days
        time_weight = np.exp(-time_decay_factor * days_ago / 365.0)
        
        # Severity weight
        severity_weight = severity_weights.get(crime.severity, 1.0)
        
        # Combined weight
        weight = time_weight * severity_weight
        weighted_crime_count += weight
    
    # Normalize: compare to max across all neighborhoods
    max_crimes = db.query(
        func.sum(func.cast(1, CrimeIncident.id))
    ).scalar() or 1
    
    # Get max weighted crime count across all neighborhoods
    all_neighborhoods = db.query(Neighborhood).all()
    max_weighted = 0.0
    
    for nh in all_neighborhoods:
        nh_crimes = db.query(CrimeIncident).filter(
            CrimeIncident.neighborhood_id == nh.id
        ).all()
        
        nh_weighted = 0.0
        for crime in nh_crimes:
            days_ago = (now - crime.date).days
            time_weight = np.exp(-time_decay_factor * days_ago / 365.0)
            severity_weight = severity_weights.get(crime.severity, 1.0)
            nh_weighted += time_weight * severity_weight
        
        max_weighted = max(max_weighted, nh_weighted)
    
    if max_weighted == 0:
        return 1.0
    
    # Inverse normalization: lower crime = higher score
    normalized_score = 1.0 - (weighted_crime_count / max_weighted)
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, normalized_score))


def process_all_crime_scores(db: Session) -> dict:
    """Process crime scores for all neighborhoods"""
    logger.info("Processing crime scores for all neighborhoods")
    
    neighborhoods = db.query(Neighborhood).all()
    scores = {}
    
    for neighborhood in neighborhoods:
        score = calculate_crime_score(neighborhood.id, db)
        scores[neighborhood.id] = score
        logger.debug(f"Neighborhood {neighborhood.name}: crime_score = {score:.3f}")
    
    logger.info(f"Processed crime scores for {len(scores)} neighborhoods")
    return scores

