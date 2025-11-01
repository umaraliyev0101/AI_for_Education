# 📦 Deploy to GitHub Container Registry (GHCR)

Complete guide to publish your AI Education Platform Docker image to GitHub Container Registry.

---

## 📋 Prerequisites

1. **GitHub Account** with repository access
2. **Docker** installed locally
3. **GitHub Personal Access Token** (PAT) with `write:packages` permission
4. **Git** configured with your GitHub account

---

## 🔑 Step 1: Create GitHub Personal Access Token

### Option A: Via GitHub Website

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `GHCR_TOKEN` or `Docker Registry Access`
4. Select scopes:
   - ✅ `write:packages` (Upload packages)
   - ✅ `read:packages` (Download packages)
   - ✅ `delete:packages` (Delete packages) - optional
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

### Option B: Via GitHub CLI

```bash
gh auth login
gh auth token
```

---

## 🔐 Step 2: Login to GitHub Container Registry

### Windows (PowerShell)
```powershell
# Set your token as environment variable
$env:CR_PAT="your_github_token_here"

# Login to GHCR
echo $env:CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### Linux/Mac (Bash)
```bash
# Set your token as environment variable
export CR_PAT=your_github_token_here

# Login to GHCR
echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### Direct Login (All Platforms)
```bash
docker login ghcr.io -u YOUR_GITHUB_USERNAME -p YOUR_GITHUB_TOKEN
```

**Expected Output:**
```
Login Succeeded
```

---

## 🏗️ Step 3: Build Docker Image

### Build Production Image
```bash
# Navigate to project directory
cd D:\Projects\AI_in_Education

# Build the image
docker build -f Dockerfile.prod -t ai-education:latest .
```

### Verify Build
```bash
docker images | grep ai-education
```

---

## 🏷️ Step 4: Tag Image for GHCR

### Tag Format
```
ghcr.io/OWNER/IMAGE_NAME:TAG
```

### Tag Your Image
```bash
# Replace with your GitHub username
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:latest

# Optional: Tag with version
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:v1.0.0

# Optional: Tag with SHA
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:$(git rev-parse --short HEAD)
```

### Verify Tags
```bash
docker images | grep ghcr.io
```

---

## 📤 Step 5: Push to GitHub Container Registry

### Push Latest Tag
```bash
docker push ghcr.io/umaraliyev0101/ai-education:latest
```

### Push All Tags
```bash
docker push ghcr.io/umaraliyev0101/ai-education:v1.0.0
docker push ghcr.io/umaraliyev0101/ai-education:latest
```

### Push Output
```
The push refers to repository [ghcr.io/umaraliyev0101/ai-education]
5f70bf18a086: Pushed
...
latest: digest: sha256:abc123... size: 4321
```

---

## 🔓 Step 6: Make Package Public (Optional)

1. Go to your GitHub profile → **Packages**
2. Click on **ai-education** package
3. Click **"Package settings"**
4. Scroll to **"Danger Zone"**
5. Click **"Change visibility"** → **"Public"**

---

## 📥 Step 7: Pull and Use Image

### Pull from GHCR
```bash
docker pull ghcr.io/umaraliyev0101/ai-education:latest
```

### Run from GHCR
```bash
docker run -d \
  --name ai-education \
  -p 8001:8001 \
  -e SECRET_KEY=your-secret-key \
  ghcr.io/umaraliyev0101/ai-education:latest
```

### Update docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    image: ghcr.io/umaraliyev0101/ai-education:latest
    # Remove build section
    ports:
      - "8001:8001"
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./vector_stores:/app/vector_stores
```

---

## 🤖 Step 8: Automate with GitHub Actions

### Update `.github/workflows/docker-build.yml`

The file is already created! Just add your GitHub secrets:

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add secrets:
   - Name: `GITHUB_TOKEN` (already exists)
   - The workflow will use it automatically

### Trigger Workflow

```bash
# Push to main branch
git add .
git commit -m "Deploy to GHCR"
git push origin main
```

### Or Create Release Tag
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

The GitHub Actions workflow will automatically:
- Build the Docker image
- Push to GHCR
- Tag with version/branch/sha

---

## 📝 Complete Example

### Full Deployment Script (PowerShell)

```powershell
# Configuration
$GITHUB_USERNAME = "umaraliyev0101"
$GITHUB_TOKEN = "your_github_token_here"
$IMAGE_NAME = "ai-education"
$VERSION = "1.0.0"

# Login to GHCR
Write-Host "🔐 Logging in to GitHub Container Registry..." -ForegroundColor Cyan
$env:CR_PAT = $GITHUB_TOKEN
echo $env:CR_PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Login failed" -ForegroundColor Red
    exit 1
}

# Build image
Write-Host "🏗️ Building Docker image..." -ForegroundColor Cyan
docker build -f Dockerfile.prod -t ${IMAGE_NAME}:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

# Tag image
Write-Host "🏷️ Tagging image..." -ForegroundColor Cyan
docker tag ${IMAGE_NAME}:latest ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:latest ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:v${VERSION}

