# Quick Start Guide - AI Education Platform

## 🚀 Deploy in 5 Minutes

### Option 1: Docker (Recommended)

1. **Prerequisites**
   - Install [Docker](https://docs.docker.com/get-docker/)
   - Install [Docker Compose](https://docs.docker.com/compose/install/)

2. **Clone and Configure**
   ```bash
   git clone https://github.com/umaraliyev0101/AI_for_Education.git
   cd AI_for_Education
   cp .env.example .env
   ```

3. **Generate Secret Key**
   ```bash
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
   ```

4. **Start Application**
   ```bash
   # Development
   docker-compose up -d

   # Production
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Access Application**
   - API: http://localhost:8001
   - API Docs: http://localhost:8001/docs
   - Health Check: http://localhost:8001/health

6. **Default Login**
   - Admin: `admin` / `admin123`
   - Teacher: `teacher` / `teacher123`

---

### Option 2: Local Development (Windows)

1. **Prerequisites**
   - Python 3.11+
   - FFmpeg
   - Git

2. **Clone Repository**
   ```powershell
   git clone https://github.com/umaraliyev0101/AI_for_Education.git
   cd AI_for_Education
   ```

3. **Create Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Setup Environment**
   ```powershell
   copy .env.example .env
   # Edit .env and set SECRET_KEY
   ```

6. **Initialize Database**
   ```powershell
   python backend/init_db.py
   ```

7. **Start Server**
   ```powershell
   # Using the startup script
   .\start.ps1

   # Or manually
   uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
   ```

---

### Option 3: Linux/Mac

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3.11 python3-pip ffmpeg
   ```

2. **Clone and Setup**
   ```bash
   git clone https://github.com/umaraliyev0101/AI_for_Education.git
   cd AI_for_Education
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure**
   ```bash
   cp .env.example .env
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
   ```

4. **Run**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

---

## 📦 Build Docker Image

### Development Build
```bash
docker build -t ai-education:dev .
docker run -p 8001:8001 ai-education:dev
```

### Production Build
```bash
docker build -f Dockerfile.prod -t ai-education:latest .
docker run -p 8001:8001 -e SECRET_KEY=your-secret ai-education:latest
```

### Tag and Push to Registry
```bash
# Docker Hub
docker tag ai-education:latest yourusername/ai-education:latest
docker push yourusername/ai-education:latest

# GitHub Container Registry
docker tag ai-education:latest ghcr.io/yourusername/ai-education:latest
docker push ghcr.io/yourusername/ai-education:latest

# AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag ai-education:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-education:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-education:latest
```

---

## 🌐 Deploy to Cloud

### Deploy to AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu, t3.medium+)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Deploy
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education
sudo docker-compose -f docker-compose.prod.yml up -d
```

### Deploy to DigitalOcean

```bash
# 1. Create Droplet (Ubuntu 22.04, 4GB RAM+)
# 2. SSH into droplet
# 3. Follow same steps as AWS EC2
```

### Deploy to Heroku

```bash
heroku login
heroku create your-app-name
heroku stack:set container
git push heroku main
```

### Deploy to Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-education
gcloud run deploy --image gcr.io/PROJECT_ID/ai-education --platform managed
```

---

## ✅ Verify Deployment

```bash
# Check health
curl http://localhost:8001/health

# Check API docs
curl http://localhost:8001/docs

# Test authentication
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

---

## 🐛 Troubleshooting

### Container won't start
```bash
docker-compose logs app
docker-compose down -v
docker-compose up --build
```

### Port already in use
```bash
# Find process
netstat -ano | findstr :8001  # Windows
lsof -i :8001                  # Linux/Mac

# Kill process
taskkill /PID <PID> /F         # Windows
kill -9 <PID>                  # Linux/Mac
```

### Database locked
```bash
rm ai_education.db
python backend/init_db.py
```

### Permission denied (Linux)
```bash
sudo chown -R $USER:$USER uploads/ vector_stores/
chmod -R 755 uploads/ vector_stores/
```

---

## 📊 Monitoring

```bash
# View logs
docker-compose logs -f app

# Check resources
docker stats

# View running containers
docker ps
```

---

## 🛑 Stop Application

```bash
# Docker
docker-compose down

# Local development
Ctrl + C
```

---

## 🔄 Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or for production
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📚 Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide
- Check [README.md](README.md) for API documentation
- Visit http://localhost:8001/docs for interactive API docs

---

## 🆘 Get Help

- Issues: https://github.com/umaraliyev0101/AI_for_Education/issues
- Documentation: See README.md and DEPLOYMENT.md
