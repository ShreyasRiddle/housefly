import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import CrimeIncident, Neighborhood
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from shapely.ops import transform
import pyproj
import logging

logger = logging.getLogger(__name__)

CRIME_API_URL = "https://data.buffalony.gov/resource/d6g9-xbgu.json"


def get_severity(offense_type: str) -> str:
    """Categorize offense by severity"""
    offense_lower = (offense_type or "").lower()
    
    violent_keywords = ['assault', 'homicide', 'murder', 'robbery', 'rape', 'weapon', 'shooting', 'stabbing']
    property_keywords = ['burglary', 'theft', 'larceny', 'vandalism', 'arson', 'auto']
    
    if any(keyword in offense_lower for keyword in violent_keywords):
        return "violent"
    elif any(keyword in offense_lower for keyword in property_keywords):
        return "property"
    else:
        return "other"


def assign_to_neighborhood(lat: float, lon: float, db: Session) -> int:
    """Assign a point to a neighborhood using spatial join"""
    if not lat or not lon:
        return None
    
    point = Point(lon, lat)  # Note: shapely uses (lon, lat)
    
    neighborhoods = db.query(Neighborhood).all()
    for neighborhood in neighborhoods:
        geom = to_shape(neighborhood.geometry)
        if geom.contains(point):
            return neighborhood.id
    
    return None


def collect_crime_data(db: Session, limit: int = 10000):
    """Collect crime data from Buffalo Open Data API"""
    logger.info("Starting crime data collection")
    
    try:
        # Fetch data from API
        params = {
            '$limit': limit,
            '$order': 'incident_datetime DESC'
        }
        response = requests.get(CRIME_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Fetched {len(data)} crime incidents")
        
        added_count = 0
        skipped_count = 0
        
        for incident in data:
            try:
                # Extract fields
                incident_id = incident.get('incident_number') or incident.get('id')
                if not incident_id:
                    skipped_count += 1
                    continue
                
                # Check if already exists
                existing = db.query(CrimeIncident).filter(
                    CrimeIncident.incident_id == str(incident_id)
                ).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # Parse date
                date_str = incident.get('incident_datetime') or incident.get('date')
                if date_str:
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        date = datetime.now()
                else:
                    date = datetime.now()
                
                # Extract location
                location = incident.get('location') or incident.get('address')
                offense_type = incident.get('offense_type') or incident.get('offense')
                
                # Try to get coordinates
                lat = None
                lon = None
                if 'latitude' in incident and 'longitude' in incident:
                    lat = float(incident['latitude'])
                    lon = float(incident['longitude'])
                elif 'location' in incident and isinstance(incident['location'], dict):
                    if 'latitude' in incident['location']:
                        lat = float(incident['location']['latitude'])
                        lon = float(incident['location']['longitude'])
                
                # Assign to neighborhood
                neighborhood_id = None
                if lat and lon:
                    neighborhood_id = assign_to_neighborhood(lat, lon, db)
                
                # Create incident record
                crime_incident = CrimeIncident(
                    incident_id=str(incident_id),
                    date=date,
                    location=location,
                    offense_type=offense_type,
                    severity=get_severity(offense_type),
                    latitude=lat,
                    longitude=lon,
                    neighborhood_id=neighborhood_id,
                    raw_data=incident
                )
                
                db.add(crime_incident)
                added_count += 1
                
                if added_count % 100 == 0:
                    db.commit()
                    logger.info(f"Processed {added_count} incidents...")
            
            except Exception as e:
                logger.error(f"Error processing incident: {e}")
                skipped_count += 1
                continue
        
        db.commit()
        logger.info(f"Crime data collection complete: {added_count} added, {skipped_count} skipped")
        return added_count
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching crime data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in crime collection: {e}")
        db.rollback()
        raise

