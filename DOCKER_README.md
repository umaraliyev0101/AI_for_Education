# 🐳 Docker Deployment - AI Education Platform

Complete Docker deployment guide for the AI Education Platform.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Files Overview](#files-overview)
3. [Build Commands](#build-commands)
4. [Run Commands](#run-commands)
5. [Testing](#testing)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Generate secret key and add to .env
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
```

### 3. Build and Run
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Test Deployment
```bash
# Windows
.\test_deployment.ps1

# Linux/Mac
chmod +x test_deployment.sh
./test_deployment.sh
```

### 5. Access Application
- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **Health**: http://localhost:8001/health

**Default Login:**
- Admin: `admin` / `admin123`
- Teacher: `teacher` / `teacher123`

---

## 📁 Files Overview

### Docker Files
```
├── Dockerfile                   # Development Docker image
├── Dockerfile.prod             # Production-optimized image
├── docker-compose.yml          # Development compose config
├── docker-compose.prod.yml     # Production compose config
└── .dockerignore               # Files to exclude from build
```

### Configuration Files
```
├── .env.example                # Environment variables template
├── nginx.conf                  # Nginx reverse proxy config
├── start.sh                    # Linux/Mac startup script
└── start.ps1                   # Windows startup script
```

### Testing
```
├── test_deployment.sh          # Bash deployment test
└── test_deployment.ps1         # PowerShell deployment test
```

### Documentation
```
├── DOCKER_README.md            # This file
├── DOCKER_SUMMARY.md           # Deployment summary
├── DEPLOYMENT.md               # Comprehensive deployment guide
└── QUICKSTART.md               # Quick start guide
```

---

## 🔨 Build Commands

### Development Build
```bash
docker build -t ai-education:dev .
```

### Production Build
```bash
docker build -f Dockerfile.prod -t ai-education:latest .
```

### Build with Docker Compose
```bash
# Development
docker-compose build

# Production
docker-compose -f docker-compose.prod.yml build
```

### Build Without Cache
```bash
docker build --no-cache -t ai-education:latest .
```

---

## ▶️ Run Commands

### Using Docker Compose (Recommended)
```bash
# Development - start in background
docker-compose up -d

# Development - start with logs
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Using Docker Run
```bash
# Basic run
docker run -d \
  --name ai-education \
  -p 8001:8001 \
  ai-education:latest

# With volumes and environment
docker run -d \
  --name ai-education \
  -p 8001:8001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/vector_stores:/app/vector_stores \
  -v $(pwd)/ai_education.db:/app/ai_education.db \
  -e SECRET_KEY=your-secret-key-here \
  -e ALLOWED_ORIGINS=http://localhost:3000 \
  --restart unless-stopped \
  ai-education:latest

# Stop
docker stop ai-education

# Remove
docker rm ai-education
```

---

## 🧪 Testing

### Run Test Script
```bash
# Windows
.\test_deployment.ps1

# Linux/Mac
chmod +x test_deployment.sh
./test_deployment.sh
```

### Manual Testing
```bash
# Health check
curl http://localhost:8001/health

# API docs
curl http://localhost:8001/docs

# Test login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

---

## ⚙️ Configuration

### Environment Variables (.env)

**Required:**
```bash
SECRET_KEY=your-super-secret-key-change-this
```

**Optional:**
```bash
# Database
DATABASE_URL=sqlite:///./ai_education.db

# Server
GUNICORN_WORKERS=4
PORT=8001

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Paths
UPLOADS_DIR=/app/uploads
MATERIALS_DIR=/app/uploads/materials
PRESENTATIONS_DIR=/app/uploads/presentations
FACES_DIR=/app/uploads/faces
AUDIO_DIR=/app/uploads/audio
SLIDES_DIR=/app/uploads/slides
VECTOR_STORES_DIR=/app/vector_stores

# Logging
DEBUG=False
LOG_LEVEL=INFO
```

### Generate Secret Key
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# PowerShell
[System.Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

---

## 🔍 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app

# Without docker-compose
docker logs -f ai-education
```

### Check Container Status
```bash
# List running containers
docker ps

# Check health
docker inspect --format='{{.State.Health.Status}}' ai-education

# View resource usage
docker stats ai-education
```

### Access Container Shell
```bash
# With docker-compose
docker-compose exec app bash

# Without docker-compose
docker exec -it ai-education bash
```

---

## 🐛 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs app
```

**Common issues:**
- Port 8001 already in use
- Missing environment variables
- Database locked

**Solutions:**
```bash
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild
docker-compose up -d --build
```

### Port Already in Use

**Find process using port:**
```bash
# Windows
netstat -ano | findstr :8001

# Linux/Mac
lsof -i :8001
```

**Kill process:**
```bash
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
```

**Or change port in docker-compose.yml:**
```yaml
ports:
  - "8002:8001"  # Use port 8002 instead
```

### Database Issues

**Reinitialize database:**
```bash
# Enter container
docker-compose exec app bash

# Run init script
python backend/init_db.py

# Exit
exit
```

**Or delete and recreate:**
```bash
rm ai_education.db
docker-compose restart app
```

### Permission Issues (Linux)

```bash
# Fix upload directory permissions
sudo chown -R $USER:$USER uploads/ vector_stores/
sudo chmod -R 755 uploads/ vector_stores/
```

### Out of Memory

**Increase Docker memory:**
- Docker Desktop: Settings → Resources → Memory → 8GB

**Or limit workers:**
```yaml
# docker-compose.yml
environment:
  - GUNICORN_WORKERS=2
```

### Slow Build

**Use build cache:**
```bash
docker-compose build
```

**Or pull from registry:**
```bash
docker pull yourusername/ai-education:latest
```

### WebSocket Connection Fails

**Check Nginx configuration:**
```nginx
location /ws {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 📦 Push to Registry

### Docker Hub
```bash
# Login
docker login

# Tag
docker tag ai-education:latest yourusername/ai-education:latest

# Push
docker push yourusername/ai-education:latest

# Pull (on another machine)
docker pull yourusername/ai-education:latest
```

### GitHub Container Registry
```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag
docker tag ai-education:latest ghcr.io/yourusername/ai-education:latest

# Push
docker push ghcr.io/yourusername/ai-education:latest
```

### AWS ECR
```bash
# Login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag
docker tag ai-education:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/ai-education:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-education:latest
```

---

## 🔄 Update & Maintenance

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backup Data
```bash
# Backup database
docker cp ai_education_app:/app/ai_education.db ./backup.db

# Backup uploads
tar -czf backup-uploads-$(date +%Y%m%d).tar.gz uploads/

# Backup vectors
tar -czf backup-vectors-$(date +%Y%m%d).tar.gz vector_stores/
```

### Restore Data
```bash
# Restore database
docker cp ./backup.db ai_education_app:/app/ai_education.db

# Restore uploads
tar -xzf backup-uploads-*.tar.gz

# Restart
docker-compose restart
```

### Clean Up
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f

# Clean everything
docker system prune -a --volumes -f
```

---

## 🌐 Production Deployment

### With Nginx (Recommended)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

This includes:
- Nginx reverse proxy on port 80
- Rate limiting
- WebSocket support
- Production-optimized settings

### Without Nginx
```bash
# Use development compose but with prod settings
docker-compose up -d
```

### Cloud Deployment

**AWS EC2:**
```bash
ssh -i key.pem ubuntu@ec2-ip
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education
docker-compose -f docker-compose.prod.yml up -d
```

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-education
gcloud run deploy --image gcr.io/PROJECT_ID/ai-education
```

**Heroku:**
```bash
heroku container:login
heroku container:push web
heroku container:release web
```

---

## 📊 Performance

### Image Size
- Development: ~4-5 GB
- Production: ~3-4 GB

### Build Time
- First build: 10-15 minutes
- Cached build: 1-2 minutes

### Memory Usage
- Minimum: 2 GB
- Recommended: 4 GB
- Optimal: 8 GB

### Scaling
```bash
# Scale to 3 instances
docker-compose up -d --scale app=3

# Use with load balancer (Nginx, HAProxy, etc.)
```

---

## ✅ Checklist

Before production deployment:

- [ ] Set strong SECRET_KEY
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring
- [ ] Test all endpoints
- [ ] Review security settings
- [ ] Document your configuration
- [ ] Set up CI/CD (optional)
- [ ] Configure log rotation
- [ ] Set resource limits
- [ ] Test disaster recovery

---

## 📚 Additional Resources

- **DEPLOYMENT.md** - Detailed deployment guide
- **QUICKSTART.md** - 5-minute quick start
- **README.md** - API documentation
- **docs/** - Additional documentation

---

## 🆘 Get Help

- **GitHub Issues**: https://github.com/umaraliyev0101/AI_for_Education/issues
- **Check Logs**: `docker-compose logs -f`
- **Health Check**: http://localhost:8001/health
- **API Docs**: http://localhost:8001/docs

---

## 🎉 Success!

Your AI Education Platform is now Dockerized! 🐳

**Next Steps:**
1. Test locally: `docker-compose up -d`
2. Run tests: `./test_deployment.sh`
3. Deploy to production
4. Set up monitoring
5. Configure backups

Happy deploying! 🚀
