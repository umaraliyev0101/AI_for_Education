# 🚀 Docker Quick Start - AI Education Platform

## ⚡ Super Quick Start (3 Steps!)

### Step 1: Start Docker Desktop
- Look for Docker icon in system tray
- If not running: Start Menu → Docker Desktop
- Wait for "Docker Desktop is running" message

### Step 2: Run Deployment Script
```powershell
.\deploy-docker.ps1
```

### Step 3: Access Application
Open browser: http://localhost:8001/docs

**Login:** admin / admin123

---

## 📋 What You Need

✅ Docker Desktop installed (You have v28.5.1)  
✅ Docker Compose installed (You have v2.40.2)  
⚠️ **Docker Desktop must be running!**

---

## 🎯 Starting Docker Desktop

### Windows 10/11:
1. Press `Win` key
2. Type "Docker Desktop"
3. Click to start
4. Wait for whale icon to stop animating (usually 30-60 seconds)
5. Icon will show "Docker Desktop is running"

### Check if Docker is Running:
```powershell
docker ps
```
✅ Should show empty table (no errors)  
❌ If error: Start Docker Desktop first

---

## 🐳 Deployment Options

### Option 1: Interactive Script (Recommended!)
```powershell
.\deploy-docker.ps1
```
**What it does:**
- Checks Docker is running
- Verifies .env configuration
- Gives you deployment options:
  1. Fresh deployment (build + start)
  2. Start existing containers
  3. Rebuild and restart
  4. Stop containers
  5. View logs

### Option 2: Manual Commands

**First Time Setup:**
```powershell
# 1. Create .env if needed
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
}

# 2. Build Docker image
docker-compose build

# 3. Start containers
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

**Daily Use:**
```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

---

## 📊 Check Your Setup

```powershell
# 1. Docker version
docker --version
# ✅ Docker version 28.5.1, build e180ab8

# 2. Docker Compose version
docker-compose --version
# ✅ Docker Compose version v2.40.2

# 3. Docker running
docker ps
# ✅ Should show table (even if empty)

# 4. .env file exists
Test-Path .env
# ✅ True

# 5. Docker files exist
Test-Path Dockerfile
Test-Path docker-compose.yml
# ✅ Both should be True
```

---

## 🎮 Using the Deployment Script

### Run the Script:
```powershell
.\deploy-docker.ps1
```

### What Happens:
1. ✅ Checks Docker is installed and running
2. ✅ Checks/creates .env file
3. ✅ Generates secure secret key automatically
4. ✅ Shows deployment menu

### Menu Options Explained:

**1. Fresh deployment (build + start)**
- Use for: First time or after code changes
- Time: 5-10 minutes (first time), 2-3 minutes (subsequent)
- What it does: Builds image from scratch, starts container

**2. Start existing containers**
- Use for: Restarting after stopping
- Time: 10-30 seconds
- What it does: Starts previously built containers

**3. Rebuild and restart**
- Use for: After changing requirements.txt or Dockerfile
- Time: 5-10 minutes
- What it does: Clean build without cache, fresh start

**4. Stop containers**
- Use for: Shutting down application
- Time: 5-10 seconds
- What it does: Stops containers, keeps data

**5. View logs**
- Use for: Debugging or monitoring
- What it does: Shows real-time application logs
- Exit: Press Ctrl+C

---

## 🔍 Troubleshooting

### Error: "Docker is not running"
**Solution:**
1. Start Docker Desktop from Start Menu
2. Wait for whale icon to stabilize
3. Run script again

### Error: "Port 8001 already in use"
**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :8001

# Stop the process
taskkill /PID <PID> /F

# Or stop your local server if running
# Then try again
```

### Error: Build fails
**Solution:**
```powershell
# Clean everything
docker-compose down -v
docker system prune -a

# Rebuild
.\deploy-docker.ps1
# Choose option 1
```

### Error: Container starts but can't access
**Solution:**
```powershell
# Wait a bit longer (containers need time to start)
Start-Sleep -Seconds 20

# Check health
curl http://localhost:8001/health

# Check logs for errors
docker-compose logs web | Select-String "error"
```

### Container keeps restarting
**Solution:**
```powershell
# Check logs
docker-compose logs web

