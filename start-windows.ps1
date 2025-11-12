# ============================================================================
# Windows Start Script for AI Education Platform
# ============================================================================
# PowerShell script to start the application on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting AI Education Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Please run setup-windows.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Please run setup-windows.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Check if database exists
if (-not (Test-Path "ai_education.db")) {
    Write-Host "Initializing database..." -ForegroundColor Yellow
    python -m backend.init_db
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the API at:" -ForegroundColor Yellow
Write-Host "  - API: http://localhost:8001" -ForegroundColor White
Write-Host "  - Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - OpenAPI: http://localhost:8001/openapi.json" -ForegroundColor White
Write-Host ""
Write-Host "Default credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the server
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
