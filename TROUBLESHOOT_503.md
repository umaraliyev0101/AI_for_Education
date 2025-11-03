# Troubleshooting Error 503 - Service Unavailable

## What Error 503 Means

Your container exists but:
- ❌ Application isn't starting properly
- ❌ Application is crashing on startup
- ❌ Port mapping is incorrect
- ❌ Health check is failing

## Diagnosis Steps

### Step 1: Check Container Status

```bash
# SSH to your server first
ssh user@your-server

# Check all containers
docker ps -a

# Look for:
# - Is ai-education-app running or stopped?
# - Is it restarting repeatedly?
# - What's the status column say?
```

Expected output:
```
CONTAINER ID   IMAGE                                    STATUS
abc123         ghcr.io/.../ai_for_education:latest     Up 2 minutes (healthy)
```

If you see:
- `Exited (1) 2 minutes ago` → Application crashed
- `Restarting (1) 30 seconds ago` → Crash loop
- `Up 2 minutes (unhealthy)` → Health check failing

---

### Step 2: Check Application Logs

```bash
# View last 100 lines
docker logs ai-education-app --tail 100

# Follow logs in real-time
docker logs ai-education-app -f
```

#### Common Error Patterns:

**1. Missing Environment Variables:**
```
KeyError: 'SECRET_KEY'
ERROR: Missing required environment variable
```
**Fix:** Add to docker-compose or .env file

**2. Database Connection Error:**
```
sqlite3.OperationalError: unable to open database file
PermissionError: [Errno 13] Permission denied: 'ai_education.db'
```
**Fix:** Check file permissions and volume mounts

**3. Port Already in Use:**
```
OSError: [Errno 98] Address already in use
```
**Fix:** Stop other process on port 8001 or change port

**4. Import Errors:**
```
ModuleNotFoundError: No module named 'transformers'
ImportError: cannot import name 'XXX'
```
**Fix:** Rebuild image with all dependencies

**5. Memory Issues:**
```
Killed
MemoryError
```
**Fix:** Increase server RAM or reduce ML model size

---

### Step 3: Test Container Directly

```bash
# Try to access health endpoint from server
curl http://localhost:8001/health

# If that fails, try entering the container
docker exec -it ai-education-app /bin/bash

# Inside container, check if app is running
ps aux | grep python
curl http://localhost:8001/health
```

---

### Step 4: Check Network/Firewall

```bash
# Check if port is listening
netstat -tlnp | grep 8001

# Check if firewall is blocking
sudo ufw status
# or
sudo firewall-cmd --list-all

# Test from outside
curl http://your-server-ip:8001/health
```

---

## Quick Fixes

### Fix 1: Restart Container

```bash
docker-compose -f docker-compose.prod.yml restart

# Or force recreate
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Fix 2: Check Environment Variables

```bash
# Ensure .env file exists
cat .env

# Should contain:
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./ai_education.db
# ... etc
```

### Fix 3: Rebuild Image

If the image is corrupted or incomplete:

```bash
# Pull latest image
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest

# Force recreate containers
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### Fix 4: Check File Permissions

```bash
# Make sure app can write to database
ls -la ai_education.db
sudo chown -R 1000:1000 /opt/ai-education/

# Recreate directories
mkdir -p uploads/{audio,faces,materials,presentations,slides}
mkdir -p vector_stores/lesson_materials
```

### Fix 5: Check Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check CPU
top

# If low resources, clean up
docker system prune -a
```

---

## Step-by-Step Recovery

### Recovery Plan A: Quick Restart

```bash
cd /opt/ai-education  # or wherever your app is

# Stop everything
docker-compose -f docker-compose.prod.yml down

# Pull latest image
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest

# Start fresh
docker-compose -f docker-compose.prod.yml up -d

# Watch logs
docker logs ai-education-app -f
```

Wait 30-60 seconds for app to start, then test:
```bash
curl http://localhost:8001/health
```

### Recovery Plan B: Fresh Deployment

If Plan A doesn't work:

```bash
# Stop and remove everything
docker-compose -f docker-compose.prod.yml down -v

# Clean up old images
docker system prune -a

