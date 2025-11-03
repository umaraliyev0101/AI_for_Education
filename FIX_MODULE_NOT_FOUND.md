# 🔧 Fix for ModuleNotFoundError: No module named 'backend'

## What Was the Problem?

The Docker container couldn't find the `backend` module because:
1. ❌ PYTHONPATH was not set
2. ❌ Working directory context was incorrect
3. ❌ Python couldn't locate the backend package

## What Was Fixed?

### 1. Updated `Dockerfile.prod`
- ✅ Added `PYTHONPATH=/app` environment variable
- ✅ Set `PYTHONUNBUFFERED=1` for better logging
- ✅ Fixed the CMD to use the startup script properly

### 2. Updated `start.sh`
- ✅ Explicitly sets PYTHONPATH
- ✅ Uses `python -m backend.init_db` instead of `python backend/init_db.py`
- ✅ Better error handling for database initialization

## How to Deploy the Fix

### Option 1: Automatic via GitHub Actions (Recommended)

```powershell
# Commit the fixes
git add Dockerfile.prod start.sh
git commit -m "fix: resolve ModuleNotFoundError by setting PYTHONPATH"
git push origin main
```

Then:
1. Wait 20-25 minutes for GitHub Actions to build
2. Go to: https://github.com/umaraliyev0101/AI_for_Education/actions
3. Verify build succeeds (green checkmark ✅)
4. On your server, if using Watchtower, it will auto-update in 5 minutes
5. If not using Watchtower, SSH to server and run:

```bash
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
docker logs ai-education-app -f
```

---

### Option 2: Build and Deploy Locally (Faster)

If you have Docker installed on Windows:

```powershell
# Build the image locally
docker build -f Dockerfile.prod -t ghcr.io/umaraliyev0101/ai_for_education:latest .

# Login to GHCR
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin

# Push to GHCR
docker push ghcr.io/umaraliyev0101/ai_for_education:latest
```

Then on your server:

```bash
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest
docker-compose -f docker-compose.prod.yml up -d --force-recreate
docker logs ai-education-app -f
```

---

### Option 3: Quick Test (Without Building)

If you want to test the fix quickly on your server:

```bash
# SSH to your server
cd /opt/ai-education  # or your app directory

# Create a wrapper script
cat > run.sh << 'EOF'
#!/bin/bash
export PYTHONPATH=/app:$PYTHONPATH
exec gunicorn backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -
EOF

chmod +x run.sh

# Update docker-compose to use this script
# Edit docker-compose.prod.yml and change:
# command: ["./run.sh"]

# Restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## Verification

After deploying, verify it works:

### 1. Check Container is Running

```bash
docker ps | grep ai-education-app
```

Should show: `Up X minutes (healthy)`

### 2. Check Logs for Success

```bash
docker logs ai-education-app
```

You should see:
```
🚀 Starting AI Education Platform...
📊 Initializing database...
🔧 Starting application server...
✅ Starting with 4 workers on port 8001
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Test Health Endpoint

```bash
curl http://localhost:8001/health
```

Should return: `{"status":"healthy"}`

### 4. Test API Docs

```bash
curl http://localhost:8001/docs
```

Or open in browser: `http://your-server-ip:8001/docs`

---

## Timeline

### Using GitHub Actions:
```
00:00  git push
20:00  Build complete on GitHub
25:00  Live on server (with Watchtower)
```

### Building Locally:
```
00:00  docker build
15:00  Build complete
16:00  Pushed to GHCR
17:00  Deployed to server
```

---

## What Changed in the Code?

### Dockerfile.prod
```dockerfile
# BEFORE (Missing PYTHONPATH)
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
CMD ["./start.sh"]

# AFTER (With PYTHONPATH)
RUN chmod +x start.sh
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONPATH=/app:$PYTHONPATH \
    PYTHONUNBUFFERED=1
CMD ["./start.sh"]
```

### start.sh
```bash
# BEFORE
python backend/init_db.py

# AFTER
export PYTHONPATH=/app:$PYTHONPATH
python -m backend.init_db
```

---

## Why This Fixes the Issue

1. **PYTHONPATH=/app** tells Python to look in `/app` for modules
2. **python -m backend.init_db** runs it as a module (proper Python import)
3. **export PYTHONPATH** ensures it's set before running any Python code
4. **PYTHONUNBUFFERED=1** ensures logs appear immediately

---

## If Still Getting Errors

### Check Structure Inside Container

```bash
docker exec -it ai-education-app /bin/bash

# Inside container:
ls -la /app
ls -la /app/backend
echo $PYTHONPATH
python -c "import sys; print(sys.path)"
python -c "import backend; print(backend.__file__)"
```

### Check Permissions

```bash
docker exec -it ai-education-app /bin/bash

# Inside container:
ls -la /app/backend/__init__.py
cat /app/backend/__init__.py
```

Should be readable by appuser.

---

## Rollback (If Needed)

If something goes wrong:

```bash
# On server, rollback to previous image
docker pull ghcr.io/umaraliyev0101/ai_for_education:sha-<previous-sha>
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

Or use the previous image tag from GHCR.

---

## Prevention

To prevent similar issues:

1. ✅ Always set PYTHONPATH in Docker containers
2. ✅ Use `python -m module.name` instead of `python path/to/file.py`
3. ✅ Test imports before running the app:
   ```dockerfile
   RUN python -c "import backend; import backend.main"
   ```
4. ✅ Use consistent paths throughout

---

## Summary

**Problem:** `ModuleNotFoundError: No module named 'backend'`

**Root Cause:** Python couldn't find the backend package

**Solution:** Set `PYTHONPATH=/app` in Dockerfile and start.sh

**Action Required:** 
1. Commit the fixed files
2. Push to GitHub
3. Wait for build (or build locally)
4. Deploy to server
5. Verify with `curl http://localhost:8001/health`

**ETA:** 
- GitHub Actions: 25 minutes
- Local build: 17 minutes

---

## Next Steps After Fix

1. ✅ Verify health endpoint works
2. ✅ Test API endpoints: http://your-server:8001/docs
3. ✅ Check logs are clean: `docker logs ai-education-app`
4. ✅ Set up Watchtower for auto-updates (if not done)
5. ✅ Add monitoring/alerts (optional)

---

**Need Help?** 

Run this on your server after deploying:

```bash
echo "=== Container Status ==="
docker ps | grep ai-education

echo -e "\n=== Recent Logs ==="
docker logs ai-education-app --tail 20

echo -e "\n=== Health Check ==="
curl http://localhost:8001/health

echo -e "\n=== Python Path Check ==="
docker exec ai-education-app python -c "import sys; print('\n'.join(sys.path))"

echo -e "\n=== Backend Module Check ==="
docker exec ai-education-app python -c "import backend; print('✅ Backend module found')"
```

Share the output if there are still issues!
