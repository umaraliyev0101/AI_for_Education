@echo off
REM AI Education System - Windows Startup Script
REM This script activates the virtual environment and runs the unified startup

echo ================================================
echo AI EDUCATION SYSTEM - WINDOWS STARTUP
echo ================================================

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at venv\Scripts\activate.bat
    echo Please run setup_and_start.bat first to create the environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python not found in virtual environment
    pause
    exit /b 1
)

REM Run the unified startup script
echo Starting AI Education System...
python start_all.py

REM Deactivate when done
call venv\Scripts\deactivate.bat

echo System stopped
pause
