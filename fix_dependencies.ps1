# ============================================================================
# Quick Fix for Dependency Conflicts
# Run this first before downloading the model
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "🔧 Fixing Dependency Conflicts" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Fix huggingface-hub version conflict
Write-Host "[1/3] Fixing huggingface-hub version..." -ForegroundColor Yellow
Write-Host ""

pip uninstall -y huggingface-hub
pip install "huggingface-hub>=0.23.0,<1.0"

Write-Host ""
Write-Host "✓ huggingface-hub fixed" -ForegroundColor Green
Write-Host ""

# Step 2: Install required packages
Write-Host "[2/3] Installing required packages..." -ForegroundColor Yellow
Write-Host ""

pip install tqdm requests

Write-Host ""
Write-Host "✓ Packages installed" -ForegroundColor Green
Write-Host ""

# Step 3: Verify installation
Write-Host "[3/3] Verifying installation..." -ForegroundColor Yellow
Write-Host ""

$verifyScript = @"
try:
    from huggingface_hub import snapshot_download
    import tqdm
    print("✓ All imports working")
    
    import huggingface_hub
    print(f"✓ huggingface-hub version: {huggingface_hub.__version__}")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
"@

python -c $verifyScript

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host "✅ Dependencies Fixed!" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now run the download script:" -ForegroundColor Cyan
    Write-Host "  .\download_llama_model.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Red
    Write-Host "❌ Verification Failed" -ForegroundColor Red
    Write-Host "============================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try manual installation:" -ForegroundColor Yellow
    Write-Host '  pip install "huggingface-hub>=0.23.0,<1.0" tqdm requests' -ForegroundColor White
    Write-Host ""
}

pause
