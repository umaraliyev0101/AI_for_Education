#!/bin/bash
# ============================================================================
# Linux/Mac Setup Script for AI Education Platform
# ============================================================================

set -e  # Exit on error

echo "========================================"
echo "AI Education Platform - Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found! Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Found Python ${PYTHON_VERSION}${NC}"

# Check Python version
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    echo -e "${RED}✗ Python 3.11 or higher is required!${NC}"
    exit 1
fi

echo ""

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}Virtual environment already exists. Skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip --quiet
echo -e "${GREEN}✓ Pip upgraded${NC}"

echo ""

# Install requirements
echo -e "${YELLOW}Installing dependencies (this may take a few minutes)...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed successfully${NC}"

echo ""

# Check if .env exists
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    
    # Generate a secure secret key
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
    else
        SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    fi
    
    # Update .env file (works on both Linux and Mac)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=your-secret-key-change-in-production.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=your-secret-key-change-in-production.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}✓ .env file created with secure secret key${NC}"
    echo -e "  You can edit .env to customize settings"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p uploads/faces
mkdir -p uploads/materials
mkdir -p uploads/presentations
mkdir -p uploads/audio
mkdir -p uploads/slides
mkdir -p uploads/audio/presentations
mkdir -p vector_stores/lesson_materials
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

echo ""

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python -m backend.init_db
echo -e "${GREEN}✓ Database initialized successfully${NC}"

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Default credentials:${NC}"
echo -e "  Username: ${GREEN}admin${NC}"
echo -e "  Password: ${GREEN}admin123${NC}"
echo ""
echo -e "${YELLOW}To start the server, run:${NC}"
echo -e "  ${GREEN}./start.sh${NC}"
echo ""
echo -e "${YELLOW}Or manually:${NC}"
echo -e "  ${GREEN}source venv/bin/activate${NC}"
echo -e "  ${GREEN}uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload${NC}"
echo ""
echo -e "${CYAN}Access the API at: http://localhost:8001${NC}"
echo -e "${CYAN}API Documentation: http://localhost:8001/docs${NC}"
echo ""
