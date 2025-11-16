@echo off
REM ============================================================================
REM AI Education Backend Startup Script (Windows)
REM Automatically downloads model (if needed) and starts the backend
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors (using PowerShell for colored output)
set "PS_GREEN=Write-Host '✓' -ForegroundColor Green -NoNewline"
set "PS_RED=Write-Host '✗' -ForegroundColor Red -NoNewline"
set "PS_YELLOW=Write-Host '⚠' -ForegroundColor Yellow -NoNewline"
set "PS_CYAN=Write-Host 'ℹ' -ForegroundColor Cyan -NoNewline"

REM ============================================================================
REM Header
REM ============================================================================

cls
echo ============================================================================
echo 🚀 AI Education Backend Startup
echo ============================================================================
echo.
echo Date: %date% %time%
echo.

REM ============================================================================
REM Check Python
REM ============================================================================

echo [1/7] Checking Python...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "%PS_RED%; Write-Host ' Python not found'"
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
powershell -Command "%PS_GREEN%; Write-Host ' %PYTHON_VERSION%'"
echo.

REM ============================================================================
REM Check pip
REM ============================================================================

echo [2/7] Checking pip...
echo.

where pip >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "%PS_RED%; Write-Host ' pip not found'"
    echo.
    echo Installing pip...
    python -m ensurepip --upgrade
)

for /f "tokens=*" %%i in ('pip --version') do set PIP_VERSION=%%i
powershell -Command "%PS_GREEN%; Write-Host ' %PIP_VERSION%'"
echo.

REM ============================================================================
REM Install Dependencies
REM ============================================================================

echo [3/7] Checking dependencies...
echo.

if not exist "requirements.txt" (
    powershell -Command "%PS_RED%; Write-Host ' requirements.txt not found'"
    pause
    exit /b 1
)

echo Installing/updating dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    powershell -Command "%PS_RED%; Write-Host ' Failed to install dependencies'"
    echo.
    echo Run manually: pip install -r requirements.txt
    pause
    exit /b 1
)

powershell -Command "%PS_GREEN%; Write-Host ' Dependencies installed'"
echo.

REM ============================================================================
REM Check Model Files
REM ============================================================================

echo [4/7] Checking model files...
echo.

set "MODEL_CACHE=%USERPROFILE%\.cache\huggingface\hub\models--behbudiy--Llama-3.1-8B-Instruct-Uz"
set "MODEL_EXISTS=0"

if exist "%MODEL_CACHE%\snapshots" (
    REM Check if snapshots directory has content
    dir /b "%MODEL_CACHE%\snapshots" | findstr "^" >nul
    if !errorlevel! equ 0 (
        REM Check for essential files
        set "FILES_OK=1"
        
        for /d %%D in ("%MODEL_CACHE%\snapshots\*") do (
            if not exist "%%D\config.json" set "FILES_OK=0"
            if not exist "%%D\tokenizer.json" set "FILES_OK=0"
        )
        
        if !FILES_OK! equ 1 (
            set "MODEL_EXISTS=1"
            powershell -Command "%PS_GREEN%; Write-Host ' Model found in cache'"
            
            REM Show model size
            for /f "tokens=3" %%s in ('dir /-c "%MODEL_CACHE%" ^| findstr "bytes"') do set MODEL_SIZE=%%s
            echo    Location: %MODEL_CACHE%
            echo.
        )
    )
)

