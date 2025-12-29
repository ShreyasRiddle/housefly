from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import RefreshStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/admin/refresh", response_model=RefreshStatus)
async def trigger_refresh(db: Session = Depends(get_db)):
    """Trigger data refresh pipeline (for cron job)"""
    try:
        # Import here to avoid circular imports
        from ...data_pipeline.refresh import run_refresh_pipeline
        
        logger.info("Refresh endpoint triggered")
        run_refresh_pipeline(db)
        
        return RefreshStatus(
            status="success",
            message="Data refresh completed successfully",
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error in refresh: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Refresh failed: {str(e)}"
        )

