# ============================================================================
# Docker Deployment Script for Windows
# ============================================================================
# Quick deployment script for AI Education Platform using Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Deployment - AI Education Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found! Please install Docker Desktop" -ForegroundColor Red
    Write-Host "  Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose not found!" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if .env exists
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    
    # Generate secure secret key
    Write-Host "Generating secure secret key..." -ForegroundColor Yellow
    $secretKey = python -c "import secrets; print(secrets.token_hex(32))"
    
    # Update .env file
    $envContent = Get-Content ".env"
    $envContent = $envContent -replace "SECRET_KEY=your-secret-key-change-in-production.*", "SECRET_KEY=$secretKey"
    $envContent = $envContent -replace "DEBUG=True", "DEBUG=False"
    $envContent | Set-Content ".env"
    
    Write-Host "✓ .env file created with secure secret key" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Review and update .env file with your settings!" -ForegroundColor Yellow
    Write-Host "  - Update CORS_ORIGINS if needed" -ForegroundColor Gray
    Write-Host "  - Press any key to continue or Ctrl+C to exit and edit .env" -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}

Write-Host ""

# Ask if user wants to build or just start
Write-Host "Deployment Options:" -ForegroundColor Yellow
Write-Host "  1. Fresh deployment (build + start)" -ForegroundColor White
Write-Host "  2. Start existing containers" -ForegroundColor White
Write-Host "  3. Rebuild and restart" -ForegroundColor White
Write-Host "  4. Stop containers" -ForegroundColor White
Write-Host "  5. View logs" -ForegroundColor White
Write-Host "  6. Exit" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Building Docker Image" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Gray
        Write-Host ""
        
        docker-compose build
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Build successful!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Starting containers..." -ForegroundColor Yellow
            docker-compose up -d
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Cyan
                Write-Host "Deployment Successful! 🎉" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "Waiting for application to start (10 seconds)..." -ForegroundColor Gray
                Start-Sleep -Seconds 10
                
                # Check health
                Write-Host "Checking application health..." -ForegroundColor Yellow
                try {
                    $health = Invoke-WebRequest -Uri http://localhost:8001/health -UseBasicParsing -TimeoutSec 5
                    Write-Host "✓ Application is healthy!" -ForegroundColor Green
                } catch {
                    Write-Host "⚠ Application may still be starting..." -ForegroundColor Yellow
                }
                
                Write-Host ""
                Write-Host "Access your application:" -ForegroundColor Yellow
                Write-Host "  - API: http://localhost:8001" -ForegroundColor White
                Write-Host "  - Docs: http://localhost:8001/docs" -ForegroundColor White
                Write-Host "  - Health: http://localhost:8001/health" -ForegroundColor White
                Write-Host ""
                Write-Host "Default credentials:" -ForegroundColor Yellow
                Write-Host "  Username: admin" -ForegroundColor White
                Write-Host "  Password: admin123" -ForegroundColor White
                Write-Host ""
                Write-Host "Useful commands:" -ForegroundColor Yellow
                Write-Host "  View logs: docker-compose logs -f" -ForegroundColor Gray
                Write-Host "  Stop: docker-compose down" -ForegroundColor Gray
                Write-Host "  Status: docker-compose ps" -ForegroundColor Gray
                Write-Host ""
                
                # Ask if user wants to view logs
                $viewLogs = Read-Host "View logs now? (y/n)"
                if ($viewLogs -eq "y") {
                    docker-compose logs -f
                }
            } else {
                Write-Host "✗ Failed to start containers" -ForegroundColor Red
                Write-Host "Check logs with: docker-compose logs" -ForegroundColor Yellow
            }
        } else {
            Write-Host "✗ Build failed" -ForegroundColor Red
            Write-Host "Check the error messages above" -ForegroundColor Yellow
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Starting containers..." -ForegroundColor Yellow
        docker-compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Containers started" -ForegroundColor Green
            Start-Sleep -Seconds 5
            docker-compose ps
            Write-Host ""
            Write-Host "Access: http://localhost:8001/docs" -ForegroundColor Cyan
        } else {
            Write-Host "✗ Failed to start containers" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Rebuilding and restarting..." -ForegroundColor Yellow
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Rebuild complete" -ForegroundColor Green
            Start-Sleep -Seconds 5
            docker-compose ps
            Write-Host ""
            Write-Host "Access: http://localhost:8001/docs" -ForegroundColor Cyan
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "Stopping containers..." -ForegroundColor Yellow
        docker-compose down
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Containers stopped" -ForegroundColor Green
        }
    }
    
    "5" {
        Write-Host ""
        Write-Host "Viewing logs (Press Ctrl+C to exit)..." -ForegroundColor Yellow
        Write-Host ""
        docker-compose logs -f
    }
    
    "6" {
        Write-Host "Exiting..." -ForegroundColor Gray
        exit 0
    }
    
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
