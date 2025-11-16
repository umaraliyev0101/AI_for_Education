@echo off
REM ============================================================================
REM Complete Setup and Start Script
REM First-time setup + model download + backend start
REM ============================================================================

setlocal enabledelayedexpansion

cls
echo ============================================================================
echo 🎓 AI Education System - Complete Setup
echo ============================================================================
echo.
echo This script will:
echo   1. Check system requirements
echo   2. Install Python dependencies
echo   3. Download the Llama model (~17GB)
echo   4. Initialize the database
echo   5. Start the backend server
echo.
echo Estimated time: 15-45 minutes (depending on internet speed)
echo.
pause
echo.

REM ============================================================================
REM Step 1: System Requirements
REM ============================================================================

echo ============================================================================
echo [1/6] Checking System Requirements
echo ============================================================================
echo.

REM Check Python
echo Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python not found
    echo.
    echo Please install Python 3.8 or higher:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%V in ('python --version') do set PYTHON_VERSION=%%V
echo ✓ Python %PYTHON_VERSION%

REM Check disk space
echo.
echo Checking disk space...
for /f "tokens=3" %%a in ('dir /-c "%cd%" ^| findstr "bytes free"') do set FREE_SPACE=%%a
set /a FREE_GB=%FREE_SPACE:~0,-9%
echo Available: %FREE_GB% GB

if %FREE_GB% LSS 20 (
    echo ⚠ Warning: Only %FREE_GB%GB free. Recommended: 20GB+
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i "!CONTINUE!" neq "y" exit /b 1
) else (
    echo ✓ Sufficient disk space
)

echo.
pause

REM ============================================================================
REM Step 2: Install Dependencies
REM ============================================================================

echo ============================================================================
echo [2/6] Installing Dependencies
echo ============================================================================
echo.

if not exist "requirements.txt" (
    echo ✗ requirements.txt not found
    echo Make sure you're in the correct directory.
    pause
    exit /b 1
)

echo Installing Python packages (this may take 5-10 minutes)...
echo.

python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠ Failed to upgrade pip, continuing...
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ✗ Failed to install dependencies
    echo.
    echo Try running manually:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ✓ Dependencies installed
echo.
pause

REM ============================================================================
REM Step 3: Download Model
REM ============================================================================

echo ============================================================================
echo [3/6] Downloading Llama Model
echo ============================================================================
echo.

set "MODEL_CACHE=%USERPROFILE%\.cache\huggingface\hub\models--behbudiy--Llama-3.1-8B-Instruct-Uz"

REM Check if model already exists
if exist "%MODEL_CACHE%\snapshots" (
    echo ✓ Model already downloaded
    echo Location: %MODEL_CACHE%
    echo.
    set /p REDOWNLOAD="Re-download model? (y/n): "
    if /i "!REDOWNLOAD!" neq "y" goto :skip_download
)

echo Model: behbudiy/Llama-3.1-8B-Instruct-Uz
echo Size: ~17GB
echo Time: 10-30 minutes (with optimizations)
echo.
echo The download will resume automatically if interrupted.
echo.
set /p START_DOWNLOAD="Start download now? (y/n): "

if /i "!START_DOWNLOAD!" neq "y" (
    echo.
    echo ⚠ Skipping model download
    echo You can download it later by running: download_llama_model.ps1
    goto :skip_download
)

echo.
echo Starting download...
echo.

REM Install download optimization tools
pip install -q -U "huggingface-hub[cli,hf_transfer]" tqdm

REM Set optimization environment variables
set HF_HUB_ENABLE_HF_TRANSFER=1
set HF_HUB_DOWNLOAD_TIMEOUT=300

REM Download using PowerShell script if available
if exist "download_llama_model.ps1" (
    echo Using optimized download script...
    powershell -ExecutionPolicy Bypass -File "download_llama_model.ps1"
) else (
    echo Using huggingface-cli...
    python -m huggingface_cli download behbudiy/Llama-3.1-8B-Instruct-Uz --resume-download
)

