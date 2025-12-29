import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import BuildingPermit, Neighborhood
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
import logging

logger = logging.getLogger(__name__)

PERMITS_API_URL = "https://data.buffalony.gov/resource/9p2d-f3yt.json"


def get_project_type(permit_type: str, value: float = None) -> str:
    """Categorize permit by project type"""
    permit_lower = (permit_type or "").lower()
    
    commercial_keywords = ['commercial', 'business', 'retail', 'office', 'industrial']
    residential_keywords = ['residential', 'dwelling', 'house', 'apartment', 'multi-family']
    
    if any(keyword in permit_lower for keyword in commercial_keywords):
        return "commercial"
    elif any(keyword in permit_lower for keyword in residential_keywords):
        return "residential"
    elif value and value > 100000:
        return "commercial"  # High value likely commercial
    else:
        return "minor"


def assign_to_neighborhood(lat: float, lon: float, db: Session) -> int:
    """Assign a point to a neighborhood using spatial join"""
    if not lat or not lon:
        return None
    
    point = Point(lon, lat)
    
    neighborhoods = db.query(Neighborhood).all()
    for neighborhood in neighborhoods:
        geom = to_shape(neighborhood.geometry)
        if geom.contains(point):
            return neighborhood.id
    
    return None


def collect_infrastructure_data(db: Session, limit: int = 10000):
    """Collect building permit data from Buffalo Open Data API"""
    logger.info("Starting infrastructure data collection")
    
    try:
        params = {
            '$limit': limit,
            '$order': 'issue_date DESC'
        }
        response = requests.get(PERMITS_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Fetched {len(data)} building permits")
        
        added_count = 0
        skipped_count = 0
        
        for permit in data:
            try:
                permit_id = permit.get('permit_number') or permit.get('id')
                if not permit_id:
                    skipped_count += 1
                    continue
                
                # Check if already exists
                existing = db.query(BuildingPermit).filter(
                    BuildingPermit.permit_id == str(permit_id)
                ).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # Parse date
                date_str = permit.get('issue_date') or permit.get('date')
                if date_str:
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        date = datetime.now()
                else:
                    date = datetime.now()
                
                # Extract fields
                permit_type = permit.get('permit_type') or permit.get('type')
                location = permit.get('location') or permit.get('address')
                status = permit.get('status') or permit.get('permit_status')
                
                # Try to parse value
                value = None
                value_str = permit.get('estimated_cost') or permit.get('value') or permit.get('cost')
                if value_str:
                    try:
                        value = float(str(value_str).replace('$', '').replace(',', ''))
                    except:
                        pass
                
                # Try to get coordinates
                lat = None
                lon = None
                if 'latitude' in permit and 'longitude' in permit:
                    lat = float(permit['latitude'])
                    lon = float(permit['longitude'])
                elif 'location' in permit and isinstance(permit['location'], dict):
                    if 'latitude' in permit['location']:
                        lat = float(permit['location']['latitude'])
                        lon = float(permit['location']['longitude'])
                
                # Assign to neighborhood
                neighborhood_id = None
                if lat and lon:
                    neighborhood_id = assign_to_neighborhood(lat, lon, db)
                
                # Create permit record
                building_permit = BuildingPermit(
                    permit_id=str(permit_id),
                    permit_type=permit_type,
                    location=location,
                    date=date,
                    status=status,
                    value=value,
                    project_type=get_project_type(permit_type, value),
                    latitude=lat,
                    longitude=lon,
                    neighborhood_id=neighborhood_id,
                    raw_data=permit
                )
                
                db.add(building_permit)
                added_count += 1
                
                if added_count % 100 == 0:
                    db.commit()
                    logger.info(f"Processed {added_count} permits...")
            
            except Exception as e:
                logger.error(f"Error processing permit: {e}")
                skipped_count += 1
                continue
        
        db.commit()
        logger.info(f"Infrastructure data collection complete: {added_count} added, {skipped_count} skipped")
        return added_count
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching permit data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in infrastructure collection: {e}")
        db.rollback()
        raise

