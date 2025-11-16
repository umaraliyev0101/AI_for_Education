"""
Simple Python script to download the Llama model
Use this if PowerShell scripts have issues
"""

import os
import sys

# Configuration
MODEL_ID = "behbudiy/Llama-3.1-8B-Instruct-Uz"

print("=" * 70)
print("🦙 Llama Model Downloader")
print("=" * 70)
print()
print(f"Model: {MODEL_ID}")
print()

# Step 1: Check/install dependencies
print("[1/3] Checking dependencies...")
print()

try:
    from huggingface_hub import snapshot_download
    from tqdm import tqdm
    print("✓ All dependencies available")
except ImportError as e:
    print(f"⚠️  Missing dependency: {e}")
    print()
    print("Installing required packages...")
    import subprocess
    
    packages = [
        "huggingface-hub>=0.23.0,<1.0",
        "tqdm",
        "requests"
    ]
    
    for package in packages:
        print(f"  Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", package],
            capture_output=True
        )
        if result.returncode != 0:
            print(f"  ⚠️  Warning: {package} installation had issues")
    
    print()
    print("Please run this script again.")
    sys.exit(0)

print()

# Step 2: Set optimizations
print("[2/3] Setting up optimizations...")
print()

os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'
os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '300'

print("✓ Optimizations enabled")
print()

# Step 3: Download model
print("[3/3] Downloading model...")
print()
print("⏳ This will take 10-30 minutes")
print("💡 You can interrupt (Ctrl+C) and resume later")
print()

try:
    path = snapshot_download(
        repo_id=MODEL_ID,
        resume_download=True,
        max_workers=4,
        token=os.getenv("HF_TOKEN")
    )
    
    print()
    print("=" * 70)
    print("✅ Download Complete!")
    print("=" * 70)
    print()
    print(f"Model saved to: {path}")
    print()
    print("You can now use the model in your code:")
    print()
    print(f'from transformers import AutoTokenizer, AutoModelForCausalLM')
    print(f'tokenizer = AutoTokenizer.from_pretrained("{MODEL_ID}")')
    print(f'model = AutoModelForCausalLM.from_pretrained("{MODEL_ID}")')
    print()
    
except KeyboardInterrupt:
    print()
    print("⚠️  Download interrupted")
    print("Run this script again to resume")
    sys.exit(130)
    
except Exception as e:
    print()
    print("=" * 70)
    print("❌ Download Failed")
    print("=" * 70)
    print()
    print(f"Error: {type(e).__name__}: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Check internet connection")
    print("  2. Run this script again (will resume)")
    print("  3. Check firewall/proxy settings")
    print()
    sys.exit(1)
