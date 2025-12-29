#!/usr/bin/env python3
"""
Script to run the data refresh pipeline manually.
Usage: python scripts/run_refresh.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from data_pipeline.refresh import run_refresh_pipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        run_refresh_pipeline(db)
        logger.info("Refresh pipeline completed successfully!")
    except Exception as e:
        logger.error(f"Error in refresh pipeline: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

