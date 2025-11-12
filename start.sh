#!/bin/bash
# ============================================================================
# Start Script for AI Education Platform
# ============================================================================
# Supports both development and production modes

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}AI Education Platform${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Determine mode (development or production)
MODE="${MODE:-development}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo -e "${YELLOW}  Please run setup-unix.sh first${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo -e "${YELLOW}  Please run setup-unix.sh first${NC}"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check if database exists
if [ ! -f "ai_education.db" ]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    python -m backend.init_db
fi

echo ""

# Start based on mode
if [ "$MODE" = "production" ]; then
    echo -e "${GREEN}Starting in PRODUCTION mode...${NC}"
    
    # Determine number of workers
    if [ -n "$GUNICORN_WORKERS" ]; then
        WORKERS=$GUNICORN_WORKERS
    else
        # Auto-detect CPU cores
        WORKERS=$(python -c "import os; print((os.cpu_count() or 1) * 2 + 1)")
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    echo -e "${GREEN}Starting with $WORKERS workers on port ${PORT:-8001}${NC}"
    echo ""
    
    exec gunicorn backend.main:app \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:${PORT:-8001} \
        --timeout 300 \
        --keepalive 5 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info \
        --capture-output
else
    echo -e "${GREEN}Starting in DEVELOPMENT mode...${NC}"
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${GREEN}Server starting...${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Access the API at:${NC}"
    echo -e "  - API: ${GREEN}http://localhost:8001${NC}"
    echo -e "  - Docs: ${GREEN}http://localhost:8001/docs${NC}"
    echo -e "  - OpenAPI: ${GREEN}http://localhost:8001/openapi.json${NC}"
    echo ""
    echo -e "${YELLOW}Default credentials:${NC}"
    echo -e "  Username: ${GREEN}admin${NC}"
    echo -e "  Password: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    exec uvicorn backend.main:app \
        --host 0.0.0.0 \
        --port ${PORT:-8001} \
        --reload \
        --log-level info
fi
