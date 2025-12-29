from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Neighborhood, Score
from ..schemas import Neighborhood as NeighborhoodSchema, NeighborhoodWithScores

router = APIRouter()


@router.get("/neighborhoods", response_model=List[NeighborhoodWithScores])
async def get_neighborhoods(db: Session = Depends(get_db)):
    """Get all 35 Buffalo neighborhoods with their current scores"""
    neighborhoods = db.query(Neighborhood).all()
    result = []
    for neighborhood in neighborhoods:
        # Get latest score
        score = db.query(Score).filter(
            Score.neighborhood_id == neighborhood.id
        ).order_by(Score.calculated_at.desc()).first()
        
        neighborhood_dict = {
            "id": neighborhood.id,
            "name": neighborhood.name,
            "created_at": neighborhood.created_at,
            "scores": score
        }
        result.append(neighborhood_dict)
    return result


@router.get("/neighborhoods/{neighborhood_id}", response_model=NeighborhoodSchema)
async def get_neighborhood(neighborhood_id: int, db: Session = Depends(get_db)):
    """Get a single neighborhood by ID"""
    neighborhood = db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()
    if not neighborhood:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    return neighborhood


@router.get("/neighborhoods/{neighborhood_id}/scores")
async def get_neighborhood_scores(neighborhood_id: int, db: Session = Depends(get_db)):
    """Get current scores for a neighborhood"""
    neighborhood = db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()
    if not neighborhood:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    
    score = db.query(Score).filter(
        Score.neighborhood_id == neighborhood_id
    ).order_by(Score.calculated_at.desc()).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="No scores found for this neighborhood")
    
    return score

