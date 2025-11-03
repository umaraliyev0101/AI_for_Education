# 🏗️ Local Docker Build Testing Guide

## Prerequisites

### 1. Start Docker Desktop

Docker is installed but not running. You need to start it:

**On Windows:**
1. Press `Windows Key`
2. Search for "Docker Desktop"
3. Click to start it
4. Wait for Docker Desktop to fully start (check system tray icon)
5. When ready, the Docker icon will be steady (not animated)

**Or from PowerShell:**
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

**Verify Docker is running:**
```powershell
docker ps
```

Should show empty list or running containers (not an error).

---

## Local Build & Test Process

### Step 1: Build the Image

```powershell
# Build with a test tag
docker build -f Dockerfile.prod -t ai-education:test .

# This will take 15-20 minutes (downloading packages)
# You'll see output like:
# Step 1/30 : FROM python:3.11-slim AS builder
# Step 2/30 : ENV PIP_NO_CACHE_DIR=1...
# ... etc
```

**Expected build time:** 15-20 minutes

---

### Step 2: Check the Build Succeeded

```powershell
# List images
docker images | Select-String "ai-education"

# Should show:
# ai-education   test   <image-id>   <size>
```

---

### Step 3: Test Run the Container

```powershell
# Run the container
docker run -d `
  --name ai-education-test `
  -p 8001:8001 `
  -e SECRET_KEY="test-secret-key-for-local-testing-only" `
  -e DATABASE_URL="sqlite:///./ai_education.db" `
  -v ${PWD}/uploads:/app/uploads `
  -v ${PWD}/ai_education.db:/app/ai_education.db `
  ai-education:test

# Check it started
docker ps
```

---

### Step 4: Watch the Logs

```powershell
# Follow logs in real-time
docker logs ai-education-test -f

# Look for:
# 🚀 Starting AI Education Platform...
# 📊 Initializing database...
# 🔧 Starting application server...
# ✅ Starting with 4 workers on port 8001
# INFO:     Started server process
# INFO:     Application startup complete.
```

**Press `Ctrl+C` to stop following logs**

---

### Step 5: Test the Application

```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET

# Should return: {"status":"healthy"}

# Test API docs (open in browser)
Start-Process "http://localhost:8001/docs"
```

---

### Step 6: Check for Errors

```powershell
# If you see "ModuleNotFoundError", check:
docker exec ai-education-test python -c "import backend; print('✅ Backend module found')"

# Check PYTHONPATH
docker exec ai-education-test printenv PYTHONPATH

# Should show: /app
```

---

### Step 7: Test API Endpoints

```powershell
# Create a test user
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
    full_name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/register" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"

# Test login
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/login" `
  -Method POST `
  -Body $loginBody `
  -ContentType "application/json"

# Should get a token
Write-Host "Access Token: $($response.access_token)"
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'backend'"

**Check:**
```powershell
docker exec ai-education-test ls -la /app/backend
docker exec ai-education-test python -c "import sys; print(sys.path)"
```

**Expected:** `/app` should be in sys.path

---

### Issue: Container Exits Immediately

**Check logs:**
```powershell
docker logs ai-education-test
```

**Common causes:**
- Start script not executable
- Import errors
- Missing dependencies

---

### Issue: Port Already in Use

**Check what's on port 8001:**
```powershell
Get-NetTCPConnection -LocalPort 8001
```

**If your dev server is running:**
```powershell
# Stop the uvicorn terminal (the one running backend)
# Or use a different port:
docker run -p 8002:8001 ...
```

---

### Issue: Build Fails

**Clean Docker cache and retry:**
```powershell
docker builder prune -a -f
docker build --no-cache -f Dockerfile.prod -t ai-education:test .
```

---

## Cleanup After Testing

### Stop and Remove Test Container

```powershell
# Stop the container
docker stop ai-education-test

# Remove the container
docker rm ai-education-test

# Optional: Remove test image
docker rmi ai-education:test
```

### Clean Up Docker Resources

```powershell
# Remove unused images
docker image prune -a

# Remove all unused resources
docker system prune -a
```

---

## If Build is Successful

### Push to GitHub Container Registry

