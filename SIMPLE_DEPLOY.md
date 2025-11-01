# 🚀 Simple Deployment Guide

## Quick Start

This is an AI Education Platform built with FastAPI. Here's how to deploy it.

---

## Option 1: Using Docker Compose (Recommended)

### Prerequisites
- Docker & Docker Compose installed
- Server with at least 4GB RAM

### Deploy Steps

1. **Clone the repository:**
```bash
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education
```

2. **Create environment file:**
```bash
nano .env
```

Add:
```env
SECRET_KEY=your-very-secret-key-minimum-32-characters-long
DATABASE_URL=sqlite:///./ai_education.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. **Pull and start:**
```bash
# Pull latest image from GitHub Container Registry
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest

# Start the application
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker logs ai-education-app -f
```

4. **Verify:**
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy"}
```

5. **Access:**
- API Docs: http://your-server-ip:8001/docs
- Health: http://your-server-ip:8001/health

---

## Option 2: With Auto-Updates (Watchtower)

Automatically update when new versions are pushed to GitHub.

1. **Login to GitHub Container Registry:**
```bash
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin
```

2. **Start with Watchtower:**
```bash
docker-compose -f docker-compose.watchtower.yml up -d
```

Watchtower will check for updates every 5 minutes and automatically deploy them.

---

## Option 3: Manual Docker Run

If you don't want to use Docker Compose:

```bash
docker run -d \
  --name ai-education-app \
  --restart unless-stopped \
  -p 8001:8001 \
  -e SECRET_KEY="your-secret-key" \
  -e DATABASE_URL="sqlite:///./ai_education.db" \
  -v ./uploads:/app/uploads \
  -v ./vector_stores:/app/vector_stores \
  -v ./ai_education.db:/app/ai_education.db \
  ghcr.io/umaraliyev0101/ai_for_education:latest
```

---

## Configuration

### Environment Variables

Required:
- `SECRET_KEY` - Secret key for JWT tokens (min 32 chars)
- `DATABASE_URL` - Database connection (default: SQLite)

Optional:
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)

### Ports

- `8001` - Main application port

### Volumes

- `./uploads` - User uploaded files
- `./vector_stores` - Vector database
- `./ai_education.db` - SQLite database

---

## Updating

### With Watchtower (Automatic)
Push to GitHub → Auto-builds → Auto-deploys (25-30 min total)

### Manual Update
```bash
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## Monitoring

### Check Status
```bash
docker ps
docker logs ai-education-app -f
```

### Health Check
```bash
curl http://localhost:8001/health
```

### Resource Usage
```bash
docker stats
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs ai-education-app

# Common issues:
# - Port 8001 in use: Change port in docker-compose
# - Permission error: sudo chown -R 1000:1000 .
```

### App Returns 503
```bash
# Wait 30-60 seconds (ML models loading)
# Check logs for errors
docker logs ai-education-app -f
```

### Out of Memory
```bash
# Reduce workers in docker-compose.prod.yml:
# command: gunicorn ... --workers 2
```

---

## Backup

### Database
```bash
cp ai_education.db ai_education.db.backup
```

### All Data
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz \
  ai_education.db uploads/ vector_stores/
```

---

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Enable firewall: `ufw allow 8001/tcp`
- [ ] Use HTTPS (add nginx reverse proxy)
- [ ] Regular backups
- [ ] Keep Docker updated

---

## Support

- GitHub: https://github.com/umaraliyev0101/AI_for_Education
- Issues: https://github.com/umaraliyev0101/AI_for_Education/issues

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ Port 8001
│  (Docker)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   SQLite    │
└─────────────┘
```

---

## Files Overview

- `Dockerfile.prod` - Production Docker image
- `docker-compose.prod.yml` - Production deployment config
- `docker-compose.watchtower.yml` - Auto-update config
- `start.sh` - Application startup script
- `nginx.conf` - Nginx reverse proxy config (optional)
- `requirements.txt` - Python dependencies
- `.github/workflows/docker-build.yml` - Auto-build on push

---

That's it! 🎉

**Deployment time:** 5 minutes
**Update time:** 30 minutes (automatic with Watchtower)
