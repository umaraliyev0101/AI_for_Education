# 🚀 Deployment Guide - AI Education Platform

Complete guide for deploying the AI Education Platform locally and on a server.

---

## 📋 Table of Contents

1. [Local Deployment (Windows)](#local-deployment-windows)
2. [Local Deployment (Linux/Mac)](#local-deployment-linuxmac)
3. [Server Deployment (Production)](#server-deployment-production)
4. [Docker Deployment](#docker-deployment)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🖥️ Local Deployment (Windows)

### Prerequisites
- Python 3.11+ installed
- Git installed
- Webcam (for face recognition features)
- 8GB+ RAM recommended

### Step 1: Clone & Setup

```powershell
# Clone the repository
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 2: Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt

# For GPU support (if you have NVIDIA GPU):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Configure Environment

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

Update these critical settings in `.env`:
```env
SECRET_KEY=your-very-secure-secret-key-minimum-32-characters-long
DATABASE_URL=sqlite:///./ai_education.db
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:8001"]
```

### Step 4: Initialize Database

```powershell
# Run database initialization
python -m backend.init_db
```

This creates:
- Database with all tables
- Default admin user (username: `admin`, password: `admin123`)
- Sample data (optional)

### Step 5: Start the Server

```powershell
# Development mode with auto-reload
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Or use the simpler command:
python -m uvicorn backend.main:app --reload --port 8001
```

### Step 6: Verify Installation

1. Open browser: http://localhost:8001
2. API Docs: http://localhost:8001/docs
3. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`

---

## 🐧 Local Deployment (Linux/Mac)

### Prerequisites
- Python 3.11+ installed
- Git installed
- Webcam (for face recognition)
- 8GB+ RAM recommended

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# For GPU support (if you have NVIDIA GPU):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
vim .env
```

Update these settings:
```env
SECRET_KEY=your-very-secure-secret-key-minimum-32-characters-long
DATABASE_URL=sqlite:///./ai_education.db
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:8001"]
```

### Step 4: Initialize Database

```bash
# Run database initialization
python -m backend.init_db
```

### Step 5: Start the Server

```bash
# Development mode
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Or make start.sh executable and run it
chmod +x start.sh
./start.sh
```

### Step 6: Verify Installation

Visit http://localhost:8001/docs and login with admin/admin123

---

## 🌐 Server Deployment (Production)

### Option A: Ubuntu Server (Recommended)

#### Prerequisites
- Ubuntu 20.04+ server
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt)
- Sudo access

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
sudo apt install nginx supervisor -y

# Install Git
sudo apt install git -y
```

#### Step 2: Create Application User

```bash
# Create dedicated user for the app
sudo adduser --disabled-password --gecos "" aiedu
sudo usermod -aG sudo aiedu

# Switch to app user
sudo su - aiedu
```

#### Step 3: Clone and Setup Application

```bash
# Clone repository
cd /home/aiedu
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

#### Step 4: Configure Environment

```bash
# Create production .env file
cp .env.example .env
nano .env
```

**Production `.env` configuration:**
```env
# Security
SECRET_KEY=generate-a-very-strong-secret-key-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
APP_NAME=AI Education Platform
APP_VERSION=1.0.0
DEBUG=False

# Database (SQLite for single server, PostgreSQL for production)
DATABASE_URL=sqlite:///./ai_education.db

# CORS - Replace with your actual domains
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# File Storage
UPLOAD_DIR=/home/aiedu/AI_for_Education/uploads
FACE_IMAGES_DIR=/home/aiedu/AI_for_Education/uploads/faces
MATERIALS_DIR=/home/aiedu/AI_for_Education/uploads/materials
PRESENTATIONS_DIR=/home/aiedu/AI_for_Education/uploads/presentations
AUDIO_DIR=/home/aiedu/AI_for_Education/uploads/audio
VECTOR_STORES_DIR=/home/aiedu/AI_for_Education/vector_stores

# AI Models
STT_MODEL=lucio/xls-r-uzbek-cv8
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
TTS_VOICE=uz-UZ-SardorNeural

# Processing
MAX_UPLOAD_SIZE=52428800
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K_DOCUMENTS=3
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Step 5: Initialize Database

```bash
# Create necessary directories
mkdir -p uploads/faces uploads/materials uploads/presentations uploads/audio uploads/slides
mkdir -p vector_stores

# Initialize database
python -m backend.init_db
```

#### Step 6: Configure Gunicorn

Create systemd service file:

```bash
sudo nano /etc/systemd/system/aiedu.service
```

Add this configuration:
```ini
[Unit]
Description=AI Education Platform
After=network.target

[Service]
Type=notify
User=aiedu
Group=aiedu
WorkingDirectory=/home/aiedu/AI_for_Education
Environment="PATH=/home/aiedu/AI_for_Education/venv/bin"
ExecStart=/home/aiedu/AI_for_Education/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001 \
    --timeout 300 \
    --keepalive 5 \
    --access-logfile /home/aiedu/AI_for_Education/logs/access.log \
    --error-logfile /home/aiedu/AI_for_Education/logs/error.log \
    --log-level info \
    backend.main:app

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Create logs directory:
```bash
mkdir -p /home/aiedu/AI_for_Education/logs
```

#### Step 7: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/aiedu
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 50M;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long-running requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Static files
    location /uploads/ {
        alias /home/aiedu/AI_for_Education/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API documentation
    location /docs {
        proxy_pass http://127.0.0.1:8001/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/aiedu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 8: Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically configure HTTPS
# Test auto-renewal
sudo certbot renew --dry-run
```

#### Step 9: Start the Application

```bash
# Enable and start the service
sudo systemctl enable aiedu
sudo systemctl start aiedu

# Check status
sudo systemctl status aiedu

# View logs
sudo journalctl -u aiedu -f
```

#### Step 10: Setup Firewall

```bash
# Configure UFW firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

---

## 🐳 Docker Deployment

### Step 1: Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/faces uploads/materials uploads/presentations \
             uploads/audio uploads/slides vector_stores logs

# Expose port
EXPOSE 8001

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run initialization and start server
CMD ["sh", "-c", "python -m backend.init_db && gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001 --timeout 300"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: aiedu-backend
    ports:
      - "8001:8001"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite:///./ai_education.db
      - DEBUG=False
      - CORS_ORIGINS=["*"]
    volumes:
      - ./uploads:/app/uploads
      - ./vector_stores:/app/vector_stores
      - ./ai_education.db:/app/ai_education.db
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  uploads:
  vector_stores:
  database:
  logs:
```

### Step 3: Create .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
.env
.git/
.gitignore
*.log
.vscode/
.idea/
*.md
!README.md
```

### Step 4: Build and Run

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

---

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key (32+ chars) | Use `openssl rand -hex 32` |
| `DATABASE_URL` | Database connection string | `sqlite:///./ai_education.db` |
| `DEBUG` | Debug mode (False in production) | `False` |
| `CORS_ORIGINS` | Allowed CORS origins | `["https://yourdomain.com"]` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 | JWT token expiration (minutes) |
| `MAX_UPLOAD_SIZE` | 52428800 | Max file upload size (bytes) |
| `UPLOAD_DIR` | `./uploads` | Upload directory path |
| `STT_MODEL` | `lucio/xls-r-uzbek-cv8` | Speech-to-text model |
| `EMBEDDING_MODEL` | `sentence-transformers/...` | Embedding model for RAG |

### Generating Secure Keys

```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using OpenSSL
openssl rand -hex 32

# Using PowerShell (Windows)
[Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

---

## ✅ Post-Deployment

### 1. Change Default Credentials

```bash
# Login with admin/admin123
# Go to /api/auth/me and update password
```

Or use the API:
```bash
curl -X PUT http://yourdomain.com/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"admin123","new_password":"new_secure_password"}'
```

### 2. Create Additional Users

```bash
# Use API or create programmatically
curl -X POST http://yourdomain.com/api/auth/register \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher1",
    "email": "teacher1@school.uz",
    "password": "secure_password",
    "role": "teacher"
  }'
```

### 3. Configure Backup

```bash
# Create backup script
sudo nano /home/aiedu/backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/aiedu/backups"
APP_DIR="/home/aiedu/AI_for_Education"

mkdir -p $BACKUP_DIR

# Backup database
cp $APP_DIR/ai_education.db $BACKUP_DIR/ai_education_$DATE.db

# Backup uploads (faces, materials, etc.)
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz $APP_DIR/uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
chmod +x /home/aiedu/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/aiedu/backup.sh
```

### 4. Setup Monitoring

Install monitoring tools:
```bash
# Install htop for system monitoring
sudo apt install htop -y

# Monitor application logs
tail -f /home/aiedu/AI_for_Education/logs/error.log

# Monitor system logs
sudo journalctl -u aiedu -f

# Check service status
sudo systemctl status aiedu nginx
```

### 5. Performance Tuning

**Gunicorn Workers:**
```
workers = (2 × CPU cores) + 1
```

**For 4 CPU cores:**
```bash
--workers 9
```

**Memory per worker:**
- Approximately 500MB-1GB per worker
- Ensure sufficient RAM

---

## 🔧 Troubleshooting

### Issue: Port 8001 already in use

```powershell
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux
lsof -ti:8001 | xargs kill -9
```

### Issue: Database locked

```bash
# Close all connections and restart
sudo systemctl restart aiedu
```

### Issue: Face recognition not working

```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera works!' if cap.isOpened() else 'Camera failed')"

# Reinstall dependencies
pip install --force-reinstall facenet-pytorch opencv-python
```

### Issue: Model download fails

```bash
# Manually download models
python -c "from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor; \
           model = Wav2Vec2ForCTC.from_pretrained('lucio/xls-r-uzbek-cv8'); \
           processor = Wav2Vec2Processor.from_pretrained('lucio/xls-r-uzbek-cv8')"
```

### Issue: Permission denied on uploads

```bash
# Fix permissions
sudo chown -R aiedu:aiedu /home/aiedu/AI_for_Education/uploads
sudo chmod -R 755 /home/aiedu/AI_for_Education/uploads
```

### Issue: Nginx 502 Bad Gateway

```bash
# Check if application is running
sudo systemctl status aiedu

# Check logs
sudo journalctl -u aiedu -n 50

# Restart services
sudo systemctl restart aiedu nginx
```

### Issue: SSL certificate renewal fails

```bash
# Manual renewal
sudo certbot renew --force-renewal

# Check renewal timer
sudo systemctl status certbot.timer
```

---

## 📊 Monitoring & Logs

### Application Logs

```bash
# Real-time logs
sudo journalctl -u aiedu -f

# Last 100 lines
sudo journalctl -u aiedu -n 100

# Logs from specific date
sudo journalctl -u aiedu --since "2025-11-01"
```

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Application Logs

```bash
# Application-specific logs
tail -f /home/aiedu/AI_for_Education/logs/error.log
tail -f /home/aiedu/AI_for_Education/logs/access.log
```

---

## 🎯 Quick Commands Reference

### Local Development

```powershell
# Windows
.\venv\Scripts\activate
uvicorn backend.main:app --reload --port 8001

# Linux/Mac
source venv/bin/activate
uvicorn backend.main:app --reload --port 8001
```

### Production Server

```bash
# Start/Stop/Restart
sudo systemctl start aiedu
sudo systemctl stop aiedu
sudo systemctl restart aiedu

# View status
sudo systemctl status aiedu

# View logs
sudo journalctl -u aiedu -f

# Nginx commands
sudo systemctl restart nginx
sudo nginx -t  # Test configuration
```

### Database Management

```bash
# Backup database
cp ai_education.db ai_education_backup_$(date +%Y%m%d).db

# Reset database (CAUTION: Deletes all data)
rm ai_education.db
python -m backend.init_db
```

---

## 📱 Testing Your Deployment

### 1. Test API Endpoints

```bash
# Health check
curl http://localhost:8001/health

# Login
curl -X POST http://localhost:8001/api/auth/login \
  -F "username=admin" \
  -F "password=admin123"

# Get students (replace TOKEN)
curl -X GET http://localhost:8001/api/students/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Test via Browser

1. Visit: http://localhost:8001/docs
2. Login with admin credentials
3. Try different API endpoints
4. Upload test files
5. Test face recognition features

---

## 🆘 Support

For issues and questions:
- GitHub Issues: https://github.com/umaraliyev0101/AI_for_Education/issues
- Email: support@yourdomain.com

---

**Deployment completed! Your AI Education Platform is now running! 🎉**