# Push image
Write-Host "📤 Pushing to GHCR..." -ForegroundColor Cyan
docker push ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker push ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:v${VERSION}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully published to GHCR!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Image available at:" -ForegroundColor Yellow
    Write-Host "  ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest" -ForegroundColor White
    Write-Host "  ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:v${VERSION}" -ForegroundColor White
} else {
    Write-Host "❌ Push failed" -ForegroundColor Red
    exit 1
}
```

Save as `deploy-to-ghcr.ps1` and run:
```powershell
.\deploy-to-ghcr.ps1
```

### Full Deployment Script (Bash)

```bash
#!/bin/bash
set -e

# Configuration
GITHUB_USERNAME="umaraliyev0101"
GITHUB_TOKEN="your_github_token_here"
IMAGE_NAME="ai-education"
VERSION="1.0.0"

echo "🔐 Logging in to GitHub Container Registry..."
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

echo "🏗️ Building Docker image..."
docker build -f Dockerfile.prod -t ${IMAGE_NAME}:latest .

echo "🏷️ Tagging image..."
docker tag ${IMAGE_NAME}:latest ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:latest ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:v${VERSION}

echo "📤 Pushing to GHCR..."
docker push ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker push ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:v${VERSION}

echo "✅ Successfully published to GHCR!"
echo ""
echo "Image available at:"
echo "  ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest"
echo "  ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:v${VERSION}"
```

Save as `deploy-to-ghcr.sh` and run:
```bash
chmod +x deploy-to-ghcr.sh
./deploy-to-ghcr.sh
```

---

## 🌐 Step 9: Deploy from GHCR

### On Any Server

```bash
# Login (if private)
docker login ghcr.io -u umaraliyev0101 -p YOUR_TOKEN

# Pull and run
docker pull ghcr.io/umaraliyev0101/ai-education:latest
docker run -d \
  --name ai-education \
  -p 8001:8001 \
  -e SECRET_KEY=your-secret-key \
  -v $(pwd)/uploads:/app/uploads \
  ghcr.io/umaraliyev0101/ai-education:latest
```

### With Docker Compose

Create `docker-compose.ghcr.yml`:
```yaml
version: '3.8'

services:
  app:
    image: ghcr.io/umaraliyev0101/ai-education:latest
    container_name: ai_education_app
    ports:
      - "8001:8001"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite:///./ai_education.db
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    volumes:
      - ./uploads:/app/uploads
      - ./vector_stores:/app/vector_stores
      - ./ai_education.db:/app/ai_education.db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: ai_education_nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    restart: unless-stopped
```

Run:
```bash
docker-compose -f docker-compose.ghcr.yml up -d
```

---

## 🔍 Verify Deployment

### Check Package on GitHub
1. Go to: https://github.com/umaraliyev0101?tab=packages
2. You should see **ai-education** package

### Pull and Test
```bash
docker pull ghcr.io/umaraliyev0101/ai-education:latest
docker run --rm ghcr.io/umaraliyev0101/ai-education:latest python --version
```

### Check Image Info
```bash
docker inspect ghcr.io/umaraliyev0101/ai-education:latest
```

---

## 📊 Image Variants

### Tag Multiple Versions
```bash
# Latest
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:latest

# Semantic version
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:1.0.0
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:1.0
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:1

# Git SHA
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:$(git rev-parse --short HEAD)

# Date
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:$(date +%Y%m%d)

# Branch
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:main
```

---

## 🔄 Update Workflow

When you update your code:

```bash
# 1. Commit changes
git add .
git commit -m "Update application"

# 2. Tag new version
git tag -a v1.1.0 -m "Release v1.1.0"

# 3. Push
git push origin main --tags

# GitHub Actions will automatically:
# - Build new image
# - Push to GHCR with tags: v1.1.0, latest
```

Or manually:
```bash
docker build -f Dockerfile.prod -t ghcr.io/umaraliyev0101/ai-education:latest .
docker push ghcr.io/umaraliyev0101/ai-education:latest
```

---

## 🛠️ Troubleshooting

### "unauthorized: unauthenticated"
```bash
# Re-login
docker logout ghcr.io
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### "denied: permission_denied"
- Check token has `write:packages` permission
- Verify username is correct
- Check package visibility settings

### "manifest unknown"
```bash
# Ensure image was pushed
docker images | grep ghcr.io

# Try pulling again
docker pull ghcr.io/umaraliyev0101/ai-education:latest
```

### Build fails
```bash
# Clear cache and rebuild
docker builder prune -a
docker build --no-cache -f Dockerfile.prod -t ai-education:latest .
```

---

## 📚 Additional Resources

- **GHCR Docs**: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- **GitHub Actions**: https://docs.github.com/en/actions
- **Docker Docs**: https://docs.docker.com/engine/reference/commandline/push/

---

## ✅ Summary

**You've successfully:**
- ✅ Created GitHub Personal Access Token
- ✅ Logged in to GHCR
- ✅ Built production Docker image
- ✅ Tagged image for GHCR
- ✅ Pushed to GitHub Container Registry
- ✅ Set up automatic deployment with GitHub Actions

**Your image is now available at:**
```
ghcr.io/umaraliyev0101/ai-education:latest
```

**Anyone can now pull and run:**
```bash
docker pull ghcr.io/umaraliyev0101/ai-education:latest
docker run -p 8001:8001 ghcr.io/umaraliyev0101/ai-education:latest
```

🎉 **Congratulations!** Your AI Education Platform is now on GitHub Container Registry!
