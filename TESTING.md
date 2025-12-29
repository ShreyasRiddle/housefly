# Testing Guide

This guide will help you test the Housefly application step by step.

## Prerequisites Check

Before testing, ensure you have:
- [ ] Python 3.9+ installed
- [ ] PostgreSQL 12+ installed with PostGIS extension
- [ ] Node.js 18+ installed (for frontend testing)
- [ ] GNews API key (optional, for sentiment data)

## Step 1: Backend Setup

### 1.1 Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cat > .env << EOF
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/housefly
GNEWS_API_KEY=your_key_here_optional
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
EOF
```

**Important**: Replace `your_user`, `your_password` with your PostgreSQL credentials.

### 1.4 Set Up Database

```bash
# Create database
createdb housefly

# Enable PostGIS extension
psql housefly -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 1.5 Run Database Migrations

```bash
cd backend
alembic upgrade head
```

If this is the first time, you may need to create an initial migration:

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Step 2: Basic API Test (Without Data)

Even without neighborhood data, we can test the API server:

### 2.1 Start the Backend Server

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2.2 Test Health Endpoint

In another terminal:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### 2.3 Test Root Endpoint

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"message":"Housefly API","version":"1.0.0"}
```

### 2.4 Test API Documentation

Open in browser: http://localhost:8000/docs

You should see the FastAPI interactive documentation.

## Step 3: Test with Sample Data

### 3.1 Create a Test Neighborhood (Optional)

If you want to test without the full GeoJSON file, you can manually insert a test neighborhood:

```bash
psql housefly
```

Then in psql:

```sql
-- Insert a test neighborhood (simplified geometry)
INSERT INTO neighborhoods (name, geometry, created_at)
VALUES (
  'Test Neighborhood',
  ST_GeomFromText('POLYGON((-78.9 42.88, -78.85 42.88, -78.85 42.92, -78.9 42.92, -78.9 42.88))', 4326),
  NOW()
);
```

### 3.2 Test Neighborhood Endpoint

```bash
curl http://localhost:8000/api/neighborhoods
```

## Step 4: Frontend Testing

### 4.1 Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4.2 Start Frontend Dev Server

```bash
npm run dev
```

The frontend should be available at http://localhost:5173

### 4.3 Test Frontend

- Open http://localhost:5173 in your browser
- You should see the map interface (may be empty without neighborhood data)

## Step 5: Full Data Pipeline Test

### 5.1 Load Neighborhood Data

First, you'll need to obtain the Buffalo neighborhood GeoJSON file from:
https://data.buffalony.gov

Once you have the GeoJSON file:

```bash
cd backend
source venv/bin/activate
python3 scripts/load_neighborhoods.py /path/to/neighborhoods.geojson
```

### 5.2 Run Data Refresh

```bash
python3 scripts/run_refresh.py
```

This will:
- Collect crime data
- Collect infrastructure/permits data
- Collect demographics data
- Collect sentiment data (if API key is set)
- Calculate scores for all neighborhoods

### 5.3 Test Refresh Endpoint

```bash
curl -X POST http://localhost:8000/api/admin/refresh
```

## Troubleshooting

### Database Connection Issues

If you get connection errors:
1. Check PostgreSQL is running: `pg_isready`
2. Verify DATABASE_URL in `.env` file
3. Check PostgreSQL user permissions

### Import Errors

If you get import errors:
1. Make sure virtual environment is activated
2. Verify all dependencies are installed: `pip list`
3. Check you're in the correct directory

### Missing GeoJSON

The app will work without neighborhood data, but the map will be empty. You can still test API endpoints.

### GNews API Issues

If GNews API key is not set or quota is exceeded, sentiment collection will use fallback data (neutral scores).

## Quick Test Script

Here's a quick test to verify everything works:

```bash
#!/bin/bash
# Quick test script

echo "Testing Housefly API..."

# Test health
echo "1. Testing health endpoint..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✓ Health check passed" || echo "✗ Health check failed"

# Test neighborhoods
echo "2. Testing neighborhoods endpoint..."
curl -s http://localhost:8000/api/neighborhoods | grep -q "neighborhoods" && echo "✓ Neighborhoods endpoint works" || echo "✗ Neighborhoods endpoint failed"

# Test scores
echo "3. Testing scores endpoint..."
curl -s http://localhost:8000/api/scores | grep -q "\[\]" && echo "✓ Scores endpoint works (empty is OK)" || echo "✗ Scores endpoint failed"

echo "Testing complete!"
```

Save as `test_api.sh`, make executable (`chmod +x test_api.sh`), and run when the server is up.

