#!/usr/bin/env python3
"""
Script to load Buffalo neighborhood GeoJSON data into the database.
Usage: python scripts/load_neighborhoods.py <path_to_geojson_file>
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from data_pipeline.utils.geojson_loader import load_neighborhoods_from_geojson
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python scripts/load_neighborhoods.py <path_to_geojson_file>")
        sys.exit(1)
    
    geojson_path = sys.argv[1]
    if not os.path.exists(geojson_path):
        logger.error(f"GeoJSON file not found: {geojson_path}")
        sys.exit(1)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        load_neighborhoods_from_geojson(geojson_path, db)
        logger.info("Neighborhoods loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading neighborhoods: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

