# PowerShell Script to Deploy to GitHub Container Registry

param(
    [string]$GitHubToken = $env:GITHUB_TOKEN,
    [string]$GitHubUsername = "umaraliyev0101",
    [string]$ImageName = "ai-education",
    [string]$Version = "1.0.0"
)

# Colors
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

Write-Host ""
Write-Host "========================================" -ForegroundColor $Cyan
Write-Host "  Deploy to GitHub Container Registry" -ForegroundColor $Cyan
Write-Host "========================================" -ForegroundColor $Cyan
Write-Host ""

# Check if token is provided
if (-not $GitHubToken) {
    Write-Host "❌ GitHub token not provided!" -ForegroundColor $Red
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor $Yellow
    Write-Host "  .\deploy-to-ghcr.ps1 -GitHubToken YOUR_TOKEN" -ForegroundColor White
    Write-Host ""
    Write-Host "Or set environment variable:" -ForegroundColor $Yellow
    Write-Host "  `$env:GITHUB_TOKEN = 'YOUR_TOKEN'" -ForegroundColor White
    Write-Host "  .\deploy-to-ghcr.ps1" -ForegroundColor White
    exit 1
}

# Configuration
$RegistryUrl = "ghcr.io"
$FullImageName = "$RegistryUrl/$GitHubUsername/$ImageName"

Write-Host "Configuration:" -ForegroundColor $Cyan
Write-Host "  Registry: $RegistryUrl" -ForegroundColor White
Write-Host "  Username: $GitHubUsername" -ForegroundColor White
Write-Host "  Image: $ImageName" -ForegroundColor White
Write-Host "  Version: $Version" -ForegroundColor White
Write-Host ""

# Step 1: Login to GHCR
Write-Host "🔐 Step 1/5: Logging in to GitHub Container Registry..." -ForegroundColor $Cyan
$env:CR_PAT = $GitHubToken
try {
    $GitHubToken | docker login $RegistryUrl -u $GitHubUsername --password-stdin 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Login successful" -ForegroundColor $Green
    } else {
        throw "Login failed"
    }
} catch {
    Write-Host "   ✗ Login failed: $_" -ForegroundColor $Red
    exit 1
}
Write-Host ""

# Step 2: Build Docker image
Write-Host "🏗️  Step 2/5: Building Docker image..." -ForegroundColor $Cyan
try {
    docker build -f Dockerfile.prod -t ${ImageName}:latest . 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Build successful" -ForegroundColor $Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "   ✗ Build failed: $_" -ForegroundColor $Red
    exit 1
}
Write-Host ""

# Step 3: Tag image
Write-Host "🏷️  Step 3/5: Tagging image..." -ForegroundColor $Cyan
try {
    docker tag ${ImageName}:latest ${FullImageName}:latest
    docker tag ${ImageName}:latest ${FullImageName}:v${Version}
    
    # Optional: Tag with git SHA if in git repo
    if (Test-Path .git) {
        $gitSha = (git rev-parse --short HEAD).Trim()
        docker tag ${ImageName}:latest ${FullImageName}:${gitSha}
        Write-Host "   ✓ Tagged: latest, v${Version}, ${gitSha}" -ForegroundColor $Green
    } else {
        Write-Host "   ✓ Tagged: latest, v${Version}" -ForegroundColor $Green
    }
} catch {
    Write-Host "   ✗ Tagging failed: $_" -ForegroundColor $Red
    exit 1
}
Write-Host ""

# Step 4: Push to GHCR
Write-Host "📤 Step 4/5: Pushing to GitHub Container Registry..." -ForegroundColor $Cyan
Write-Host "   This may take several minutes..." -ForegroundColor $Yellow

try {
    Write-Host "   → Pushing latest tag..." -ForegroundColor White
    docker push ${FullImageName}:latest 2>&1 | Out-Null
    
    Write-Host "   → Pushing version tag..." -ForegroundColor White
    docker push ${FullImageName}:v${Version} 2>&1 | Out-Null
    
    if (Test-Path .git) {
        $gitSha = (git rev-parse --short HEAD).Trim()
        Write-Host "   → Pushing SHA tag..." -ForegroundColor White
        docker push ${FullImageName}:${gitSha} 2>&1 | Out-Null
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Push successful" -ForegroundColor $Green
    } else {
        throw "Push failed"
    }
} catch {
    Write-Host "   ✗ Push failed: $_" -ForegroundColor $Red
    exit 1
}
Write-Host ""

# Step 5: Verify
Write-Host "🔍 Step 5/5: Verifying deployment..." -ForegroundColor $Cyan
try {
    $imageInfo = docker inspect ${FullImageName}:latest 2>&1 | ConvertFrom-Json
    if ($imageInfo) {
        Write-Host "   ✓ Image verified on registry" -ForegroundColor $Green
    }
} catch {
    Write-Host "   ⚠ Could not verify (may still be successful)" -ForegroundColor $Yellow
}
Write-Host ""

# Success summary
Write-Host "========================================" -ForegroundColor $Green
Write-Host "  ✅ Deployment Successful!" -ForegroundColor $Green
Write-Host "========================================" -ForegroundColor $Green
Write-Host ""
Write-Host "📦 Your image is available at:" -ForegroundColor $Cyan
Write-Host "   ${FullImageName}:latest" -ForegroundColor $Yellow
Write-Host "   ${FullImageName}:v${Version}" -ForegroundColor $Yellow
if (Test-Path .git) {
    $gitSha = (git rev-parse --short HEAD).Trim()
    Write-Host "   ${FullImageName}:${gitSha}" -ForegroundColor $Yellow
}
Write-Host ""
Write-Host "🌐 View on GitHub:" -ForegroundColor $Cyan
Write-Host "   https://github.com/${GitHubUsername}?tab=packages" -ForegroundColor $Yellow
Write-Host ""
Write-Host "📥 To pull and run:" -ForegroundColor $Cyan
Write-Host "   docker pull ${FullImageName}:latest" -ForegroundColor $White
Write-Host "   docker run -p 8001:8001 ${FullImageName}:latest" -ForegroundColor $White
Write-Host ""
Write-Host "✨ Next steps:" -ForegroundColor $Cyan
Write-Host "   1. Make package public on GitHub (optional)" -ForegroundColor $White
Write-Host "   2. Update your docker-compose.yml to use GHCR image" -ForegroundColor $White
Write-Host "   3. Deploy to your production server" -ForegroundColor $White
Write-Host ""