# Common issues:
# - .env file missing or invalid
# - Database initialization failed
# - Port conflict

# Fix: Recreate .env
Copy-Item .env.example .env -Force
# Edit .env with proper values
notepad .env

# Restart
docker-compose down
docker-compose up -d
```

---

## 📈 After Deployment

### Verify Everything Works:

1. **Health Check:**
   ```powershell
   curl http://localhost:8001/health
   ```
   Expected: `{"status":"healthy"}`

2. **API Documentation:**
   Open: http://localhost:8001/docs

3. **Login:**
   - Click "Authorize" button
   - Username: `admin`
   - Password: `admin123`

4. **Test Features:**
   - Try `/api/students` endpoints
   - Create a test student
   - Upload a test file

### Monitor Container:

```powershell
# Real-time logs
docker-compose logs -f

# Container stats
docker stats

# Container status
docker-compose ps

# Execute commands inside container
docker-compose exec web bash
```

---

## 🔄 Daily Workflow

### Starting Your Day:
```powershell
# Start containers
docker-compose up -d

# Wait 10 seconds
Start-Sleep -Seconds 10

# Open in browser
start http://localhost:8001/docs
```

### Ending Your Day:
```powershell
# Stop containers (keeps data)
docker-compose down
```

### Making Code Changes:
```powershell
# After changing Python code
docker-compose restart

# After changing requirements.txt or Dockerfile
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎯 Next Steps

1. **Test the deployment:**
   - Login to http://localhost:8001/docs
   - Try different API endpoints
   - Upload test files

2. **Change default password:**
   - Use `/api/auth/change-password` endpoint
   - Or manually update in database

3. **Create users:**
   - Create teacher accounts
   - Create viewer accounts

4. **Add students:**
   - Use student endpoints
   - Enroll faces

5. **Upload materials:**
   - Upload lesson materials
   - Upload presentations

---

## 📚 Useful Commands Reference

```powershell
# === Container Management ===
docker-compose up -d          # Start in background
docker-compose down           # Stop containers
docker-compose restart        # Restart containers
docker-compose ps             # List containers

# === Logs ===
docker-compose logs           # View all logs
docker-compose logs -f        # Follow logs
docker-compose logs web       # Logs for web service
docker-compose logs --tail=50 # Last 50 lines

# === Building ===
docker-compose build          # Build image
docker-compose build --no-cache  # Build without cache
docker-compose up -d --build  # Build and start

# === Cleanup ===
docker-compose down -v        # Stop and remove volumes
docker system prune           # Remove unused data
docker system prune -a        # Remove all unused data

# === Debugging ===
docker-compose exec web bash  # Shell in container
docker-compose exec web env   # Show environment
docker stats                  # Resource usage
docker inspect aiedu-backend  # Detailed info
```

---

## ⚡ Pro Tips

1. **Use the script:** `.\deploy-docker.ps1` handles everything
2. **Check logs regularly:** `docker-compose logs -f`
3. **Monitor resources:** Docker Desktop → Containers tab
4. **Keep it clean:** Run `docker system prune` weekly
5. **Backup data:** Containers are ephemeral, volumes persist

---

## 🆘 Need Help?

1. **Check logs first:**
   ```powershell
   docker-compose logs web | Select-String "error"
   ```

2. **Check comprehensive guide:**
   - Read `DOCKER_DEPLOYMENT.md`

3. **Common issues:**
   - Docker not running → Start Docker Desktop
   - Port in use → Stop conflicting service
   - Build fails → Clean and rebuild
   - Can't connect → Wait longer, check logs

4. **Still stuck?**
   - GitHub Issues: https://github.com/umaraliyev0101/AI_for_Education/issues

---

## ✅ Quick Checklist

Before running:
- [ ] Docker Desktop installed
- [ ] Docker Desktop is running
- [ ] .env file exists (script creates it)
- [ ] Port 8001 is free

After deployment:
- [ ] Container is running: `docker-compose ps`
- [ ] Health check passes: `curl http://localhost:8001/health`
- [ ] Can access docs: http://localhost:8001/docs
- [ ] Can login with admin/admin123

---

**Ready to deploy? Run: `.\deploy-docker.ps1` 🚀**
