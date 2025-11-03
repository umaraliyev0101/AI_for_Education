# 🚀 Quick Start: Test Docker Build Locally

## Step 1: Start Docker Desktop

Press `Windows Key`, search for "Docker Desktop", and start it.

Wait until the Docker icon in the system tray is steady (not animated).

## Step 2: Run the Test Script

```powershell
.\test-docker-build.ps1
```

This will:
- ✅ Build the Docker image (15-20 minutes)
- ✅ Start a test container
- ✅ Run health checks
- ✅ Verify everything works
- ✅ Give you access to test the API

## What You'll See

```
╔════════════════════════════════════════════════════════╗
║   AI Education Platform - Local Docker Build Test     ║
╚════════════════════════════════════════════════════════╝

🔍 Checking Docker status...
✅ Docker is running

🧹 Cleaning up existing test container...

🏗️  Building Docker image (this will take 15-20 minutes)...
Started at: 14:30:00
...
✅ Build SUCCEEDED in 18.5 minutes!

🚀 Starting container...
✅ Container started

⏳ Waiting for application to start (30 seconds)...

📋 Container logs:
═══════════════════════════════════════════════════════
🚀 Starting AI Education Platform...
📊 Initializing database...
🔧 Starting application server...
✅ Starting with 4 workers on port 8001
INFO:     Application startup complete.
═══════════════════════════════════════════════════════

🏥 Testing health endpoint...
✅ Health check PASSED: healthy

╔════════════════════════════════════════════════════════╗
║                    TEST RESULTS                        ║
╚════════════════════════════════════════════════════════╝

Container: ai-education-test
Image: ai-education:test
Port: 8001
Health: ✅ HEALTHY

Access your application:
  • Health: http://localhost:8001/health
  • API Docs: http://localhost:8001/docs
  • OpenAPI: http://localhost:8001/openapi.json
```

## If Build Succeeds ✅

Your Docker image works! You can:

1. **Test it locally:**
   - Open http://localhost:8001/docs
   - Try the API endpoints

2. **Push to GitHub:**
   ```powershell
   git add .
   git commit -m "fix: resolve ModuleNotFoundError and optimize Docker build"
   git push origin main
   ```

3. **Deploy to server:**
   - Wait for GitHub Actions to build (~20 min)
   - Pull on server: `docker pull ghcr.io/umaraliyev0101/ai_for_education:latest`
   - Restart: `docker-compose -f docker-compose.prod.yml up -d --force-recreate`

## If Build Fails ❌

The script will show you the exact error. Common issues:

### "ModuleNotFoundError: No module named 'backend'"
✅ Already fixed in the current code (PYTHONPATH set)

### "exit code: 1" during pip install
- Check the error message
- May need to add system dependencies
- Share the output for help

### "Docker is not running"
- Start Docker Desktop first
- Wait for it to fully initialize

## Script Options

```powershell
# Skip building (use existing image)
.\test-docker-build.ps1 -NoBuild

# Keep container running (don't ask about cleanup)
.\test-docker-build.ps1 -NoCleanup

# Use different port
.\test-docker-build.ps1 -Port 8002
```

## Manual Commands (If You Prefer)

### Build:
```powershell
docker build -f Dockerfile.prod -t ai-education:test .
```

### Run:
```powershell
docker run -d --name ai-education-test -p 8001:8001 `
  -e SECRET_KEY="test-secret" `
  ai-education:test
```

### Check:
```powershell
docker logs ai-education-test -f
Invoke-WebRequest http://localhost:8001/health
```

### Cleanup:
```powershell
docker stop ai-education-test
docker rm ai-education-test
docker rmi ai-education:test
```

## Need Help?

See `LOCAL_BUILD_GUIDE.md` for detailed troubleshooting.

---

**Ready? Start Docker Desktop and run:** `.\test-docker-build.ps1`

**Time needed:** ~20 minutes total (mostly waiting for build)
