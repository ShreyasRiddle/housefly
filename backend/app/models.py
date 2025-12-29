from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Neighborhood(Base):
    __tablename__ = "neighborhoods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    geometry = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scores = relationship("Score", back_populates="neighborhood")
    score_history = relationship("ScoreHistory", back_populates="neighborhood")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), nullable=False)
    crime_score = Column(Float, nullable=False)
    infrastructure_score = Column(Float, nullable=False)
    demographic_score = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    profitability_score = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    neighborhood = relationship("Neighborhood", back_populates="scores")


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id = Column(Integer, primary_key=True, index=True)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), nullable=False)
    crime_score = Column(Float, nullable=False)
    infrastructure_score = Column(Float, nullable=False)
    demographic_score = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    profitability_score = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    neighborhood = relationship("Neighborhood", back_populates="score_history")


class CrimeIncident(Base):
    __tablename__ = "crime_incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True)
    date = Column(DateTime, nullable=False)
    location = Column(String)
    offense_type = Column(String)
    severity = Column(String)  # violent, property, other
    latitude = Column(Float)
    longitude = Column(Float)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"))
    raw_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


class BuildingPermit(Base):
    __tablename__ = "building_permits"

    id = Column(Integer, primary_key=True, index=True)
    permit_id = Column(String, unique=True, index=True)
    permit_type = Column(String)
    location = Column(String)
    date = Column(DateTime)
    status = Column(String)
    value = Column(Float)
    project_type = Column(String)  # commercial, residential, minor
    latitude = Column(Float)
    longitude = Column(Float)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"))
    raw_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


class DemographicsProfile(Base):
    __tablename__ = "demographics_profiles"

    id = Column(Integer, primary_key=True, index=True)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), unique=True)
    income_median = Column(Float)
    age_median = Column(Float)
    household_size_avg = Column(Float)
    population = Column(Integer)
    raw_data = Column(JSONB)
    updated_at = Column(DateTime, default=datetime.utcnow)


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String, unique=True, index=True)
    title = Column(String)
    content = Column(Text)
    published_at = Column(DateTime)
    source = Column(String)
    url = Column(String)
    sentiment_score = Column(Float)  # VADER compound score
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), nullable=True)
    raw_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

