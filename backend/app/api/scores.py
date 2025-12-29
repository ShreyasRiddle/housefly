from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Neighborhood, Score, ScoreHistory
from ..schemas import Score as ScoreSchema, ScoreBreakdown, ScoreProjection
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/scores", response_model=List[ScoreSchema])
async def get_all_scores(db: Session = Depends(get_db)):
    """Get all neighborhood scores (latest for each)"""
    neighborhoods = db.query(Neighborhood).all()
    scores = []
    for neighborhood in neighborhoods:
        score = db.query(Score).filter(
            Score.neighborhood_id == neighborhood.id
        ).order_by(Score.calculated_at.desc()).first()
        if score:
            scores.append(score)
    return scores


@router.get("/scores/{neighborhood_id}", response_model=ScoreProjection)
async def get_score_projection(
    neighborhood_id: int,
    years: int = Query(1, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """Get score with time projection (1yr, 3yr, or 5yr)"""
    neighborhood = db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()
    if not neighborhood:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    
    # Get current score
    current_score = db.query(Score).filter(
        Score.neighborhood_id == neighborhood_id
    ).order_by(Score.calculated_at.desc()).first()
    
    if not current_score:
        raise HTTPException(status_code=404, detail="No scores found for this neighborhood")
    
    # Get historical scores for trend analysis
    history = db.query(ScoreHistory).filter(
        ScoreHistory.neighborhood_id == neighborhood_id
    ).order_by(ScoreHistory.calculated_at.asc()).all()
    
    # Calculate projections using linear regression if we have enough history
    if len(history) >= 3:
        # Use historical data for projection
        dates = [(h.calculated_at - history[0].calculated_at).days for h in history]
        scores = [h.profitability_score for h in history]
        
        X = np.array(dates).reshape(-1, 1)
        y = np.array(scores)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Project forward
        days_ahead = {1: 365, 3: 1095, 5: 1825}
        days = days_ahead.get(years, 365)
        projection = model.predict([[days]])[0]
        projection = max(0, min(100, projection))  # Clamp to [0, 100]
        
        # Determine trend
        if len(scores) >= 2:
            recent_trend = scores[-1] - scores[-2]
            if recent_trend > 0.5:
                trend = "up"
            elif recent_trend < -0.5:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "stable"
    else:
        # Not enough history, use current score with small variation
        projection = current_score.profitability_score
        trend = "stable"
    
    return ScoreProjection(
        neighborhood_id=neighborhood_id,
        neighborhood_name=neighborhood.name,
        current_score=current_score.profitability_score,
        projection_1yr=projection if years == 1 else current_score.profitability_score,
        projection_3yr=projection if years == 3 else current_score.profitability_score,
        projection_5yr=projection if years == 5 else current_score.profitability_score,
        trend=trend
    )


@router.get("/scores/breakdown/{neighborhood_id}", response_model=ScoreBreakdown)
async def get_score_breakdown(neighborhood_id: int, db: Session = Depends(get_db)):
    """Get detailed subscore breakdown for a neighborhood"""
    neighborhood = db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()
    if not neighborhood:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    
    score = db.query(Score).filter(
        Score.neighborhood_id == neighborhood_id
    ).order_by(Score.calculated_at.desc()).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="No scores found for this neighborhood")
    
    return ScoreBreakdown(
        neighborhood_id=neighborhood_id,
        neighborhood_name=neighborhood.name,
        crime_score=score.crime_score,
        infrastructure_score=score.infrastructure_score,
        demographic_score=score.demographic_score,
        sentiment_score=score.sentiment_score,
        profitability_score=score.profitability_score,
        calculated_at=score.calculated_at
    )