# Re-create directories
mkdir -p uploads/{audio,faces,materials,presentations,slides}
mkdir -p vector_stores/lesson_materials

# Start fresh
docker-compose -f docker-compose.prod.yml up -d

# Monitor startup
docker logs ai-education-app -f
```

### Recovery Plan C: Manual Debug

If still failing:

```bash
# Run container interactively
docker run -it --rm \
  -p 8001:8001 \
  -v $(pwd)/uploads:/app/uploads \
  ghcr.io/umaraliyev0101/ai_for_education:latest \
  /bin/bash

# Inside container:
cd /app
ls -la
python -c "import backend.main"  # Test imports
uvicorn backend.main:app --host 0.0.0.0 --port 8001  # Start manually
```

This will show you the exact error!

---

## Common Issues & Solutions

### Issue: Container Exits Immediately

**Symptoms:**
```bash
docker ps -a
# Shows: Exited (1) 2 seconds ago
```

**Check:**
```bash
docker logs ai-education-app
```

**Common causes:**
- Missing CMD or ENTRYPOINT in Dockerfile
- Application crashes on import
- Invalid gunicorn configuration

**Fix:** Check logs and fix the specific error

---

### Issue: Container Starts But 503 Error

**Symptoms:**
- `docker ps` shows container running
- `curl localhost:8001` gives 503

**Possible causes:**
1. **App is starting slowly** (loading ML models)
   - Wait 1-2 minutes
   - Check logs for "Application startup complete"

2. **App crashed after startup**
   - Check logs for errors after "Started server process"

3. **Health check failing**
   ```bash
   docker inspect ai-education-app | grep -A 10 Health
   ```

4. **Nginx/reverse proxy issue**
   - Check nginx logs: `docker logs nginx`
   - Verify upstream configuration

---

### Issue: Permission Denied

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/app/ai_education.db'
```

**Fix:**
```bash
# On host machine
sudo chown -R 1000:1000 .
chmod -R 755 uploads
chmod 644 ai_education.db
```

---

### Issue: Memory/CPU Exhausted

**Symptoms:**
```
Container was killed
MemoryError
```

**Check:**
```bash
docker stats
free -h
```

**Fix:**
- Upgrade server RAM
- Or reduce worker count in docker-compose:
```yaml
command: gunicorn backend.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker
```

---

## Monitoring Commands

Keep these handy:

```bash
# Check what's running
docker ps

# Stream logs
docker logs ai-education-app -f

# Check resource usage
docker stats

# Check health
curl http://localhost:8001/health

# Enter container
docker exec -it ai-education-app /bin/bash

# Restart specific container
docker restart ai-education-app
```

---

## If Nothing Works

1. **Check GitHub Actions Build:**
   - Go to: https://github.com/umaraliyev0101/AI_for_Education/actions
   - Verify last build succeeded
   - Check build logs for errors

2. **Test Image Locally:**
   ```bash
   # On your Windows machine (if Docker is installed)
   docker pull ghcr.io/umaraliyev0101/ai_for_education:latest
   docker run -p 8001:8001 ghcr.io/umaraliyev0101/ai_for_education:latest
   ```

3. **Provide Logs:**
   Run on server and share output:
   ```bash
   docker logs ai-education-app --tail 200 > app_logs.txt
   docker ps -a > container_status.txt
   docker images | grep ai > images.txt
   ```

---

## Need Immediate Help?

Run this diagnostic script on your server:

```bash
#!/bin/bash
echo "=== Docker Status ==="
docker ps -a

echo -e "\n=== Container Logs (last 50 lines) ==="
docker logs ai-education-app --tail 50

echo -e "\n=== Health Check ==="
curl -s http://localhost:8001/health || echo "Health check failed"

echo -e "\n=== Disk Space ==="
df -h

echo -e "\n=== Memory ==="
free -h

echo -e "\n=== Listening Ports ==="
netstat -tlnp | grep 8001 || echo "Port 8001 not listening"

echo -e "\n=== Recent Image ==="
docker images | grep ai_for_education | head -1
```

Save as `diagnose.sh`, run `chmod +x diagnose.sh && ./diagnose.sh`, and share the output.
