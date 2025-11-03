# PowerShell startup script for Windows

Write-Host "🚀 Starting AI Education Platform..." -ForegroundColor Green

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Run database initialization
Write-Host "📊 Initializing database..." -ForegroundColor Yellow
python backend\init_db.py

# Start the application
Write-Host "🔧 Starting application server..." -ForegroundColor Yellow
$env:PORT = if ($env:PORT) { $env:PORT } else { "8001" }

uvicorn backend.main:app --host 0.0.0.0 --port $env:PORT --reload