if !MODEL_EXISTS! equ 0 (
    powershell -Command "%PS_YELLOW%; Write-Host ' Model not found or incomplete'"
    echo.
    echo The Llama model needs to be downloaded (~17GB).
    echo This is a ONE-TIME download and will take 10-30 minutes.
    echo.
    set /p DOWNLOAD_CHOICE="Download model now? (y/n): "
    
    if /i "!DOWNLOAD_CHOICE!"=="y" (
        echo.
        echo Starting model download...
        echo.
        
        REM Check if PowerShell download script exists
        if exist "download_llama_model.ps1" (
            powershell -ExecutionPolicy Bypass -File "download_llama_model.ps1"
        ) else (
            REM Use Python as fallback
            echo Using Python to download model...
            python -c "from huggingface_hub import snapshot_download; import os; os.environ['HF_HUB_ENABLE_HF_TRANSFER']='1'; snapshot_download('behbudiy/Llama-3.1-8B-Instruct-Uz', resume_download=True)"
        )
        
        if !errorlevel! neq 0 (
            powershell -Command "%PS_RED%; Write-Host ' Model download failed'"
            echo.
            echo Please check your internet connection and try again.
            echo Or run manually: download_llama_model.ps1
            pause
            exit /b 1
        )
        
        powershell -Command "%PS_GREEN%; Write-Host ' Model downloaded successfully'"
        echo.
    ) else (
        powershell -Command "%PS_YELLOW%; Write-Host ' Skipping model download'"
        echo.
        echo Warning: Backend will start but Q&A features may not work without the model.
        echo You can download it later by running: download_llama_model.ps1
        echo.
        timeout /t 3 >nul
    )
)

REM ============================================================================
REM Check Database
REM ============================================================================

echo [5/7] Checking database...
echo.

if not exist "ai_education.db" (
    powershell -Command "%PS_YELLOW%; Write-Host ' Database not found, will be created on first run'"
    echo.
) else (
    powershell -Command "%PS_GREEN%; Write-Host ' Database found'"
    echo.
)

REM ============================================================================
REM Check Environment Variables
REM ============================================================================

echo [6/7] Checking environment...
echo.

if not exist ".env" (
    powershell -Command "%PS_YELLOW%; Write-Host ' .env file not found'"
    echo.
    echo Creating .env from template...
    
    if exist ".env.example" (
        copy .env.example .env >nul
        powershell -Command "%PS_GREEN%; Write-Host ' Created .env file'"
    ) else (
        echo Creating default .env...
        (
            echo # AI Education System Configuration
            echo.
            echo # Database
            echo DATABASE_URL=sqlite:///./ai_education.db
            echo.
            echo # Security
            echo SECRET_KEY=your-secret-key-change-this-in-production
            echo ALGORITHM=HS256
            echo ACCESS_TOKEN_EXPIRE_MINUTES=30
            echo.
            echo # LLM Model
            echo LLM_MODEL_NAME=behbudiy/Llama-3.1-8B-Instruct-Uz
            echo.
            echo # Directories
            echo UPLOAD_DIR=uploads
            echo AUDIO_DIR=uploads/audio
            echo MATERIALS_DIR=uploads/materials
            echo PRESENTATIONS_DIR=uploads/presentations
            echo FACES_DIR=uploads/faces
            echo VECTOR_STORES_DIR=vector_stores
        ) > .env
        powershell -Command "%PS_GREEN%; Write-Host ' Created default .env file'"
    )
    echo.
) else (
    powershell -Command "%PS_GREEN%; Write-Host ' Environment configured'"
    echo.
)

REM ============================================================================
REM Start Backend
REM ============================================================================

echo [7/7] Starting backend server...
echo.
echo ============================================================================
echo 🌐 Server Configuration
echo ============================================================================
echo.
echo   URL: http://localhost:8001
echo   Docs: http://localhost:8001/docs
echo   API: http://localhost:8001/api
echo.
echo ============================================================================
echo 📋 Useful Commands
echo ============================================================================
echo.
echo   Ctrl+C          Stop the server
echo   Ctrl+Break      Force stop
echo.
echo ============================================================================
echo.
echo Starting in 3 seconds...
timeout /t 3 >nul
echo.

REM Start uvicorn
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

REM Check if server exited with error
if %errorlevel% neq 0 (
    echo.
    echo ============================================================================
    powershell -Command "%PS_RED%; Write-Host ' Server failed to start'"
    echo ============================================================================
    echo.
    echo Common issues:
    echo   1. Port 8001 already in use
    echo   2. Missing dependencies
    echo   3. Database errors
    echo.
    echo Check the error messages above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
powershell -Command "%PS_GREEN%; Write-Host ' Server stopped normally'"
echo ============================================================================
echo.
pause
