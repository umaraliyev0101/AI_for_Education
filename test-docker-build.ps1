#!/usr/bin/env pwsh
# Docker Build and Test Script for AI Education Platform

param(
    [switch]$NoBuild,
    [switch]$NoCleanup,
    [string]$Port = "8001"
)

$ErrorActionPreference = "Continue"
$containerName = "ai-education-test"
$imageName = "ai-education:test"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AI Education Platform - Local Docker Build Test     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "🔍 Checking Docker status..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Clean up existing test container
Write-Host ""
Write-Host "🧹 Cleaning up existing test container..." -ForegroundColor Yellow
docker stop $containerName 2>$null | Out-Null
docker rm $containerName 2>$null | Out-Null

# Build the image
if (-not $NoBuild) {
    Write-Host ""
    Write-Host "🏗️  Building Docker image (this will take 15-20 minutes)..." -ForegroundColor Cyan
    Write-Host "Started at: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    
    $buildStart = Get-Date
    docker build -f Dockerfile.prod -t $imageName .
    $buildEnd = Get-Date
    $buildTime = ($buildEnd - $buildStart).TotalMinutes
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Build FAILED!" -ForegroundColor Red
        Write-Host "Check the error messages above." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ Build SUCCEEDED in $([math]::Round($buildTime, 1)) minutes!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⏭️  Skipping build (using existing image)" -ForegroundColor Yellow
}

# Check image exists
Write-Host ""
Write-Host "🔍 Checking image..." -ForegroundColor Yellow
$imageExists = docker images $imageName -q
if (-not $imageExists) {
    Write-Host "❌ Image not found! Please build first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Image found: $imageName" -ForegroundColor Green

# Create necessary directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$dirs = @(
    "uploads/audio",
    "uploads/faces",
    "uploads/materials",
    "uploads/presentations",
    "uploads/slides",
    "vector_stores/lesson_materials"
)
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories ready" -ForegroundColor Green

# Start the container
Write-Host ""
Write-Host "🚀 Starting container..." -ForegroundColor Cyan
docker run -d `
  --name $containerName `
  -p "${Port}:8001" `
  -e SECRET_KEY="test-secret-key-for-local-testing-minimum-32-characters-long" `
  -e DATABASE_URL="sqlite:///./ai_education.db" `
  -e ALGORITHM="HS256" `
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" `
  -v "${PWD}/uploads:/app/uploads" `
  -v "${PWD}/vector_stores:/app/vector_stores" `
  $imageName

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start container!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Container started" -ForegroundColor Green

# Wait for startup
Write-Host ""
Write-Host "⏳ Waiting for application to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "📋 Container logs:" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Gray
docker logs $containerName
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Gray

# Additional wait
Start-Sleep -Seconds 25

# Health check
Write-Host ""
Write-Host "🏥 Testing health endpoint..." -ForegroundColor Cyan

$maxRetries = 5
$retryCount = 0
$healthOk = $false

while ($retryCount -lt $maxRetries -and -not $healthOk) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:${Port}/health" -TimeoutSec 10 -ErrorAction Stop
        if ($response.status -eq "healthy") {
            Write-Host "✅ Health check PASSED: $($response.status)" -ForegroundColor Green
            $healthOk = $true
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "⏳ Attempt $retryCount/$maxRetries failed, retrying in 5 seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
}

if (-not $healthOk) {
    Write-Host ""
    Write-Host "❌ Health check FAILED after $maxRetries attempts!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Recent logs:" -ForegroundColor Yellow
    docker logs $containerName --tail 50
    
    if (-not $NoCleanup) {
        Write-Host ""
        Write-Host "🧹 Cleaning up failed container..." -ForegroundColor Yellow
        docker stop $containerName 2>$null | Out-Null
        docker rm $containerName 2>$null | Out-Null
    }
    exit 1
}

# Test API documentation
Write-Host ""
Write-Host "📚 Testing API documentation..." -ForegroundColor Cyan
try {
    $docsResponse = Invoke-WebRequest -Uri "http://localhost:${Port}/docs" -TimeoutSec 10
    if ($docsResponse.StatusCode -eq 200) {
        Write-Host "✅ API docs accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  API docs might not be accessible" -ForegroundColor Yellow
}

# Module check
Write-Host ""
Write-Host "🔍 Checking backend module..." -ForegroundColor Cyan
try {
    $moduleCheck = docker exec $containerName python -c "import backend; print('SUCCESS')" 2>&1
    if ($moduleCheck -match "SUCCESS") {
        Write-Host "✅ Backend module imports correctly" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend module check: $moduleCheck" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not verify backend module" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    TEST RESULTS                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Container: $containerName" -ForegroundColor White
Write-Host "Image: $imageName" -ForegroundColor White
Write-Host "Port: $Port" -ForegroundColor White
Write-Host "Health: ✅ HEALTHY" -ForegroundColor Green
Write-Host ""
Write-Host "Access your application:" -ForegroundColor Cyan
Write-Host "  • Health: http://localhost:${Port}/health" -ForegroundColor Gray
Write-Host "  • API Docs: http://localhost:${Port}/docs" -ForegroundColor Gray
Write-Host "  • OpenAPI: http://localhost:${Port}/openapi.json" -ForegroundColor Gray
Write-Host ""

# Commands
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  • View logs:    docker logs $containerName -f" -ForegroundColor Gray
Write-Host "  • Stop:         docker stop $containerName" -ForegroundColor Gray
Write-Host "  • Start:        docker start $containerName" -ForegroundColor Gray
Write-Host "  • Shell:        docker exec -it $containerName /bin/bash" -ForegroundColor Gray
Write-Host "  • Remove:       docker rm -f $containerName" -ForegroundColor Gray
Write-Host ""

# Ask about cleanup
if (-not $NoCleanup) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    $cleanup = Read-Host "Stop and remove test container? (y/n)"
    
    if ($cleanup -eq "y") {
        Write-Host ""
        Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
        docker stop $containerName | Out-Null
        docker rm $containerName | Out-Null
        Write-Host "✅ Container removed" -ForegroundColor Green
        
        $removeImage = Read-Host "Also remove test image? (y/n)"
        if ($removeImage -eq "y") {
            docker rmi $imageName | Out-Null
            Write-Host "✅ Image removed" -ForegroundColor Green
        }
    } else {
        Write-Host ""
        Write-Host "Container is still running. Access it at http://localhost:${Port}" -ForegroundColor Cyan
    }
} else {
    Write-Host "Container is still running (--NoCleanup flag used)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ Test completed successfully!" -ForegroundColor Green
Write-Host ""
