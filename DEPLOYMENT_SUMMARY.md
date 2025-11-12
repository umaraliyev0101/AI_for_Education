# 📦 Deployment Package - AI Education Platform

## 🎯 Overview

This deployment package contains everything you need to deploy the AI Education Platform both locally and on production servers.

---

## 📁 Deployment Files Overview

### Core Files
| File | Purpose | Usage |
|------|---------|-------|
| `QUICKSTART.md` | 5-minute quick start guide | First-time setup |
| `DEPLOYMENT.md` | Complete deployment documentation | Reference guide |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step checklist | During deployment |
| `README.md` | Project overview | Understanding the project |

### Configuration Files
| File | Purpose | Usage |
|------|---------|-------|
| `.env.example` | Environment template | Copy to `.env` |
| `requirements.txt` | Python dependencies | pip install |
| `pyproject.toml` | Project metadata | Python packaging |
| `Dockerfile` | Docker image definition | Docker deployment |
| `docker-compose.yml` | Multi-container setup | Docker orchestration |
| `.dockerignore` | Docker build exclusions | Optimize Docker builds |
| `nginx.conf` | Nginx configuration | Production web server |
| `aiedu.service` | Systemd service | Production service |

### Setup Scripts
| File | Platform | Purpose |
|------|----------|---------|
| `setup-windows.ps1` | Windows | Automated setup |
| `start-windows.ps1` | Windows | Start server |
| `setup-unix.sh` | Linux/Mac | Automated setup |
| `start.sh` | Linux/Mac | Start server (dev/prod) |

---

## 🚀 Quick Deployment Guide

### 1️⃣ **Local Development (Windows)**

```powershell
# Navigate to project
cd D:\Projects\AI_in_Education

# Run setup (one-time)
.\setup-windows.ps1

# Start server
.\start-windows.ps1
```

**Access:** http://localhost:8001/docs  
**Login:** admin / admin123

---

### 2️⃣ **Local Development (Linux/Mac)**

```bash
# Navigate to project
cd ~/AI_in_Education

# Run setup (one-time)
chmod +x setup-unix.sh start.sh
./setup-unix.sh

# Start server
./start.sh
```

**Access:** http://localhost:8001/docs  
**Login:** admin / admin123

---

### 3️⃣ **Docker Deployment**

```bash
# Setup
cp .env.example .env
# Edit .env with secure values

# Build and run
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f
```

**Access:** http://localhost:8001/docs  
**Login:** admin / admin123

---

### 4️⃣ **Production Server (Ubuntu)**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11 python3.11-venv nginx certbot -y

# Create app user
sudo adduser --disabled-password --gecos "" aiedu
sudo su - aiedu

# Clone and setup
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education
./setup-unix.sh

# Configure environment
nano .env  # Set production values

# Exit to root user
exit

# Setup systemd service
sudo cp /home/aiedu/AI_for_Education/aiedu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aiedu
sudo systemctl start aiedu

