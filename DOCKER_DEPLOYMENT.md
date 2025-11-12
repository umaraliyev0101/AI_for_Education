# 🐳 Docker Deployment Guide - AI Education Platform

Complete guide for deploying with Docker on Windows, Linux, and Mac.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Docker Commands](#docker-commands)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)

---

## ✅ Prerequisites

### Verify Docker Installation

```powershell
# Check Docker
docker --version
# Expected: Docker version 20.10+

# Check Docker Compose
docker-compose --version
# Expected: Docker Compose version 2.0+

# Check Docker is running
docker ps
# Should not show errors
```

### Your System Status ✅
- **Docker Version:** 28.5.1 ✅
- **Docker Compose:** v2.40.2 ✅
- **Status:** Ready to deploy!

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Create Environment File

```powershell
# Copy template
Copy-Item .env.example .env

# Generate secure key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated key and edit `.env`:

```powershell
notepad .env
```

Update these lines:
```env
SECRET_KEY=<paste-your-generated-key-here>
DEBUG=False
CORS_ORIGINS=["http://localhost:3000","http://localhost:8001"]
```

### Step 2: Build and Start

```powershell
# Build the Docker image
docker-compose build

# Start containers in background
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

### Step 3: Access Application

- **API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/health

**Default Login:**
- Username: `admin`
- Password: `admin123`

### That's it! 🎉

Press `Ctrl+C` to exit logs. Containers run in background.

---

## 📖 Detailed Setup

### Understanding the Docker Setup

Your project uses:
- **Dockerfile** - Defines the application container
- **docker-compose.yml** - Orchestrates services
- **.dockerignore** - Excludes unnecessary files

### Architecture

```
┌─────────────────────────────────────┐
│     Docker Host (Your Machine)     │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   aiedu-backend Container    │  │
│  │                              │  │
│  │  - FastAPI App               │  │
│  │  - Python 3.11               │  │
│  │  - Port 8001                 │  │
│  │  - Gunicorn + Uvicorn        │  │
│  └──────────────────────────────┘  │
│            ↓                        │
│  ┌──────────────────────────────┐  │
│  │   Persistent Volumes         │  │
│  │  - ./uploads                 │  │
│  │  - ./vector_stores           │  │
│  │  - ./ai_education.db         │  │
│  │  - ./logs                    │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Step-by-Step Deployment

#### 1. Prepare Environment

```powershell
# Navigate to project
cd D:\Projects\AI_in_Education

# Create .env from template
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
}

# Generate secure secret key
$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "Generated Secret Key: $secretKey" -ForegroundColor Cyan

# Edit .env file
notepad .env
```

**Critical .env settings for Docker:**

```env
# Security - REQUIRED
SECRET_KEY=<your-generated-64-character-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
APP_NAME=AI Education Platform
APP_VERSION=1.0.0
DEBUG=False

# Database (SQLite in container)
DATABASE_URL=sqlite:///./ai_education.db

# CORS - Update for your frontend
CORS_ORIGINS=["http://localhost:3000","http://localhost:8001"]

# File Storage (container paths)
UPLOAD_DIR=/app/uploads
FACE_IMAGES_DIR=/app/uploads/faces
MATERIALS_DIR=/app/uploads/materials
PRESENTATIONS_DIR=/app/uploads/presentations
AUDIO_DIR=/app/uploads/audio
VECTOR_STORES_DIR=/app/vector_stores

# AI Models
STT_MODEL=lucio/xls-r-uzbek-cv8
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
TTS_VOICE=uz-UZ-SardorNeural

# Processing
MAX_UPLOAD_SIZE=52428800
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K_DOCUMENTS=3

# Server (for container)
GUNICORN_WORKERS=4
PORT=8001
HOST=0.0.0.0
```

#### 2. Build Docker Image

```powershell
# Build the image (takes 5-10 minutes first time)
docker-compose build

# Check image was created
docker images | Select-String "aiedu"
```

**What happens during build:**
- ✅ Downloads Python 3.11 base image
- ✅ Installs system dependencies
- ✅ Installs Python packages from requirements.txt
- ✅ Copies application code
- ✅ Creates necessary directories
- ✅ Sets up health checks

#### 3. Start Containers

```powershell
# Start in background (-d = detached mode)
docker-compose up -d

# Verify containers are running
docker-compose ps
```

**Expected output:**
```
NAME                IMAGE               STATUS              PORTS
aiedu-backend       aiedu-web          Up X seconds        0.0.0.0:8001->8001/tcp
```

#### 4. Initialize Database

The database is automatically initialized when the container starts. To verify:

```powershell
# Check logs for initialization message
docker-compose logs web | Select-String "Database"
```

#### 5. Verify Deployment

```powershell
# Check health endpoint
curl http://localhost:8001/health

# Expected: {"status":"healthy"}

# Test login (PowerShell)
$loginData = @{
    username = "admin"
    password = "admin123"
}
Invoke-WebRequest -Uri http://localhost:8001/api/auth/login -Method Post -Body $loginData
```

#### 6. Access Application

Open your browser:
- **API Docs:** http://localhost:8001/docs
- **Interactive Testing:** Use the "Try it out" buttons

---

## 🎮 Docker Commands

### Container Management

```powershell
# Start containers
docker-compose up -d

