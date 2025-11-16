# 🪟 Windows Quick Start Guide

## 🚀 Option 1: Complete Setup (First Time)

**Run this if you're setting up for the first time:**

```cmd
setup_and_start.bat
```

This script will:
1. ✅ Check Python and dependencies
2. 📦 Install all required packages
3. ⬇️ Download the Llama model (~17GB, 10-30 min)
4. 📁 Create necessary directories
5. 🗄️ Initialize the database
6. 🚀 Start the backend server

**Total time:** 15-45 minutes (mostly model download)

---

## ⚡ Option 2: Quick Start (Already Set Up)

**If you've already run the setup once:**

```cmd
quick_start.bat
```

Starts the server immediately without checks.

---

## 🔄 Option 3: Smart Start (Checks + Downloads if Needed)

**Recommended for daily use:**

```cmd
start_backend.bat
```

This script will:
- ✅ Check if Python is installed
- ✅ Verify dependencies
- ✅ Check if model is downloaded (downloads if missing)
- ✅ Start the server

**Only downloads model if it's not already present!**

---

## 📥 Option 4: Download Model Only

**If you just want to download the model:**

```powershell
.\download_llama_model.ps1
```

---

## 🛠️ Manual Setup

If scripts don't work, here's the manual process:

### 1. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 2. Download Model
```powershell
.\download_llama_model.ps1
```

### 3. Create .env File
```cmd
copy .env.example .env
```

Edit `.env` and set your configuration.

### 4. Start Server
```cmd
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## 🌐 Accessing the Application

Once the server is running:

- **API Docs (Swagger):** http://localhost:8001/docs
- **API Docs (ReDoc):** http://localhost:8001/redoc
- **Health Check:** http://localhost:8001/health

---

## 📋 System Requirements

- **OS:** Windows 10/11
- **Python:** 3.8 or higher
- **RAM:** 16GB+ (for CPU inference) or 8GB+ VRAM (for GPU)
- **Disk:** 20GB+ free space
- **Internet:** Required for initial model download

---

## 🐛 Troubleshooting

### Issue: "Python not found"
**Solution:** Install Python from https://www.python.org/downloads/
- ✅ Check "Add Python to PATH" during installation

### Issue: "Port 8001 already in use"
**Solution:** 
```cmd
# Kill process using port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Issue: "Model download failed"
**Solution:**
1. Check internet connection
2. Run download script again (it will resume)
3. Or download manually:
   ```cmd
   pip install huggingface-hub[cli]
   huggingface-cli download behbudiy/Llama-3.1-8B-Instruct-Uz
   ```

### Issue: "Out of memory"
**Solution:**
- Close other applications
- Or install quantization: `pip install bitsandbytes`
- Or use GPU if available

### Issue: "Module not found"
**Solution:**
```cmd
pip install -r requirements.txt --upgrade
```

---

## 🔧 Batch File Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `setup_and_start.bat` | Complete first-time setup | First run ever |
| `start_backend.bat` | Smart start with checks | Daily use (recommended) |
| `quick_start.bat` | Instant start, no checks | When everything is set up |
| `download_llama_model.ps1` | Download model only | To pre-download model |

---

## 📝 Notes

- **Model Location:** `%USERPROFILE%\.cache\huggingface\hub\`
- **Database:** `ai_education.db` (SQLite)
- **Uploads:** `uploads/` directory
- **Model Size:** ~17GB (one-time download)

---

## 🎯 Quick Commands

```cmd
REM Check Python version
python --version

REM Check if model is downloaded
dir "%USERPROFILE%\.cache\huggingface\hub\models--behbudiy--Llama-3.1-8B-Instruct-Uz"

REM Install/update dependencies
pip install -r requirements.txt

REM Start server manually
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

REM Run tests
pytest

REM Check logs
type backend.log
```

---

## 🆘 Need Help?

1. Check the error message carefully
2. Look for solutions in this README
3. Check the main README.md for more details
4. Run diagnostic: `.\diagnose_llm_complete.sh` (Git Bash) or check PowerShell equivalent

---

## ✅ Success Indicators

When everything is working, you'll see:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Visit http://localhost:8001/docs to verify! 🎉
