#!/bin/bash
# Test script to verify Docker deployment

set -e

echo "🧪 Testing AI Education Docker Deployment..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8001"
CONTAINER_NAME="ai_education_app"

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing $description... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $status)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $status, expected $expected_status)"
        return 1
    fi
}

# Check if container is running
echo "1. Checking if container is running..."
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${GREEN}✓${NC} Container is running"
else
    echo -e "${RED}✗${NC} Container is not running"
    echo "Start the container with: docker-compose up -d"
    exit 1
fi

echo ""
echo "2. Testing API endpoints..."
echo ""

# Test endpoints
PASSED=0
FAILED=0

test_endpoint "/" 200 "Root endpoint" && ((PASSED++)) || ((FAILED++))
test_endpoint "/health" 200 "Health check" && ((PASSED++)) || ((FAILED++))
test_endpoint "/docs" 200 "API documentation" && ((PASSED++)) || ((FAILED++))
test_endpoint "/openapi.json" 200 "OpenAPI spec" && ((PASSED++)) || ((FAILED++))

echo ""
echo "3. Testing authentication..."
echo ""

# Test login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓${NC} Authentication working"
    ((PASSED++))
    
    # Extract token
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    # Test authenticated endpoint
    echo ""
    echo "4. Testing authenticated endpoint..."
    AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/lessons/" \
        -H "Authorization: Bearer $TOKEN")
    
    if [ "$AUTH_STATUS" -eq 200 ]; then
        echo -e "${GREEN}✓${NC} Authenticated requests working"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Authenticated requests failing"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Authentication failed"
    ((FAILED++))
fi

echo ""
echo "5. Checking container health..."
echo ""

HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
if [ "$HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✓${NC} Container is healthy"
    ((PASSED++))
elif [ "$HEALTH" = "starting" ]; then
    echo -e "${YELLOW}⚠${NC} Container is still starting"
else
    echo -e "${RED}✗${NC} Container health: $HEALTH"
    ((FAILED++))
fi

echo ""
echo "6. Checking logs for errors..."
echo ""

ERROR_COUNT=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No errors in logs"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Found $ERROR_COUNT error messages in logs"
    echo "Run 'docker logs $CONTAINER_NAME' to view"
fi

# Summary
echo ""
echo "============================================"
echo "Test Summary:"
echo "============================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "============================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Your deployment is working correctly! 🎉"
    echo ""
    echo "Access points:"
    echo "  - API: $BASE_URL"
    echo "  - Docs: $BASE_URL/docs"
    echo "  - Health: $BASE_URL/health"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check logs: docker-compose logs -f"
    echo "  2. Restart: docker-compose restart"
    echo "  3. Rebuild: docker-compose up -d --build"
    exit 1
fi
