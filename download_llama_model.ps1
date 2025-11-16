################################################################################
# Llama 3.1 8B Uzbek Model Downloader (PowerShell)
# Optimized for Windows with resume capability and fast transfer
################################################################################

# Script settings
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Configuration
$MODEL_ID = "behbudiy/Llama-3.1-8B-Instruct-Uz"
$CACHE_DIR = "$env:USERPROFILE\.cache\huggingface\hub"
$MIN_DISK_SPACE_GB = 20

################################################################################
# Functions
################################################################################

function Write-Header {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "🦙 Llama 3.1 8B Uzbek Model Downloader" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✓ Public model - No token required!" -ForegroundColor Green
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Message {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Command)
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Test-DiskSpace {
    Write-Host "Checking disk space..." -ForegroundColor Cyan
    
    $drive = (Get-Location).Drive
    $freeSpace = [math]::Round(($drive.Free / 1GB), 2)
    
    if ($freeSpace -lt $MIN_DISK_SPACE_GB) {
        Write-Warning-Message "Only ${freeSpace}GB free. Recommended: ${MIN_DISK_SPACE_GB}GB"
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    } else {
        Write-Success "Disk space: ${freeSpace}GB available"
    }
}

function Test-Internet {
    Write-Host "Checking internet connection..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri "https://huggingface.co" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "Internet connection: OK"
            return $true
        }
    } catch {
        Write-Error-Message "Internet connection: Failed"
        return $false
    }
}

function Test-HFToken {
    Write-Host "Checking HuggingFace authentication..." -ForegroundColor Cyan
    
    if ($env:HF_TOKEN) {
        Write-Success "HF_TOKEN found - will use for download"
    } else {
        Write-Success "No token required - this is a public model"
        Write-Info "You can optionally set HF_TOKEN for better download stability"
    }
}

function Install-Dependencies {
    Write-Host "Checking dependencies..." -ForegroundColor Cyan
    
    # Check Python
    if (-not (Test-Command "python")) {
        Write-Error-Message "Python is not installed"
        Write-Host "Install Python from: https://www.python.org/downloads/"
        exit 1
    }
    Write-Success "Python: OK"
    
    # Check pip
    if (-not (Test-Command "pip")) {
        Write-Error-Message "pip is not installed"
        exit 1
    }
    Write-Success "pip: OK"
    
    # Install/upgrade huggingface-hub
    Write-Host "Installing huggingface-hub with fast transfer..." -ForegroundColor Yellow
    pip install -q -U "huggingface-hub[cli,hf_transfer]" tqdm
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "huggingface-hub installed"
    } else {
        Write-Warning-Message "Failed to install huggingface-hub"
    }
}

function Enable-Optimizations {
    Write-Host "Enabling download optimizations..." -ForegroundColor Cyan
    
    # Enable hf_transfer for faster downloads (3-5x faster)
    $env:HF_HUB_ENABLE_HF_TRANSFER = "1"
    Write-Success "Fast transfer mode enabled (3-5x faster)"
    
    # Increase timeout
    $env:HF_HUB_DOWNLOAD_TIMEOUT = "300"
    Write-Success "Download timeout set to 300s"
    
    # Set cache directory
    $env:HF_HOME = "$env:USERPROFILE\.cache\huggingface"
    Write-Success "Cache directory: $env:HF_HOME\hub"
}