# Stop containers (keeps data)
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v

# Restart containers
docker-compose restart

# Stop specific service
docker-compose stop web

# Start specific service
docker-compose start web
```

### Viewing Logs

```powershell
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs web

# Last 100 lines
docker-compose logs --tail=100 web

# Logs since specific time
docker-compose logs --since 2024-01-01T00:00:00
```

### Container Information

```powershell
# List running containers
docker-compose ps

# View container stats (CPU, Memory)
docker stats

# Inspect container details
docker-compose exec web env

# View container processes
docker-compose top web
```

### Executing Commands in Container

```powershell
# Open shell in container
docker-compose exec web bash

# Run Python commands
docker-compose exec web python -c "print('Hello from container')"

# Check Python packages
docker-compose exec web pip list

# Initialize database manually
docker-compose exec web python -m backend.init_db

# Check disk space
docker-compose exec web df -h

# View file structure
docker-compose exec web ls -la /app
```

### Image Management

```powershell
# List images
docker images

# Remove old images
docker image prune

# Remove specific image
docker rmi aiedu-backend

# Rebuild without cache
docker-compose build --no-cache

# Pull latest base images
docker-compose pull
```

### Volume Management

```powershell
# List volumes
docker volume ls

# Inspect volume
docker volume inspect ai_in_education_uploads

# Remove unused volumes
docker volume prune

# Backup volume
docker run --rm -v ai_in_education_uploads:/data -v ${PWD}:/backup alpine tar czf /backup/uploads-backup.tar.gz /data
```

### Cleanup

```powershell
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove all unused containers, networks, images
docker system prune

# Remove everything (careful!)
docker system prune -a --volumes
```

---

## 🐛 Troubleshooting

### Issue 1: Container Won't Start

```powershell
# Check container logs
docker-compose logs web

# Check for port conflicts
netstat -ano | findstr :8001

# Try stopping and removing everything
docker-compose down
docker-compose up -d
```

### Issue 2: Permission Denied

**Windows:**
- Run PowerShell as Administrator
- Check Docker Desktop is running

**Solution:**
```powershell
# Restart Docker Desktop
# Then try again
docker-compose down
docker-compose up -d
```

### Issue 3: Build Fails

```powershell
# Clean build
docker-compose down
docker-compose build --no-cache

# Check disk space
docker system df

# Remove old images
docker image prune -a
```

### Issue 4: Database Not Initialized

```powershell
# Manual initialization
docker-compose exec web python -m backend.init_db

# Check database file
docker-compose exec web ls -la /app/ai_education.db

# View initialization logs
docker-compose logs web | Select-String "init"
```

### Issue 5: Port Already in Use

```powershell
# Find process using port 8001
netstat -ano | findstr :8001

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# Change: "8001:8001" to "8002:8001"
docker-compose up -d
```

### Issue 6: Can't Access from Browser

1. **Check container is running:**
   ```powershell
   docker-compose ps
   ```

2. **Check health endpoint:**
   ```powershell
   curl http://localhost:8001/health
   ```

3. **Check logs for errors:**
   ```powershell
   docker-compose logs web | Select-String "error"
   ```

4. **Verify firewall:**
   - Windows Defender may block Docker ports
   - Allow Docker Desktop in Windows Firewall

### Issue 7: Slow Performance

```powershell
# Increase resources in Docker Desktop
# Settings → Resources → Memory (4GB+)

# Check resource usage
docker stats

# Reduce workers in .env
# GUNICORN_WORKERS=2
```

### Issue 8: AI Models Not Downloading

```powershell
# Check logs
docker-compose logs web | Select-String "download\|model"

# Manually trigger download
docker-compose exec web python -c "
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
model = Wav2Vec2ForCTC.from_pretrained('lucio/xls-r-uzbek-cv8')
print('Model downloaded successfully')
"
```

### Issue 9: File Upload Fails

```powershell
# Check upload directory exists and is writable
docker-compose exec web ls -la /app/uploads

# Create if missing
docker-compose exec web mkdir -p /app/uploads/faces /app/uploads/materials /app/uploads/presentations

# Check permissions
docker-compose exec web chmod -R 755 /app/uploads
```

### Issue 10: WebSocket Connection Fails

**Solution:** Check CORS settings in `.env`:
```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:8001","ws://localhost:8001"]
```

Then restart:
```powershell
docker-compose restart
```

---

## 🏢 Production Deployment with Docker

### Using Docker Compose with Nginx

Enable the production profile:

```powershell
# Start with Nginx reverse proxy
docker-compose --profile production up -d

# This starts:
# - Web application (aiedu-backend)
# - Nginx reverse proxy (aiedu-nginx)
```

### Using PostgreSQL Instead of SQLite

Enable PostgreSQL:

```powershell
# Update docker-compose.yml to use postgres profile
docker-compose --profile production up -d

