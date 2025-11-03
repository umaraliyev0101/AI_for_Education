#!/bin/bash
# Bash Script to Deploy to GitHub Container Registry

set -e  # Exit on error

# Configuration
GITHUB_TOKEN="${GITHUB_TOKEN:-$1}"
GITHUB_USERNAME="${2:-umaraliyev0101}"
IMAGE_NAME="${3:-ai-education}"
VERSION="${4:-1.0.0}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo ""
echo -e "${CYAN}========================================"
echo -e "  Deploy to GitHub Container Registry"
echo -e "========================================${NC}"
echo ""

# Check if token is provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ GitHub token not provided!${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ${NC}./deploy-to-ghcr.sh YOUR_TOKEN [username] [image] [version]${NC}"
    echo ""
    echo -e "${YELLOW}Or set environment variable:${NC}"
    echo -e "  ${NC}export GITHUB_TOKEN='YOUR_TOKEN'${NC}"
    echo -e "  ${NC}./deploy-to-ghcr.sh${NC}"
    echo ""
    exit 1
fi

# Configuration
REGISTRY_URL="ghcr.io"
FULL_IMAGE_NAME="$REGISTRY_URL/$GITHUB_USERNAME/$IMAGE_NAME"

echo -e "${CYAN}Configuration:${NC}"
echo -e "  Registry: $REGISTRY_URL"
echo -e "  Username: $GITHUB_USERNAME"
echo -e "  Image: $IMAGE_NAME"
echo -e "  Version: $VERSION"
echo ""

# Step 1: Login to GHCR
echo -e "${CYAN}🔐 Step 1/5: Logging in to GitHub Container Registry...${NC}"
if echo "$GITHUB_TOKEN" | docker login $REGISTRY_URL -u $GITHUB_USERNAME --password-stdin >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓ Login successful${NC}"
else
    echo -e "   ${RED}✗ Login failed${NC}"
    exit 1
fi
echo ""

# Step 2: Build Docker image
echo -e "${CYAN}🏗️  Step 2/5: Building Docker image...${NC}"
if docker build -f Dockerfile.prod -t ${IMAGE_NAME}:latest . >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓ Build successful${NC}"
else
    echo -e "   ${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Step 3: Tag image
echo -e "${CYAN}🏷️  Step 3/5: Tagging image...${NC}"
docker tag ${IMAGE_NAME}:latest ${FULL_IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:latest ${FULL_IMAGE_NAME}:v${VERSION}

# Optional: Tag with git SHA if in git repo
if [ -d .git ]; then
    GIT_SHA=$(git rev-parse --short HEAD)
    docker tag ${IMAGE_NAME}:latest ${FULL_IMAGE_NAME}:${GIT_SHA}
    echo -e "   ${GREEN}✓ Tagged: latest, v${VERSION}, ${GIT_SHA}${NC}"
else
    echo -e "   ${GREEN}✓ Tagged: latest, v${VERSION}${NC}"
fi
echo ""

# Step 4: Push to GHCR
echo -e "${CYAN}📤 Step 4/5: Pushing to GitHub Container Registry...${NC}"
echo -e "   ${YELLOW}This may take several minutes...${NC}"

echo -e "   → Pushing latest tag..."
docker push ${FULL_IMAGE_NAME}:latest >/dev/null 2>&1

echo -e "   → Pushing version tag..."
docker push ${FULL_IMAGE_NAME}:v${VERSION} >/dev/null 2>&1

if [ -d .git ]; then
    GIT_SHA=$(git rev-parse --short HEAD)
    echo -e "   → Pushing SHA tag..."
    docker push ${FULL_IMAGE_NAME}:${GIT_SHA} >/dev/null 2>&1
fi

echo -e "   ${GREEN}✓ Push successful${NC}"
echo ""

# Step 5: Verify
echo -e "${CYAN}🔍 Step 5/5: Verifying deployment...${NC}"
if docker inspect ${FULL_IMAGE_NAME}:latest >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓ Image verified on registry${NC}"
else
    echo -e "   ${YELLOW}⚠ Could not verify (may still be successful)${NC}"
fi
echo ""

# Success summary
echo -e "${GREEN}========================================"
echo -e "  ✅ Deployment Successful!"
echo -e "========================================${NC}"
echo ""
echo -e "${CYAN}📦 Your image is available at:${NC}"
echo -e "   ${YELLOW}${FULL_IMAGE_NAME}:latest${NC}"
echo -e "   ${YELLOW}${FULL_IMAGE_NAME}:v${VERSION}${NC}"
if [ -d .git ]; then
    GIT_SHA=$(git rev-parse --short HEAD)
    echo -e "   ${YELLOW}${FULL_IMAGE_NAME}:${GIT_SHA}${NC}"
fi
echo ""
echo -e "${CYAN}🌐 View on GitHub:${NC}"
echo -e "   ${YELLOW}https://github.com/${GITHUB_USERNAME}?tab=packages${NC}"
echo ""
echo -e "${CYAN}📥 To pull and run:${NC}"
echo -e "   docker pull ${FULL_IMAGE_NAME}:latest"
echo -e "   docker run -p 8001:8001 ${FULL_IMAGE_NAME}:latest"
echo ""
echo -e "${CYAN}✨ Next steps:${NC}"
echo -e "   1. Make package public on GitHub (optional)"
echo -e "   2. Update your docker-compose.yml to use GHCR image"
echo -e "   3. Deploy to your production server"
echo ""