function Start-ModelDownload {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "📥 Starting Download" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Model: $MODEL_ID" -ForegroundColor Yellow
    Write-Host "Cache: $CACHE_DIR" -ForegroundColor Yellow
    Write-Host "Estimated time: 10-30 minutes (with optimizations)" -ForegroundColor Yellow
    Write-Host "💡 Tip: Download will automatically resume if interrupted" -ForegroundColor Yellow
    Write-Host ""
    
    # Create cache directory
    New-Item -ItemType Directory -Force -Path $CACHE_DIR | Out-Null
    
    # Download using Python (more reliable on Windows)
    Write-Info "Using Python for download..."
    
    $downloadScript = @"
import os
from huggingface_hub import snapshot_download
from tqdm import tqdm

print("\n📥 Downloading model files...")

try:
    # Download to default HuggingFace cache
    snapshot_download(
        repo_id="$MODEL_ID",
        resume_download=True,
        max_workers=8,
        local_files_only=False,
        token=os.getenv("HF_TOKEN")
    )
    print("\n✅ Download completed successfully!")
except Exception as e:
    print(f"\n❌ Download failed: {e}")
    exit(1)
"@
    
    # Save script to temp file
    $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
    $downloadScript | Out-File -FilePath $tempScript -Encoding UTF8
    
    # Run download
    try {
        python $tempScript
        $downloadSuccess = $LASTEXITCODE -eq 0
    } finally {
        # Clean up temp file
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
    
    return $downloadSuccess
}

function Test-Download {
    Write-Host ""
    Write-Host "Verifying downloaded files..." -ForegroundColor Cyan
    
    # Find model directory (excluding .locks)
    $modelDir = Get-ChildItem -Path $CACHE_DIR -Directory -Filter "models--behbudiy--Llama-3.1-8B-Instruct-Uz" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notlike "*\.locks*" } |
        Select-Object -First 1
    
    if (-not $modelDir) {
        Write-Error-Message "Model directory not found"
        return $false
    }
    
    # Find snapshot directory
    $snapshotDir = Get-ChildItem -Path "$($modelDir.FullName)\snapshots" -Directory -ErrorAction SilentlyContinue |
        Select-Object -First 1
    
    if (-not $snapshotDir) {
        Write-Error-Message "Snapshot directory not found"
        return $false
    }
    
    Write-Success "Model directory found"
    Write-Host "   Path: $($snapshotDir.FullName)"
    
    # Check total size
    $totalSize = (Get-ChildItem -Path $snapshotDir.FullName -Recurse -File | 
        Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($totalSize / 1MB, 0)
    $sizeGB = [math]::Round($totalSize / 1GB, 1)
    
    Write-Success "Total size: ${sizeGB}GB"
    
    # Check essential files
    $essentialFiles = @(
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json"
    )
    
    Write-Host ""
    Write-Host "Essential files:"
    $allFound = $true
    
    foreach ($file in $essentialFiles) {
        $filePath = Join-Path $snapshotDir.FullName $file
        if (Test-Path $filePath) {
            $fileSize = (Get-Item $filePath).Length
            Write-Success "$file ($fileSize bytes)"
        } else {
            Write-Warning-Message "$file (missing)"
            $allFound = $false
        }
    }
    
    # Check for model weight files
    $weightFiles = Get-ChildItem -Path $snapshotDir.FullName -Filter "*.safetensors" -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Success "Model weights: $($weightFiles.Count) files"
    
    if ($allFound -and $weightFiles.Count -gt 0) {
        Write-Success "Verification passed!"
        return $true
    } else {
        Write-Warning-Message "Some files may be missing"
        return $false
    }
}

function Show-Usage {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "🎉 SUCCESS! Model is ready to use" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To use the model in your code:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "from transformers import AutoTokenizer, AutoModelForCausalLM"
    Write-Host ""
    Write-Host "# Model will be loaded from standard HuggingFace cache"
    Write-Host "MODEL_NAME = `"$MODEL_ID`""
    Write-Host "tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)"
    Write-Host "model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)"
    Write-Host ""
    Write-Host "Cache location:" -ForegroundColor Cyan
    Write-Host "$env:USERPROFILE\.cache\huggingface\hub"
    Write-Host ""
}

################################################################################
# Main Script
################################################################################

# Handle Ctrl+C gracefully
$ErrorActionPreference = "Continue"
trap {
    Write-Host ""
    Write-Warning-Message "Download interrupted by user"
    Write-Info "Run this script again to resume download"
    exit 130
}

# Print header
Write-Header

# Step 1: Check requirements
Test-DiskSpace
$internetOk = Test-Internet
if (-not $internetOk) {
    exit 1
}

# Step 2: Install dependencies
Install-Dependencies

# Step 3: Check HuggingFace token
Test-HFToken

# Step 4: Enable optimizations
Enable-Optimizations

# Step 5: Download model
$downloadSuccess = Start-ModelDownload

if ($downloadSuccess) {
    # Step 6: Verify download
    $verifySuccess = Test-Download
    
    if ($verifySuccess) {
        # Step 7: Show usage instructions
        Show-Usage
        exit 0
    } else {
        Write-Warning-Message "Download may be incomplete"
        Write-Info "Run this script again to retry"
        exit 1
    }
} else {
    Write-Error-Message "Download failed"
    Write-Info "Troubleshooting tips:"
    Write-Host "  1. Check your internet connection"
    Write-Host "  2. Try running during off-peak hours"
    Write-Host "  3. Run this script again (it will resume)"
    Write-Host "  4. (Optional) Set HF_TOKEN for better stability"
    exit 1
}
