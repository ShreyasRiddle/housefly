import json
import requests
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Neighborhood
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
import logging

logger = logging.getLogger(__name__)


def load_neighborhoods_from_geojson(geojson_path: str, db: Session):
    """Load neighborhoods from GeoJSON file into database"""
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    for feature in geojson_data.get('features', []):
        name = feature['properties'].get('name') or feature['properties'].get('NAME') or feature['properties'].get('Neighborhood')
        if not name:
            logger.warning(f"Skipping feature without name: {feature.get('id')}")
            continue
        
        # Check if neighborhood already exists
        existing = db.query(Neighborhood).filter(Neighborhood.name == name).first()
        if existing:
            logger.info(f"Neighborhood {name} already exists, skipping")
            continue
        
        # Convert GeoJSON geometry to PostGIS geometry
        geom = shape(feature['geometry'])
        geom_wkb = from_shape(geom, srid=4326)
        
        neighborhood = Neighborhood(
            name=name,
            geometry=geom_wkb
        )
        db.add(neighborhood)
        logger.info(f"Added neighborhood: {name}")
    
    db.commit()
    logger.info("Finished loading neighborhoods")


def download_neighborhood_shapefile():
    """Download Buffalo neighborhood shapefile from data.buffalony.gov"""
    # This would download the shapefile and convert to GeoJSON
    # For now, we'll create a placeholder script
    # The actual download URL would be: https://data.buffalony.gov/api/geospatial/...
    logger.info("Neighborhood shapefile download not yet implemented")
    logger.info("Please download the shapefile manually from:")
    logger.info("https://data.buffalony.gov")
    logger.info("And convert to GeoJSON format")

