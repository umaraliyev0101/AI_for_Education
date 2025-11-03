# 🚨 Error 503 Quick Fix Guide

## What to Do RIGHT NOW

### Option 1: Quick Restart (Try This First)

SSH to your server and run:

```bash
cd /opt/ai-education  # or your app directory

# Restart the container
docker restart ai-education-app

# Watch logs
docker logs ai-education-app -f
```

Wait 30-60 seconds, then test:
```bash
curl http://localhost:8001/health
```

---

### Option 2: Force Recreate

If restart didn't work:

```bash
# Stop and remove
docker-compose -f docker-compose.prod.yml down

# Start fresh
docker-compose -f docker-compose.prod.yml up -d

# Watch logs
docker logs ai-education-app -f
```

---

### Option 3: Pull Latest Image

If using Watchtower or manual deployment:

```bash
# Pull latest
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest

# Recreate
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Monitor
docker logs ai-education-app -f
```

---

## Diagnosis: Run This Script

```bash
# Upload diagnose.sh to your server
# Then run:
chmod +x diagnose.sh
./diagnose.sh
```

This will show you exactly what's wrong!

---

## Most Common Causes & Fixes

### 1. App is Still Starting (ML Models Loading)

**Symptoms:** Container running, but 503 error

**Fix:** Wait 2-3 minutes. ML models take time to load.

```bash
# Watch for "Application startup complete"
docker logs ai-education-app -f
```

---

### 2. Application Crashed

**Symptoms:** Container keeps restarting

**Fix:** Check logs for errors:

```bash
docker logs ai-education-app --tail 100
```

Common errors:
- `ModuleNotFoundError` → Image build failed, rebuild
- `PermissionError` → Fix: `sudo chown -R 1000:1000 .`
- `KeyError: 'SECRET_KEY'` → Add to .env file

---

### 3. Port Not Mapped Correctly

**Symptoms:** Container running, but can't access

**Fix:**

```bash
# Check port mapping
docker ps

# Should show: 0.0.0.0:8001->8001/tcp

# If wrong, fix in docker-compose and recreate
```

---

### 4. Health Check Failing

**Symptoms:** Container marked as unhealthy

**Fix:**

```bash
# Check health status
docker inspect ai-education-app | grep -A 10 Health

# Test health endpoint manually
docker exec ai-education-app curl http://localhost:8001/health
```

---

### 5. Out of Memory

**Symptoms:** Container keeps getting killed

**Fix:**

```bash
# Check memory
free -h
docker stats

# Reduce workers in docker-compose.yml:
# command: gunicorn ... --workers 2
```

---

## Emergency Commands

```bash
# 1. Stop everything
docker-compose -f docker-compose.prod.yml down

# 2. Clean up
docker system prune -f

# 3. Recreate directories
mkdir -p uploads/{audio,faces,materials,presentations,slides}
mkdir -p vector_stores/lesson_materials

# 4. Start fresh
docker-compose -f docker-compose.prod.yml up -d

# 5. Watch logs
docker logs ai-education-app -f
```

---

## Check GitHub Actions Build

Your image might not have built correctly:

1. Go to: https://github.com/umaraliyev0101/AI_for_Education/actions
2. Check if last build succeeded
3. If failed, check the build logs
4. The optimized Dockerfile.prod should fix it

---

## Still Not Working?

### Get Detailed Logs

```bash
# Save logs to file
docker logs ai-education-app > app_logs.txt 2>&1

# Check last 200 lines for errors
tail -200 app_logs.txt | grep -i "error\|exception\|traceback"
```

### Test Image Locally (if you have Docker on Windows)

```powershell
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest
docker run -p 8001:8001 ghcr.io/umaraliyev0101/ai_for_education:latest
```

If it fails locally too, the image build is broken.

---

## Contact Info

Share these details:

```bash
# Run on server:
echo "=== Container Status ===" > debug_info.txt
docker ps -a >> debug_info.txt
echo -e "\n=== Container Logs ===" >> debug_info.txt
docker logs ai-education-app --tail 100 >> debug_info.txt 2>&1
echo -e "\n=== Image Info ===" >> debug_info.txt
docker images | grep ai >> debug_info.txt

# Then share debug_info.txt
```

---

## Prevention

After fixing, set up monitoring:

```bash
# Install Watchtower for auto-updates
docker-compose -f docker-compose.watchtower.yml up -d

# Check status regularly
docker ps
docker logs ai-education-app --tail 20
curl http://localhost:8001/health
```

---

## Most Likely Cause

Based on your GitHub Actions, the most likely issue is:

**The Docker build on GitHub Actions is still failing** (from the pip install error we fixed earlier)

### To Verify:

1. Go to: https://github.com/umaraliyev0101/AI_for_Education/actions
2. Check the latest "Build and Push Docker Image" workflow
3. If it's red (failed), the image is broken

### Solution:

```bash
# Commit the fixed Dockerfile.prod
git add Dockerfile.prod
git commit -m "fix: optimize Docker build for GitHub Actions"
git push

# Wait 25 minutes for build to complete
# Then on server:
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

---

**TL;DR:** 
1. SSH to server
2. Run: `docker logs ai-education-app`
3. See what error appears
4. Fix that specific error
5. Run: `docker restart ai-education-app`
