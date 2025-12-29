#!/bin/bash
# Quick API test script for Housefly

echo "=========================================="
echo "Housefly API Test Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"

# Test 1: Health check
echo "1. Testing health endpoint..."
if curl -s -f "${API_URL}/health" > /dev/null; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    curl -s "${API_URL}/health" | python3 -m json.tool
else
    echo -e "${RED}✗ Health check failed - Is the server running?${NC}"
    echo "   Start server with: cd backend && uvicorn app.main:app --reload"
    exit 1
fi
echo ""

# Test 2: Root endpoint
echo "2. Testing root endpoint..."
if curl -s -f "${API_URL}/" > /dev/null; then
    echo -e "${GREEN}✓ Root endpoint works${NC}"
    curl -s "${API_URL}/" | python3 -m json.tool
else
    echo -e "${RED}✗ Root endpoint failed${NC}"
fi
echo ""

# Test 3: Neighborhoods endpoint
echo "3. Testing neighborhoods endpoint..."
RESPONSE=$(curl -s "${API_URL}/api/neighborhoods")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Neighborhoods endpoint accessible${NC}"
    COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('neighborhoods', [])))" 2>/dev/null || echo "0")
    if [ "$COUNT" = "0" ]; then
        echo -e "${YELLOW}  ⚠ No neighborhoods found (this is OK if data hasn't been loaded)${NC}"
    else
        echo -e "${GREEN}  Found $COUNT neighborhoods${NC}"
    fi
else
    echo -e "${RED}✗ Neighborhoods endpoint failed${NC}"
fi
echo ""

# Test 4: Scores endpoint
echo "4. Testing scores endpoint..."
if curl -s -f "${API_URL}/api/scores" > /dev/null; then
    echo -e "${GREEN}✓ Scores endpoint works${NC}"
    SCORE_COUNT=$(curl -s "${API_URL}/api/scores" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "  Found $SCORE_COUNT scores"
else
    echo -e "${RED}✗ Scores endpoint failed${NC}"
fi
echo ""

# Test 5: API Documentation
echo "5. Testing API documentation..."
if curl -s -f "${API_URL}/docs" > /dev/null; then
    echo -e "${GREEN}✓ API docs available at ${API_URL}/docs${NC}"
else
    echo -e "${RED}✗ API docs not accessible${NC}"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "API Base URL: ${API_URL}"
echo "API Docs: ${API_URL}/docs"
echo ""
echo "If all tests passed, your backend is working!"
echo "Next steps:"
echo "  1. Load neighborhood data (see TESTING.md)"
echo "  2. Run data refresh: python backend/scripts/run_refresh.py"
echo "  3. Start frontend: cd frontend && npm run dev"

