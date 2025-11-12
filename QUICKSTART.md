# 🚀 Quick Start Guide - AI Education Platform

Get your AI Education Platform running in 5 minutes!

---

## 🖥️ **For Windows Users**

### Step 1: Open PowerShell

Right-click on Start menu → **Windows PowerShell** (or **Terminal**)

### Step 2: Navigate to Project

```powershell
cd D:\Projects\AI_in_Education
```

### Step 3: Run Setup Script

```powershell
# Allow script execution (one-time only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\setup-windows.ps1
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create .env file with secure key
- ✅ Initialize database
- ✅ Create default admin user

### Step 4: Start the Server

```powershell
.\start-windows.ps1
```

### Step 5: Access the Application

Open your browser:
- **API**: http://localhost:8001
- **Documentation**: http://localhost:8001/docs

**Login credentials:**
- Username: `admin`
- Password: `admin123`

### That's it! 🎉

To stop the server: Press `Ctrl+C`

---

## 🐧 **For Linux/Mac Users**

### Step 1: Open Terminal

Open your terminal application

### Step 2: Navigate to Project

```bash
cd ~/AI_in_Education
# or wherever you cloned the project
```

### Step 3: Run Setup Script

```bash
# Make script executable
chmod +x setup-unix.sh

# Run setup
./setup-unix.sh
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create .env file with secure key
- ✅ Initialize database
- ✅ Create default admin user

### Step 4: Start the Server

```bash
# Make start script executable
chmod +x start.sh

# Start the server
./start.sh
```

Or manually:

```bash
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 5: Access the Application

Open your browser:
- **API**: http://localhost:8001
- **Documentation**: http://localhost:8001/docs

**Login credentials:**
- Username: `admin`
- Password: `admin123`

### That's it! 🎉

To stop the server: Press `Ctrl+C`

---

## 🐳 **Using Docker** (Recommended for Production)

### Prerequisites
- Docker installed
- Docker Compose installed

### Step 1: Clone and Navigate

```bash
cd ~/AI_in_Education
```

### Step 2: Create .env File

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Important:** Set a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Build and Start

```bash
# Build the image
docker-compose build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 4: Access the Application

- **API**: http://localhost:8001
- **Documentation**: http://localhost:8001/docs

**Login:** `admin` / `admin123`

### Management Commands

```bash
# Stop containers
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f web

# Execute commands in container
docker-compose exec web python -m backend.init_db
```

---

## 🌐 **Production Server Deployment**

For deploying to a production server (Ubuntu/Debian):

### Quick Command

```bash
# Clone repository
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education

# Run automated setup
chmod +x setup-unix.sh
./setup-unix.sh

# For production with Nginx + SSL:
# See DEPLOYMENT.md for complete guide
```

### Key Production Steps

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv nginx supervisor certbot
   ```

2. **Setup application**
   ```bash
   ./setup-unix.sh
   ```

3. **Configure systemd service**
   ```bash
   sudo cp aiedu.service /etc/systemd/system/
   sudo systemctl enable aiedu
   sudo systemctl start aiedu
   ```

4. **Configure Nginx**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/aiedu
   sudo ln -s /etc/nginx/sites-available/aiedu /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Setup SSL**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

**📖 For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 📚 **Next Steps**

After installation:

1. **Change default password** (Important!)
   - Login to http://localhost:8001/docs
   - Use the `/api/auth/change-password` endpoint

2. **Create users**
   - Create teacher accounts
   - Create viewer accounts

3. **Add students**
   - Use the `/api/students/` endpoints
   - Enroll student faces

4. **Create lessons**
   - Upload lesson materials
   - Upload presentations
   - Schedule lessons

5. **Test features**
   - Test face recognition attendance
   - Test Q&A with audio
   - Test presentation delivery

---

## 🔧 **Troubleshooting**

### Port 8001 Already in Use

**Windows:**
```powershell
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8001 | xargs kill -9
```

### Python Not Found

Install Python 3.11+:
- **Windows**: https://www.python.org/downloads/
- **Linux**: `sudo apt install python3.11`
- **Mac**: `brew install python@3.11`

### Virtual Environment Issues

**Windows:**
```powershell
Remove-Item -Recurse -Force venv
python -m venv venv
```

**Linux/Mac:**
```bash
rm -rf venv
python3 -m venv venv
```

### Dependencies Installation Failed

```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

### Database Errors

```bash
# Reset database (WARNING: Deletes all data!)
rm ai_education.db
python -m backend.init_db
```

### Permission Denied

**Linux/Mac:**
```bash
chmod +x setup-unix.sh start.sh
```

---

## 📞 **Getting Help**

- 📖 **Full Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- ✅ **Deployment Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/umaraliyev0101/AI_for_Education/issues)
- 📧 **Email**: support@yourdomain.com

---

## 🎯 **Quick Reference**

### Essential Commands

**Windows:**
```powershell
# Setup
.\setup-windows.ps1

# Start server
.\start-windows.ps1

# Or manually
.\venv\Scripts\activate
uvicorn backend.main:app --reload --port 8001
```

**Linux/Mac:**
```bash
# Setup
./setup-unix.sh

# Start server
./start.sh

# Or manually
source venv/bin/activate
uvicorn backend.main:app --reload --port 8001
```

**Docker:**
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f
```

### Default Credentials

- Username: `admin`
- Password: `admin123`

**⚠️ Change this immediately in production!**

### Important URLs

- API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- OpenAPI Schema: http://localhost:8001/openapi.json
- Health Check: http://localhost:8001/health

---

**🎉 Enjoy your AI Education Platform!**

Need more details? Check out [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive documentation.