# Setup Nginx
sudo cp /home/aiedu/AI_for_Education/nginx.conf /etc/nginx/sites-available/aiedu
# Edit nginx.conf with your domain
sudo nano /etc/nginx/sites-available/aiedu
sudo ln -s /etc/nginx/sites-available/aiedu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Verify deployment
sudo systemctl status aiedu
sudo systemctl status nginx
curl https://yourdomain.com/health
```

**Access:** https://yourdomain.com/docs  
**Login:** admin / admin123

---

## 🔐 Security Configuration

### 1. Generate Secure Secret Key

**Python:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**OpenSSL:**
```bash
openssl rand -hex 32
```

**PowerShell:**
```powershell
[Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

### 2. Update .env File

```env
SECRET_KEY=your-generated-key-here
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com"]
```

### 3. Change Default Password

After first login, immediately change the admin password via API or database.

---

## 📊 Environment Variables Reference

### Required Variables

```env
# Security
SECRET_KEY=<generate-secure-key>  # REQUIRED

# Application
DEBUG=False                         # False in production
DATABASE_URL=sqlite:///./ai_education.db
CORS_ORIGINS=["https://yourdomain.com"]

# AI Models
STT_MODEL=lucio/xls-r-uzbek-cv8
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
TTS_VOICE=uz-UZ-SardorNeural
```

### Optional Variables

```env
# Token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File upload limit (bytes)
MAX_UPLOAD_SIZE=52428800

# Server configuration
PORT=8001
GUNICORN_WORKERS=4

# Processing
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K_DOCUMENTS=3
```

---

## 🧪 Testing Your Deployment

### 1. Health Check

```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy"}
```

### 2. Login Test

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -F "username=admin" \
  -F "password=admin123"
# Expected: {"access_token":"...","token_type":"bearer"}
```

### 3. API Documentation

Visit: http://localhost:8001/docs

### 4. Full Feature Test

Use the API documentation to test:
- ✅ Student management
- ✅ Lesson creation
- ✅ Face enrollment
- ✅ Attendance marking
- ✅ Q&A system
- ✅ Presentation delivery

---

## 📝 Post-Deployment Tasks

### Immediate (Day 1)
1. ✅ Change default admin password
2. ✅ Create additional users (teachers, viewers)
3. ✅ Test all critical features
4. ✅ Monitor logs for errors
5. ✅ Verify SSL certificate
6. ✅ Test from external network

### First Week
1. ✅ Enroll first students
2. ✅ Upload lesson materials
3. ✅ Conduct pilot lesson
4. ✅ Setup backup script
5. ✅ Train staff on system
6. ✅ Gather user feedback

### First Month
1. ✅ Review performance metrics
2. ✅ Optimize if needed
3. ✅ Update documentation
4. ✅ Test disaster recovery
5. ✅ Update dependencies
6. ✅ Security review

---

## 🔧 Common Commands

### Local Development

```bash
# Start dev server
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
uvicorn backend.main:app --reload --port 8001

# Initialize database
python -m backend.init_db

# View logs
tail -f logs/error.log
```

### Production Server

```bash
# Service management
sudo systemctl start aiedu
sudo systemctl stop aiedu
sudo systemctl restart aiedu
sudo systemctl status aiedu

# View logs
sudo journalctl -u aiedu -f
tail -f /home/aiedu/AI_for_Education/logs/error.log

# Nginx management
sudo systemctl restart nginx
sudo nginx -t  # Test configuration

# Database backup
cp ai_education.db ai_education_backup_$(date +%Y%m%d).db
```

### Docker

```bash
# Container management
docker-compose up -d        # Start
docker-compose down         # Stop
docker-compose restart      # Restart
docker-compose logs -f web  # View logs

# Execute commands
docker-compose exec web python -m backend.init_db
docker-compose exec web bash
```

---

## 🐛 Troubleshooting

### Application Won't Start

1. Check Python version: `python --version` (need 3.11+)
2. Check virtual environment: `which python` (should be in venv)
3. Check .env file exists: `ls -la .env`
4. Check port availability: `lsof -i :8001` (Linux) or `netstat -ano | findstr :8001` (Windows)
5. Check logs: `tail -f logs/error.log`

### Database Issues

```bash
# Verify database file
ls -lh ai_education.db

# Reset database (WARNING: Deletes data!)
rm ai_education.db
python -m backend.init_db
```

### Permission Issues (Linux)

```bash
# Fix file permissions
sudo chown -R aiedu:aiedu /home/aiedu/AI_for_Education
sudo chmod -R 755 /home/aiedu/AI_for_Education
sudo chmod -R 777 /home/aiedu/AI_for_Education/uploads
```

### Nginx 502 Bad Gateway

```bash
# Check if app is running
sudo systemctl status aiedu

# Check app logs
sudo journalctl -u aiedu -n 50

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart aiedu nginx
```

### Model Download Issues

```bash
# Manually download models
python -c "
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
model = Wav2Vec2ForCTC.from_pretrained('lucio/xls-r-uzbek-cv8')
processor = Wav2Vec2Processor.from_pretrained('lucio/xls-r-uzbek-cv8')
print('Models downloaded successfully')
"
```

---

## 📦 Backup & Recovery

### Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/aiedu/backups"
APP_DIR="/home/aiedu/AI_for_Education"

mkdir -p $BACKUP_DIR

# Backup database
cp $APP_DIR/ai_education.db $BACKUP_DIR/ai_education_$DATE.db

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz $APP_DIR/uploads/

# Backup .env
cp $APP_DIR/.env $BACKUP_DIR/.env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Schedule Daily Backups

```bash
# Make backup script executable
chmod +x /home/aiedu/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/aiedu/backup.sh
```

### Recovery

```bash
# Stop application
sudo systemctl stop aiedu

# Restore database
cp /home/aiedu/backups/ai_education_YYYYMMDD.db /home/aiedu/AI_for_Education/ai_education.db

# Restore uploads
tar -xzf /home/aiedu/backups/uploads_YYYYMMDD.tar.gz -C /home/aiedu/AI_for_Education/

# Start application
sudo systemctl start aiedu
```

---

## 📊 Monitoring

### System Resources

```bash
# CPU and memory
htop

# Disk space
df -h

# Check application memory
ps aux | grep gunicorn
```

### Application Logs

```bash
# Real-time logs
sudo journalctl -u aiedu -f

# Last 100 lines
sudo journalctl -u aiedu -n 100

# Today's logs
sudo journalctl -u aiedu --since today

# Errors only
sudo journalctl -u aiedu -p err
```

### Nginx Logs

```bash
# Access log
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log
```

---

## 📈 Performance Tuning

### Gunicorn Workers

```bash
# Formula: (2 × CPU cores) + 1
# For 4 cores: 9 workers

# Edit in .env
GUNICORN_WORKERS=9
```

### Database Optimization (PostgreSQL)

If using PostgreSQL instead of SQLite:

```env
DATABASE_URL=postgresql://user:password@localhost/ai_education
```

Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

### Redis Caching (Optional)

For improved performance:

```bash
# Install Redis
sudo apt install redis-server

# Update .env
REDIS_URL=redis://localhost:6379/0
```

---

## 🔄 Updating the Application

### Pull Latest Changes

```bash
# Navigate to app directory
cd /home/aiedu/AI_for_Education

# Pull updates
git pull origin main

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Run migrations (if any)
# alembic upgrade head

# Restart application
sudo systemctl restart aiedu
```

### Rolling Back

```bash
# List available commits
git log --oneline -10

# Rollback to specific commit
git checkout <commit-hash>

# Restart
sudo systemctl restart aiedu
```

---

## 📞 Support & Resources

### Documentation
- 📖 [QUICKSTART.md](QUICKSTART.md) - 5-minute quick start
- 📖 [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
- 📖 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment checklist
- 📖 [README.md](README.md) - Project overview

### Online Resources
- 🌐 Repository: https://github.com/umaraliyev0101/AI_for_Education
- 🐛 Issues: https://github.com/umaraliyev0101/AI_for_Education/issues
- 📧 Email: support@yourdomain.com

### Community
- 💬 Discussions: GitHub Discussions
- 🤝 Contributing: See CONTRIBUTING.md
- 📝 License: MIT License

---

## ✅ Deployment Checklist Summary

Use [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for the complete checklist.

**Pre-Deployment:**
- [ ] Python 3.11+ installed
- [ ] Dependencies installed
- [ ] .env configured
- [ ] Database initialized
- [ ] SSL certificate obtained (production)

**Security:**
- [ ] SECRET_KEY generated
- [ ] DEBUG=False (production)
- [ ] Default password changed
- [ ] Firewall configured
- [ ] CORS origins set

**Testing:**
- [ ] Health check passes
- [ ] Login works
- [ ] All features tested
- [ ] External access verified
- [ ] Performance acceptable

**Post-Deployment:**
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Documentation updated
- [ ] Staff trained
- [ ] Users notified

---

## 🎉 Success!

Your AI Education Platform is now deployed and ready to use!

**Default Access:**
- 🌐 URL: http://localhost:8001 (local) or https://yourdomain.com (production)
- 📚 Docs: /docs
- 🔐 Login: admin / admin123

**Next Steps:**
1. Change default password
2. Create user accounts
3. Add students
4. Create lessons
5. Start teaching!

---

**Made with ❤️ for Education**

For questions or issues, check the documentation or open an issue on GitHub.

Good luck with your deployment! 🚀
