#!/usr/bin/env pwsh
# Cleanup Script - Remove Unnecessary Documentation and Scripts

param(
    [switch]$DryRun,  # Show what would be deleted without deleting
    [switch]$Force    # Skip confirmation
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     AI Education Platform - Cleanup Script           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Files to remove
$filesToRemove = @(
    # Documentation - Deployment Guides
    "AUTO_DEPLOY_SUMMARY.md",
    "AUTO_REDEPLOY.md",
    "COMPLETE_SETUP.md",
    "DEPLOY_TO_GHCR.md",
    "DEPLOYMENT.md",
    "DEPLOYMENT_DIAGRAM.txt",
    "DEPLOYMENT_SUMMARY.md",
    "DOCKER_README.md",
    "DOCKER_SUMMARY.md",
    "GHCR_QUICKSTART.md",
    "QUICKSTART.md",
    "SERVER_SETUP.md",
    
    # Documentation - Troubleshooting
    "ERROR_503_QUICKFIX.md",
    "FIX_DOCKER_BUILD.md",
    "FIX_GITHUB_ACTIONS.md",
    "FIX_MODULE_NOT_FOUND.md",
    "INSTALL_DOCKER.md",
    "LOCAL_BUILD_GUIDE.md",
    "QUICKFIX_MODULE_ERROR.md",
    "START_HERE.md",
    "TROUBLESHOOT_503.md",
    
    # Scripts - Deployment
    "deploy-to-ghcr.ps1",
    "deploy-to-ghcr.sh",
    
    # Scripts - Testing
    "test_deployment.ps1",
    "test_deployment.sh",
    "test-docker-build.ps1",
    
    # Scripts - Development
    "start.ps1",
    
    # Docker - Development
    "Dockerfile",
    "docker-compose.yml",
    
    # Tests (optional - comment out if you want to keep)
    "test_backend_setup.py",
    "test_qa_system.py",
    
    # Duplicates
    "main.py",
    "backend_requirements.txt"
)

# Files to keep (essential)
$keepFiles = @(
    "Dockerfile.prod",
    "docker-compose.prod.yml",
    "docker-compose.watchtower.yml",
    "diagnose.sh",
    "start.sh",
    "nginx.conf",
    "requirements.txt",
    "pyproject.toml",
    "README.md",
    ".dockerignore",
    ".gitignore"
)

Write-Host "🔍 Files to remove:" -ForegroundColor Yellow
Write-Host ""

$existingFiles = @()
$missingFiles = @()

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        $existingFiles += $file
        $size = (Get-Item $file).Length
        $sizeKB = [math]::Round($size / 1KB, 1)
        Write-Host "  ❌ $file" -ForegroundColor Red -NoNewline
        Write-Host " ($sizeKB KB)" -ForegroundColor Gray
    } else {
        $missingFiles += $file
    }
}

Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  Files to delete: $($existingFiles.Count)" -ForegroundColor Yellow
Write-Host "  Already missing: $($missingFiles.Count)" -ForegroundColor Gray
Write-Host ""

# Calculate space to free
$totalSize = 0
foreach ($file in $existingFiles) {
    $totalSize += (Get-Item $file).Length
}
$totalMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "  Space to free: $totalMB MB" -ForegroundColor Green
Write-Host ""

if ($existingFiles.Count -eq 0) {
    Write-Host "✅ No files to remove. Already clean!" -ForegroundColor Green
    exit 0
}

# Show what will be kept
Write-Host "✅ Essential files that will be kept:" -ForegroundColor Green
Write-Host ""
foreach ($file in $keepFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
}
Write-Host "  ✓ backend/ (all backend code)" -ForegroundColor Green
Write-Host "  ✓ face_recognition/ (face recognition)" -ForegroundColor Green
Write-Host "  ✓ stt_pipelines/ (speech-to-text)" -ForegroundColor Green
Write-Host "  ✓ utils/ (utilities)" -ForegroundColor Green
Write-Host "  ✓ .github/ (CI/CD workflows)" -ForegroundColor Green
Write-Host ""

# Dry run
if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To actually delete files, run without -DryRun flag:" -ForegroundColor Cyan
    Write-Host "  .\cleanup.ps1" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# Confirmation
if (-not $Force) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  WARNING: This will permanently delete $($existingFiles.Count) files!" -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "Are you sure you want to continue? (type 'yes' to confirm)"
    
    if ($confirm -ne "yes") {
        Write-Host ""
        Write-Host "❌ Cleanup cancelled" -ForegroundColor Red
        exit 0
    }
}

# Delete files
Write-Host ""
Write-Host "🗑️  Deleting files..." -ForegroundColor Yellow
Write-Host ""

$deletedCount = 0
$failedCount = 0

foreach ($file in $existingFiles) {
    try {
        Remove-Item $file -Force
        Write-Host "  ✓ Deleted: $file" -ForegroundColor Green
        $deletedCount++
    } catch {
        Write-Host "  ✗ Failed: $file - $($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  Deleted: $deletedCount files" -ForegroundColor Green
Write-Host "  Failed: $failedCount files" -ForegroundColor $(if ($failedCount -gt 0) { "Red" } else { "Gray" })
Write-Host "  Freed: $totalMB MB" -ForegroundColor Green
Write-Host ""

# Offer to commit
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
$gitCommit = Read-Host "Commit changes to git? (y/n)"

if ($gitCommit -eq "y") {
    Write-Host ""
    Write-Host "📝 Committing changes..." -ForegroundColor Cyan
    
    git add -A
    git commit -m "cleanup: remove unnecessary documentation and development files"
    
    Write-Host ""
    Write-Host "✅ Changes committed!" -ForegroundColor Green
    Write-Host ""
    
    $gitPush = Read-Host "Push to GitHub? (y/n)"
    
    if ($gitPush -eq "y") {
        Write-Host ""
        Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
        git push origin main
        Write-Host "✅ Pushed to GitHub!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎉 All done! Your repository is now clean and production-ready." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. GitHub Actions will auto-build on next push" -ForegroundColor Gray
Write-Host "  2. Your friend can deploy using docker-compose.prod.yml" -ForegroundColor Gray
Write-Host "  3. See SIMPLE_DEPLOY.md for deployment instructions" -ForegroundColor Gray
Write-Host ""
