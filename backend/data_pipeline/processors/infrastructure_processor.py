import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import BuildingPermit, Neighborhood
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def calculate_infrastructure_score(neighborhood_id: int, db: Session) -> float:
    """Calculate infrastructure score for a neighborhood (0-1, higher = better)"""
    # Get all permits for this neighborhood
    permits = db.query(BuildingPermit).filter(
        BuildingPermit.neighborhood_id == neighborhood_id
    ).all()
    
    if not permits:
        # No permits = lower score (no development activity)
        return 0.3
    
    # Project type weights
    type_weights = {
        'commercial': 3.0,
        'residential': 2.0,
        'minor': 1.0
    }
    
    # Time decay: recent permits weighted higher
    now = datetime.now()
    time_decay_factor = 0.1
    
    weighted_value = 0.0
    
    for permit in permits:
        # Time decay
        days_ago = (now - permit.date).days if permit.date else 365
        time_weight = np.exp(-time_decay_factor * days_ago / 365.0)
        
        # Type weight
        type_weight = type_weights.get(permit.project_type, 1.0)
        
        # Value weight (normalize by $100k)
        value_weight = (permit.value or 50000) / 100000.0
        
        # Combined weight
        weight = time_weight * type_weight * (1.0 + value_weight)
        weighted_value += weight
    
    # Normalize: compare to max across all neighborhoods
    all_neighborhoods = db.query(Neighborhood).all()
    max_weighted = 0.0
    
    for nh in all_neighborhoods:
        nh_permits = db.query(BuildingPermit).filter(
            BuildingPermit.neighborhood_id == nh.id
        ).all()
        
        nh_weighted = 0.0
        for permit in nh_permits:
            days_ago = (now - permit.date).days if permit.date else 365
            time_weight = np.exp(-time_decay_factor * days_ago / 365.0)
            type_weight = type_weights.get(permit.project_type, 1.0)
            value_weight = (permit.value or 50000) / 100000.0
            nh_weighted += time_weight * type_weight * (1.0 + value_weight)
        
        max_weighted = max(max_weighted, nh_weighted)
    
    if max_weighted == 0:
        return 0.5
    
    # Normalize to [0, 1]
    normalized_score = weighted_value / max_weighted
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, normalized_score))


def process_all_infrastructure_scores(db: Session) -> dict:
    """Process infrastructure scores for all neighborhoods"""
    logger.info("Processing infrastructure scores for all neighborhoods")
    
    neighborhoods = db.query(Neighborhood).all()
    scores = {}
    
    for neighborhood in neighborhoods:
        score = calculate_infrastructure_score(neighborhood.id, db)
        scores[neighborhood.id] = score
        logger.debug(f"Neighborhood {neighborhood.name}: infrastructure_score = {score:.3f}")
    
    logger.info(f"Processed infrastructure scores for {len(scores)} neighborhoods")
    return scores

