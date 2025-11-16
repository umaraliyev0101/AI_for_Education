@echo off
REM ============================================================================
REM Quick Start - For users who already have everything set up
REM ============================================================================

echo ============================================================================
echo 🚀 AI Education - Quick Start
echo ============================================================================
echo.

REM Quick checks
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python not found. Run setup_and_start.bat first.
    pause
    exit /b 1
)

echo Starting backend server...
echo.
echo 🌐 Server: http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

pause
