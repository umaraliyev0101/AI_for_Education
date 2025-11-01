# Fix Docker Build Issues

## Changes Made to Dockerfile.prod

### Key Optimizations:

1. **Staged Installation**: Split package installation into multiple smaller steps to avoid GitHub Actions memory limits (6GB)

2. **PyTorch CPU Version**: Using CPU-only PyTorch from `https://download.pytorch.org/whl/cpu` for:
   - Smaller download size (~200MB vs ~800MB)
   - Faster build time
   - Sufficient for inference workloads

3. **opencv-python-headless**: Using headless version instead of full opencv-python:
   - No GUI dependencies
   - Smaller size
   - Better for Docker containers

4. **Additional Runtime Libraries**: Added libraries needed for ML packages:
   - `libgl1`, `libglib2.0-0`, `libsm6`, `libxext6`, `libxrender-dev` for OpenCV
   - `libgomp1` for PyTorch threading
   - `libsndfile1`, `ffmpeg` for audio processing

5. **Environment Variables**: Set pip environment variables for better performance:
   - `PIP_NO_CACHE_DIR=1` - Reduces disk usage
   - `PIP_DISABLE_PIP_VERSION_CHECK=1` - Faster pip operations
   - `PIP_DEFAULT_TIMEOUT=100` - Handle slow downloads

## How to Test the Fix

### Option 1: Test on GitHub Actions (Automatic)

```powershell
# Commit the changes
git add Dockerfile.prod
git commit -m "fix: optimize Docker build for GitHub Actions"
git push origin main
```

Then watch the GitHub Actions workflow:
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Watch the "Build and Push Docker Image" workflow
4. Check the build logs for success

### Option 2: Test Locally (Faster)

```powershell
# Build locally to verify it works
docker build -f Dockerfile.prod -t ai-education:test .

# If successful, you'll see:
# => => naming to docker.io/library/ai-education:test

# Then deploy to GHCR
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_GITHUB_TOKEN"
```

## Expected Build Time

- **GitHub Actions**: 15-25 minutes (includes caching)
- **Local Build**: 20-30 minutes (first time)
- **Local Build (cached)**: 5-10 minutes

## Troubleshooting

### If Build Still Fails

1. **Check Error Message**:
   ```powershell
   # Look for specific package that failed
   # Example: "ERROR: Failed building wheel for X"
   ```

2. **Increase Timeout**:
   If seeing timeout errors, update Dockerfile.prod:
   ```dockerfile
   ENV PIP_DEFAULT_TIMEOUT=300
   ```

3. **Skip Optional Packages**:
   Some packages are optional. Create a minimal `requirements.prod.txt`:
   ```
   # Essential packages only
   fastapi>=0.104.0
   uvicorn[standard]>=0.24.0
   gunicorn>=21.2.0
   sqlalchemy>=2.0.0
   # ... add others as needed
   ```

4. **Use Pre-built Base Image**:
   Consider using an image with ML dependencies pre-installed:
   ```dockerfile
   FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime AS builder
   ```

### Memory Issues on GitHub Actions

If you see "Killed" or memory errors:

1. **Reduce Concurrent Installations**:
   - Already done - each RUN command installs fewer packages

2. **Use GitHub Actions with More Memory**:
   - GitHub-hosted runners have 6GB RAM
   - Consider self-hosted runners for heavy builds

3. **Build Locally and Push**:
   ```powershell
   # Build on your machine (more RAM available)
   docker build -f Dockerfile.prod -t ghcr.io/YOUR_USERNAME/ai-education:latest .
   
   # Push to GHCR
   docker push ghcr.io/YOUR_USERNAME/ai-education:latest
   ```

## What's Different Now

### Before (Single Large Install):
```dockerfile
RUN pip install -r requirements.txt
# All 50+ packages at once = High memory usage
```

### After (Staged Install):
```dockerfile
RUN pip install numpy scipy Pillow  # Lightweight first
RUN pip install fastapi uvicorn     # Web framework
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu  # CPU-only
RUN pip install transformers        # ML packages
# ... etc in small batches
```

## Verification

After successful build, verify the image:

```powershell
# Run the container
docker run -d -p 8001:8001 --name ai-edu-test ghcr.io/YOUR_USERNAME/ai-education:latest

# Check logs
docker logs ai-edu-test

# Test health endpoint
curl http://localhost:8001/health

# Clean up
docker stop ai-edu-test
docker rm ai-edu-test
```

## Next Steps

1. ✅ Commit and push Dockerfile.prod
2. ⏳ Wait for GitHub Actions to complete
3. ✅ Verify image is in GitHub Container Registry
4. ✅ Deploy to production using docker-compose.prod.yml

## Alternative: Quick Deploy (Skip GitHub Actions)

If you need to deploy NOW and can't wait for the build:

```powershell
# Build and push locally (requires Docker Desktop running)
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN"

# Then on your server
docker-compose -f docker-compose.prod.yml up -d
```

This bypasses GitHub Actions completely and deploys directly from your local machine.