```powershell
# Tag for GHCR
docker tag ai-education:test ghcr.io/umaraliyev0101/ai_for_education:latest

# Login to GHCR
$token = "YOUR_GITHUB_TOKEN"
echo $token | docker login ghcr.io -u umaraliyev0101 --password-stdin

# Push
docker push ghcr.io/umaraliyev0101/ai_for_education:latest
```

---

## Quick Test Script

Save this as `test-docker-build.ps1`:

```powershell
#!/usr/bin/env pwsh
# Quick Docker Build Test Script

Write-Host "🏗️  Building Docker image..." -ForegroundColor Cyan
docker build -f Dockerfile.prod -t ai-education:test .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build succeeded!" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Starting container..." -ForegroundColor Cyan
docker run -d `
  --name ai-education-test `
  -p 8001:8001 `
  -e SECRET_KEY="test-secret-key-for-local-testing" `
  -e DATABASE_URL="sqlite:///./ai_education.db" `
  ai-education:test

Start-Sleep -Seconds 5

Write-Host "📋 Checking logs..." -ForegroundColor Cyan
docker logs ai-education-test

Write-Host ""
Write-Host "🏥 Testing health endpoint..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 30
    Write-Host "✅ Health check passed: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed!" -ForegroundColor Red
    Write-Host "Logs:" -ForegroundColor Yellow
    docker logs ai-education-test
}

Write-Host ""
Write-Host "🧹 Cleanup? (y/n)" -ForegroundColor Yellow
$cleanup = Read-Host

if ($cleanup -eq "y") {
    docker stop ai-education-test
    docker rm ai-education-test
    Write-Host "✅ Cleaned up!" -ForegroundColor Green
} else {
    Write-Host "Container still running. Stop with: docker stop ai-education-test" -ForegroundColor Cyan
}
```

Run it:
```powershell
.\test-docker-build.ps1
```

---

## Build Output to Watch For

### ✅ Good Signs:
```
Step 1/30 : FROM python:3.11-slim AS builder
 ---> abc123def456
Step 2/30 : ENV PIP_NO_CACHE_DIR=1
 ---> Running in xyz789
...
Successfully built abc123def456
Successfully tagged ai-education:test
```

### ❌ Bad Signs:
```
ERROR: failed to solve: process '/bin/sh -c pip install...' did not complete successfully: exit code: 1
```

If you see errors during build, share the output!

---

## Expected Timeline

| Step | Time |
|------|------|
| Start Docker Desktop | 1-2 min |
| Build image | 15-20 min |
| Start container | 30 sec |
| Health check | 10 sec |
| Test endpoints | 1 min |
| **Total** | **~20 min** |

---

## What to Check Before Building

### 1. Files Exist
```powershell
Test-Path Dockerfile.prod  # Should be True
Test-Path start.sh         # Should be True
Test-Path requirements.txt # Should be True
Test-Path backend/main.py  # Should be True
```

### 2. Docker Desktop Running
```powershell
docker ps  # Should not error
```

### 3. Disk Space
```powershell
Get-PSDrive C | Select-Object Used,Free
# Need at least 10GB free
```

---

## After Successful Local Test

1. ✅ Commit the changes
2. ✅ Push to GitHub
3. ✅ Let GitHub Actions build
4. ✅ Deploy to server
5. ✅ Celebrate! 🎉

---

## Common Build Times by Machine

| Machine Type | Build Time |
|--------------|------------|
| Modern Desktop (8+ cores, 16GB RAM) | 12-15 min |
| Laptop (4 cores, 8GB RAM) | 18-25 min |
| Older Machine (2 cores, 4GB RAM) | 30-40 min |
| GitHub Actions (cloud) | 20-25 min |

Your first build will be slower (downloading base images). Subsequent builds are faster (cached layers).

---

## Ready to Build?

1. **Start Docker Desktop** (wait for it to fully start)
2. **Run:** `docker build -f Dockerfile.prod -t ai-education:test .`
3. **Wait** 15-20 minutes
4. **Test:** `docker run -d -p 8001:8001 --name ai-education-test ai-education:test`
5. **Verify:** `docker logs ai-education-test -f`
6. **Check:** `Invoke-WebRequest http://localhost:8001/health`

Good luck! 🚀
