# Housefly: Buffalo Profitability Scoring Engine

A resume-quality real estate web application that displays profitability scores for each of Buffalo's 35 official planning neighborhoods. The score is generated from real-world public datasets using a weighted algorithm incorporating crime, infrastructure, demographics, and sentiment.

## Features

- **Interactive Map**: Leaflet-based map showing all 35 Buffalo neighborhoods
- **Color-Coded Scores**: Neighborhoods are color-coded by profitability score (0-100)
- **Time Projections**: View 1-year, 3-year, and 5-year profitability projections
- **Score Breakdown**: Detailed breakdown of 4 subscores (crime, infrastructure, demographics, sentiment)
- **Data-Driven**: Uses only free and open-access data sources

## Tech Stack

- **Frontend**: React + TypeScript + Vite + Leaflet
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL with PostGIS
- **Data Processing**: Pandas, NumPy, scikit-learn
- **Sentiment Analysis**: VADER

## Project Structure

```
housefly/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── data_pipeline/   # Data collection and processing
│   ├── scripts/         # Utility scripts
│   └── alembic/         # Database migrations
├── frontend/            # React frontend
└── data/                # GeoJSON and data files
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+ with PostGIS extension
- GNews API key (optional, for sentiment analysis)

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database URL and GNews API key
```

4. Set up PostgreSQL database:
```bash
createdb housefly
psql housefly -c "CREATE EXTENSION postgis;"
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Load neighborhood data:
```bash
# First, download neighborhood shapefile from data.buffalony.gov
# Convert to GeoJSON, then:
python3 scripts/load_neighborhoods.py data/neighborhoods.geojson
```

7. Run initial data refresh:
```bash
python3 scripts/run_refresh.py
```

8. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables (optional):
```bash
# Create .env file if needed
VITE_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Data Sources

- **Crime Data**: Buffalo Open Data - Crime Incidents
- **Infrastructure**: Buffalo Open Data - Building Permits
- **Demographics**: Buffalo Open Data - Neighborhood Profiles
- **Sentiment**: GNews API (free tier)

## Score Calculation

The profitability score is calculated using a weighted formula:

```
profitabilityScore = 
  crimeWeight * crimeScore +
  infrastructureWeight * infrastructureScore +
  demographicWeight * demographicScore +
  sentimentWeight * sentimentScore
```

All subscores are normalized to [0, 1] before applying weights. Default weights are equal (0.25 each) and can be adjusted in `backend/config/weights.yaml`.

## Automated Data Refresh

Set up a daily cron job to refresh data:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed):
0 2 * * * /path/to/housefly/backend/cron_refresh.sh
```

Or use the API endpoint:
```bash
curl -X POST http://localhost:8000/api/admin/refresh
```

## API Endpoints

- `GET /api/neighborhoods` - List all neighborhoods
- `GET /api/neighborhoods/{id}` - Get neighborhood details
- `GET /api/neighborhoods/{id}/scores` - Get current scores
- `GET /api/scores` - Get all scores
- `GET /api/scores/{id}?years={1|3|5}` - Get score projection
- `GET /api/scores/breakdown/{id}` - Get score breakdown
- `POST /api/admin/refresh` - Trigger data refresh

## Development

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## License

MIT

## Contributing

This is a portfolio project. Contributions and suggestions are welcome!
