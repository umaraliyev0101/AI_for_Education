# Deployment Guide - AI Education Platform

## Table of Contents
- [Docker Deployment](#docker-deployment)
- [Manual Deployment](#manual-deployment)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Docker Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- 10GB free disk space

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

4. **Check logs**
```bash
docker-compose logs -f app
```

5. **Access the application**
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

### Docker Commands

**Build image**
```bash
docker build -t ai-education:latest .
```

**Run container**
```bash
docker run -d \
  --name ai-education \
  -p 8001:8001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/vector_stores:/app/vector_stores \
  -e SECRET_KEY=your-secret-key \
  ai-education:latest
```

**Stop and remove**
```bash
docker-compose down
```

**Rebuild and restart**
```bash
docker-compose up -d --build
```

**View logs**
```bash
docker-compose logs -f
```

**Enter container shell**
```bash
docker-compose exec app bash
```

---

## Manual Deployment

### Prerequisites
- Python 3.11+
- PostgreSQL or SQLite
- FFmpeg
- PortAudio

### Installation Steps

1. **Install system dependencies (Ubuntu/Debian)**
```bash
sudo apt-get update
sudo apt-get install -y \
  python3.11 \
  python3.11-venv \
  python3-dev \
  gcc \
  g++ \
  make \
  libffi-dev \
  libssl-dev \
  libsndfile1 \
  ffmpeg \
  portaudio19-dev
```

2. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**
```bash
pip install --upgrade pip
pip install -r backend_requirements.txt
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python backend/init_db.py
```

6. **Run the application**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

---

## Production Deployment

### Using Gunicorn (Recommended)

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Run with Gunicorn**
```bash
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

### Systemd Service (Linux)

Create `/etc/systemd/system/ai-education.service`:

```ini
[Unit]
Description=AI Education Platform
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/ai_education
Environment="PATH=/opt/ai_education/venv/bin"
ExecStart=/opt/ai_education/venv/bin/gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --timeout 300
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ai-education
sudo systemctl start ai-education
sudo systemctl status ai-education
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/ai-education`:

```nginx
upstream ai_education {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    # WebSocket support
    location /ws {
        proxy_pass http://ai_education;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # API endpoints
    location / {
        proxy_pass http://ai_education;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/ai-education /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Environment Variables

### Required Variables
```bash
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=sqlite:///./ai_education.db
```

### Optional Variables
```bash
# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Paths
UPLOADS_DIR=./uploads
MATERIALS_DIR=./uploads/materials
PRESENTATIONS_DIR=./uploads/presentations
FACES_DIR=./uploads/faces
AUDIO_DIR=./uploads/audio
SLIDES_DIR=./uploads/slides
VECTOR_STORES_DIR=./vector_stores

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com

# External Services
OPENAI_API_KEY=sk-...
HUGGINGFACE_TOKEN=hf_...

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

### Generate SECRET_KEY

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

---

## Cloud Deployment

### Deploy to AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04, t3.medium or larger)

2. **Connect and install Docker**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

3. **Clone and deploy**
```bash
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education
cp .env.example .env
# Edit .env
docker-compose up -d
```

4. **Configure security group**
- Allow inbound: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Allow outbound: All

### Deploy to Google Cloud Run

1. **Build and push to Google Container Registry**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-education

# Or use Cloud Build
gcloud run deploy ai-education \
  --image gcr.io/PROJECT_ID/ai-education \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --timeout 300
```

### Deploy to Heroku

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create app and deploy**
```bash
heroku login
heroku create your-app-name
heroku stack:set container
git push heroku main
```

3. **Set environment variables**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgresql://...
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs app

# Check container status
docker-compose ps

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Database issues
```bash
# Reinitialize database
docker-compose exec app python backend/init_db.py

# Or delete and recreate
rm ai_education.db
docker-compose restart app
```

### Permission issues
```bash
# Fix upload directory permissions
sudo chown -R 1000:1000 uploads/ vector_stores/
sudo chmod -R 755 uploads/ vector_stores/
```

### Port already in use
```bash
# Find and kill process using port 8001
sudo lsof -i :8001
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8002:8001"
```

### Out of memory
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory > 8GB

# Or limit workers
environment:
  - WORKERS=2
```

### WebSocket connection issues
- Check firewall allows WebSocket connections
- Verify Nginx WebSocket proxy configuration
- Check browser console for errors

---

## Monitoring

### Check health
```bash
curl http://localhost:8001/health
```

### View resource usage
```bash
docker stats ai_education_app
```

### Application logs
```bash
docker-compose logs -f --tail=100 app
```

---

## Backup and Restore

### Backup
```bash
# Backup database
docker-compose exec app sqlite3 ai_education.db ".backup backup.db"

# Backup uploads
tar -czf uploads-backup.tar.gz uploads/

# Backup vector stores
tar -czf vectors-backup.tar.gz vector_stores/
```

### Restore
```bash
# Restore database
docker cp backup.db ai_education_app:/app/ai_education.db

# Restore uploads
tar -xzf uploads-backup.tar.gz

# Restart
docker-compose restart
```

---

## Scaling

### Horizontal Scaling
```bash
# Scale app instances
docker-compose up -d --scale app=3

# Use load balancer (Nginx, HAProxy, etc.)
```

### Vertical Scaling
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

---

## Support
For issues or questions:
- GitHub Issues: https://github.com/umaraliyev0101/AI_for_Education/issues
- Documentation: See README.md
