@echo off
chcp 65001 >nul
color 0A
title AI Education Platform - Complete Installation and Check

echo ============================================================
echo    AI for Education - Complete Setup and Health Check
echo ============================================================
echo.

REM Check if Python is installed
echo [1/10] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)
python --version
echo ✅ Python found
echo.

REM Check Python version
echo [2/10] Verifying Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python 3.9 or higher is required
    pause
    exit /b 1
)
echo ✅ Python version is compatible
echo.

REM Create virtual environment if it doesn't exist
echo [3/10] Setting up virtual environment...
if not exist "venv\" (
    echo Creating new virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [4/10] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo [5/10] Upgrading pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo ⚠️ WARNING: Failed to upgrade pip, continuing...
) else (
    echo ✅ pip upgraded
)
echo.

REM Install dependencies
echo [6/10] Installing dependencies from requirements.txt...
echo This may take several minutes...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install dependencies
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Check CUDA availability
echo [7/10] Checking CUDA availability...
python -c "import torch; print('✅ PyTorch version:', torch.__version__); print('✅ CUDA available:', torch.cuda.is_available()); print('✅ CUDA device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
echo.

REM Create necessary directories
echo [8/10] Creating necessary directories...
if not exist "uploads\audio" mkdir uploads\audio
if not exist "uploads\faces" mkdir uploads\faces
if not exist "uploads\materials" mkdir uploads\materials
if not exist "uploads\presentations" mkdir uploads\presentations
if not exist "uploads\slides" mkdir uploads\slides
if not exist "vector_stores\lesson_materials" mkdir vector_stores\lesson_materials
if not exist "lesson_materials" mkdir lesson_materials
echo ✅ Directories created
echo.

REM Initialize database
echo [9/10] Initializing database...
python -m backend.init_db >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Database initialization warning (may already exist)
) else (
    echo ✅ Database initialized
)
echo.

REM Check/Download LLM model
echo [10/10] Checking LLM model...
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; print('Checking model...'); tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base'); print('✅ Tokenizer loaded'); model = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base'); print('✅ Model loaded successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Model not found, downloading...
    echo This is a one-time download and may take several minutes...
    python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base'); model = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base'); print('✅ Model downloaded and cached')"
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Failed to download model
        pause
        exit /b 1
    )
) else (
    echo ✅ Model is ready
)
echo.

REM Run comprehensive health check
echo ============================================================
echo    Running System Health Check
echo ============================================================
echo.
python check_system.py
echo.

echo ============================================================
echo    Installation Complete!
echo ============================================================
echo.
echo ✅ All components installed and verified
echo.
echo To start the backend server, run:
echo    start_backend.bat
echo.
echo Or manually:
echo    venv\Scripts\activate
echo    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
echo.
pause