if %errorlevel% neq 0 (
    echo.
    echo ✗ Model download failed
    echo.
    echo Troubleshooting:
    echo   1. Check your internet connection
    echo   2. Try running again (download will resume)
    echo   3. Run manually: download_llama_model.ps1
    echo.
    set /p CONTINUE_WITHOUT="Continue without model? (y/n): "
    if /i "!CONTINUE_WITHOUT!" neq "y" (
        pause
        exit /b 1
    )
) else (
    echo.
    echo ✓ Model downloaded successfully
)

:skip_download
echo.
pause

REM ============================================================================
REM Step 4: Create Directories
REM ============================================================================

echo ============================================================================
echo [4/6] Creating Directories
echo ============================================================================
echo.

REM Create upload directories
if not exist "uploads" mkdir uploads
if not exist "uploads\audio" mkdir uploads\audio
if not exist "uploads\materials" mkdir uploads\materials
if not exist "uploads\presentations" mkdir uploads\presentations
if not exist "uploads\faces" mkdir uploads\faces
if not exist "uploads\slides" mkdir uploads\slides

REM Create vector stores directory
if not exist "vector_stores" mkdir vector_stores
if not exist "vector_stores\lesson_materials" mkdir vector_stores\lesson_materials

REM Create lesson materials directory
if not exist "lesson_materials" mkdir lesson_materials

echo ✓ Created directory structure:
echo   - uploads/
echo   - vector_stores/
echo   - lesson_materials/
echo.
pause

REM ============================================================================
REM Step 5: Initialize Database
REM ============================================================================

echo ============================================================================
echo [5/6] Initializing Database
echo ============================================================================
echo.

if exist "ai_education.db" (
    echo Database already exists
    echo.
    set /p RESET_DB="Reset database? (y/n): "
    if /i "!RESET_DB!"=="y" (
        del ai_education.db
        echo ✓ Old database deleted
    )
)

if not exist ".env" (
    echo Creating .env configuration...
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        (
            echo # AI Education System Configuration
            echo DATABASE_URL=sqlite:///./ai_education.db
            echo SECRET_KEY=change-this-secret-key-in-production
            echo ALGORITHM=HS256
            echo ACCESS_TOKEN_EXPIRE_MINUTES=30
            echo LLM_MODEL_NAME=behbudiy/Llama-3.1-8B-Instruct-Uz
        ) > .env
    )
    echo ✓ Created .env file
)

echo.
echo Initializing database...
python -c "from backend.database import engine; from backend.models import user, student, lesson, qa_session, attendance; import backend.models.user as user_models; user_models.Base.metadata.create_all(bind=engine); print('✓ Database initialized')"

if %errorlevel% neq 0 (
    echo ⚠ Database initialization may have issues
    echo The database will be created automatically on first run
)

echo.
pause

REM ============================================================================
REM Step 6: Start Backend
REM ============================================================================

echo ============================================================================
echo [6/6] Starting Backend Server
echo ============================================================================
echo.
echo ✅ Setup Complete!
echo.
echo ============================================================================
echo 🌐 Server Information
echo ============================================================================
echo.
echo   Backend API:  http://localhost:8001
echo   API Docs:     http://localhost:8001/docs
echo   ReDoc:        http://localhost:8001/redoc
echo.
echo ============================================================================
echo 📋 Default Admin Credentials
echo ============================================================================
echo.
echo   You'll need to create an admin user through the API.
echo   Visit http://localhost:8001/docs and use /api/auth/register
echo.
echo ============================================================================
echo.
echo Starting server in 3 seconds...
echo Press Ctrl+C to stop the server.
echo.
timeout /t 3 >nul

REM Start the backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

echo.
echo ============================================================================
echo Server stopped
echo ============================================================================
echo.
echo To restart the server, run: start_backend.bat
echo.
pause
