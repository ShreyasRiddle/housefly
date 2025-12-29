from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NeighborhoodBase(BaseModel):
    name: str


class NeighborhoodCreate(NeighborhoodBase):
    geometry: dict  # GeoJSON geometry


class Neighborhood(NeighborhoodBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScoreBase(BaseModel):
    crime_score: float
    infrastructure_score: float
    demographic_score: float
    sentiment_score: float
    profitability_score: float


class Score(ScoreBase):
    id: int
    neighborhood_id: int
    calculated_at: datetime

    class Config:
        from_attributes = True


class ScoreBreakdown(BaseModel):
    neighborhood_id: int
    neighborhood_name: str
    crime_score: float
    infrastructure_score: float
    demographic_score: float
    sentiment_score: float
    profitability_score: float
    calculated_at: datetime


class ScoreProjection(BaseModel):
    neighborhood_id: int
    neighborhood_name: str
    current_score: float
    projection_1yr: float
    projection_3yr: float
    projection_5yr: float
    trend: str  # "up", "down", "stable"


class NeighborhoodWithScores(Neighborhood):
    scores: Optional[Score] = None


class NeighborhoodList(BaseModel):
    neighborhoods: List[NeighborhoodWithScores]


class RefreshStatus(BaseModel):
    status: str
    message: str
    timestamp: datetime