# Update .env
# DATABASE_URL=postgresql://aiedu:aiedu123@postgres:5432/ai_education
```

### Environment Variables for Production

```env
# Production .env
SECRET_KEY=<very-secure-64-char-key>
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# PostgreSQL (if using)
POSTGRES_USER=aiedu
POSTGRES_PASSWORD=<secure-password>
POSTGRES_DB=ai_education
DATABASE_URL=postgresql://aiedu:<secure-password>@postgres:5432/ai_education

# Redis (if using)
REDIS_URL=redis://redis:6379/0

# Server
GUNICORN_WORKERS=8
PORT=8001
```

### SSL with Docker

For production with SSL, use the Nginx container and mount SSL certificates:

```yaml
# Add to nginx service in docker-compose.yml
volumes:
  - ./nginx/ssl:/etc/nginx/ssl:ro
  - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```

---

## 📊 Monitoring Docker Deployment

### Real-time Monitoring

```powershell
# Watch resource usage
docker stats

# Stream logs
docker-compose logs -f

# Check health
while ($true) {
    curl http://localhost:8001/health
    Start-Sleep -Seconds 5
}
```

### Docker Desktop Dashboard

1. Open Docker Desktop
2. Go to "Containers" tab
3. View your containers:
   - Status
   - Logs
   - Stats
   - Inspect

### Health Checks

Built-in health check runs every 30 seconds:

```powershell
# Check health status
docker-compose ps

# Inspect health details
docker inspect aiedu-backend | Select-String "Health"
```

---

## 💾 Backup and Restore

### Backup

```powershell
# Create backup directory
New-Item -ItemType Directory -Path "backups" -Force

# Backup database
docker-compose exec web cp /app/ai_education.db /app/ai_education.db.backup
docker cp aiedu-backend:/app/ai_education.db.backup ./backups/db_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").db

# Backup uploads
docker run --rm -v ai_in_education_uploads:/data -v ${PWD}/backups:/backup alpine tar czf /backup/uploads_$(Get-Date -Format "yyyyMMdd_HHmmss").tar.gz /data

# Backup vector stores
docker run --rm -v ai_in_education_vector-stores:/data -v ${PWD}/backups:/backup alpine tar czf /backup/vectors_$(Get-Date -Format "yyyyMMdd_HHmmss").tar.gz /data
```

### Restore

```powershell
# Stop containers
docker-compose down

# Restore database
docker cp ./backups/db_backup_YYYYMMDD_HHMMSS.db aiedu-backend:/app/ai_education.db

# Restore uploads (extract tar.gz first)
docker run --rm -v ai_in_education_uploads:/data -v ${PWD}/backups:/backup alpine tar xzf /backup/uploads_YYYYMMDD_HHMMSS.tar.gz -C /data

# Start containers
docker-compose up -d
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Docker and Docker Compose installed
- [ ] `.env` file created and configured
- [ ] SECRET_KEY generated and set
- [ ] CORS_ORIGINS configured
- [ ] DEBUG set to False for production

### Deployment
- [ ] `docker-compose build` successful
- [ ] `docker-compose up -d` started containers
- [ ] `docker-compose ps` shows "Up" status
- [ ] Health check responds: `curl http://localhost:8001/health`
- [ ] Can login via `/docs`

### Post-Deployment
- [ ] Change default admin password
- [ ] Test all critical features
- [ ] Setup backup script
- [ ] Monitor logs for errors
- [ ] Document configuration
- [ ] Setup monitoring alerts

---

## 📚 Quick Reference

### Most Used Commands

```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Rebuild
docker-compose build --no-cache
docker-compose up -d

# Shell access
docker-compose exec web bash

# Cleanup
docker-compose down -v
docker system prune -a
```

### Useful Aliases (PowerShell Profile)

Add to your PowerShell profile:

```powershell
# Open profile
notepad $PROFILE

# Add these functions
function dc-up { docker-compose up -d }
function dc-down { docker-compose down }
function dc-logs { docker-compose logs -f }
function dc-ps { docker-compose ps }
function dc-restart { docker-compose restart }
function dc-shell { docker-compose exec web bash }
```

---

## 🎯 Next Steps

1. **Test your deployment:**
   - Open http://localhost:8001/docs
   - Login with admin/admin123
   - Try creating a student
   - Upload test files

2. **Customize configuration:**
   - Update AI model settings
   - Configure CORS for your frontend
   - Adjust worker count for performance

3. **Setup monitoring:**
   - Configure Docker Desktop limits
   - Setup log rotation
   - Monitor resource usage

4. **Plan production:**
   - Setup PostgreSQL (optional)
   - Configure Nginx reverse proxy
   - Setup SSL certificates
   - Plan backup strategy

---

## 📞 Support

- **Docker Issues:** Check Docker Desktop logs
- **Application Issues:** Check container logs: `docker-compose logs -f`
- **GitHub Issues:** https://github.com/umaraliyev0101/AI_for_Education/issues

---

**Your Docker deployment is ready! 🐳**

Run `docker-compose up -d` and access http://localhost:8001/docs to get started!
