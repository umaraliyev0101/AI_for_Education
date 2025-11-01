# PowerShell Test Script for Docker Deployment

Write-Host "🧪 Testing AI Education Docker Deployment..." -ForegroundColor Cyan
Write-Host ""

$BASE_URL = "http://localhost:8001"
$CONTAINER_NAME = "ai_education_app"

# Function to test endpoint
function Test-Endpoint {
    param(
        [string]$Endpoint,
        [int]$ExpectedStatus,
        [string]$Description
    )
    
    Write-Host -NoNewline "Testing $Description... "
    
    try {
        $response = Invoke-WebRequest -Uri "$BASE_URL$Endpoint" -UseBasicParsing -ErrorAction Stop
        $status = $response.StatusCode
        
        if ($status -eq $ExpectedStatus) {
            Write-Host "✓ PASSED" -ForegroundColor Green -NoNewline
            Write-Host " (HTTP $status)"
            return $true
        } else {
            Write-Host "✗ FAILED" -ForegroundColor Red -NoNewline
            Write-Host " (HTTP $status, expected $ExpectedStatus)"
            return $false
        }
    } catch {
        Write-Host "✗ FAILED" -ForegroundColor Red -NoNewline
        Write-Host " (Error: $($_.Exception.Message))"
        return $false
    }
}

# Check if container is running
Write-Host "1. Checking if container is running..."
$containerRunning = docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | Select-String -Pattern $CONTAINER_NAME

if ($containerRunning) {
    Write-Host "✓ Container is running" -ForegroundColor Green
} else {
    Write-Host "✗ Container is not running" -ForegroundColor Red
    Write-Host "Start the container with: docker-compose up -d"
    exit 1
}

Write-Host ""
Write-Host "2. Testing API endpoints..."
Write-Host ""

$passed = 0
$failed = 0

# Test endpoints
if (Test-Endpoint "/" 200 "Root endpoint") { $passed++ } else { $failed++ }
if (Test-Endpoint "/health" 200 "Health check") { $passed++ } else { $failed++ }
if (Test-Endpoint "/docs" 200 "API documentation") { $passed++ } else { $failed++ }
if (Test-Endpoint "/openapi.json" 200 "OpenAPI spec") { $passed++ } else { $failed++ }

Write-Host ""
Write-Host "3. Testing authentication..."
Write-Host ""

# Test login
try {
    $loginData = @{
        username = "admin"
        password = "admin123"
    }
    
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginData `
        -ErrorAction Stop
    
    if ($response.access_token) {
        Write-Host "✓ Authentication working" -ForegroundColor Green
        $passed++
        
        $token = $response.access_token
        
        # Test authenticated endpoint
        Write-Host ""
        Write-Host "4. Testing authenticated endpoint..."
        
        try {
            $headers = @{
                "Authorization" = "Bearer $token"
            }
            $authResponse = Invoke-WebRequest -Uri "$BASE_URL/api/lessons/" `
                -Headers $headers `
                -UseBasicParsing `
                -ErrorAction Stop
            
            Write-Host "✓ Authenticated requests working" -ForegroundColor Green
            $passed++
        } catch {
            Write-Host "✗ Authenticated requests failing" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "✗ Authentication failed - no token received" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "✗ Authentication failed - $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Write-Host ""
Write-Host "5. Checking container health..."
Write-Host ""

try {
    $health = docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>$null
    
    if ($health -eq "healthy") {
        Write-Host "✓ Container is healthy" -ForegroundColor Green
        $passed++
    } elseif ($health -eq "starting") {
        Write-Host "⚠ Container is still starting" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Container health: $health" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "✗ Could not check container health" -ForegroundColor Red
    $failed++
}

Write-Host ""
Write-Host "6. Checking logs for errors..."
Write-Host ""

$logs = docker logs $CONTAINER_NAME 2>&1
$errorCount = ($logs | Select-String -Pattern "error" -CaseSensitive:$false).Count

if ($errorCount -eq 0) {
    Write-Host "✓ No errors in logs" -ForegroundColor Green
    $passed++
} else {
    Write-Host "⚠ Found $errorCount error messages in logs" -ForegroundColor Yellow
    Write-Host "Run 'docker logs $CONTAINER_NAME' to view"
}

# Summary
Write-Host ""
Write-Host "============================================"
Write-Host "Test Summary:"
Write-Host "============================================"
Write-Host "Passed: " -NoNewline
Write-Host $passed -ForegroundColor Green
Write-Host "Failed: " -NoNewline
Write-Host $failed -ForegroundColor Red
Write-Host "============================================"

if ($failed -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your deployment is working correctly! 🎉"
    Write-Host ""
    Write-Host "Access points:"
    Write-Host "  - API: $BASE_URL"
    Write-Host "  - Docs: $BASE_URL/docs"
    Write-Host "  - Health: $BASE_URL/health"
    exit 0
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:"
    Write-Host "  1. Check logs: docker-compose logs -f"
    Write-Host "  2. Restart: docker-compose restart"
    Write-Host "  3. Rebuild: docker-compose up -d --build"
    exit 1
}
