@echo off
REM AI Education System - Windows Startup Script
REM This script runs the unified startup (dependencies installed globally)

echo ================================================
echo AI EDUCATION SYSTEM - WINDOWS STARTUP
echo ================================================

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Run the unified startup script
echo Starting AI Education System...
python start_all.py

echo System stopped
pause
