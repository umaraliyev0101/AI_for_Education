@echo off
chcp 65001 >nul
color 0B
title AI Education Backend Server

echo ============================================================
echo    AI for Education - Backend Server
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ ERROR: Virtual environment not found
    echo Please run install_and_check.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

echo Checking CUDA availability...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
echo.

echo Starting FastAPI server...
echo Server will be available at: http://localhost:8001
echo API Documentation: http://localhost:8001/docs
echo.
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001

pause
