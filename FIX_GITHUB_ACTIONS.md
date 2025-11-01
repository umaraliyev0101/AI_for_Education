# 🔧 Fix GitHub Actions Docker Build Error

## ❌ The Error

You're seeing:
```
Log in to Docker Hub
Error: Username and password required
```

This means GitHub Actions is trying to login to Docker Hub instead of GitHub Container Registry (GHCR).

---

## ✅ Solution: Update GitHub Actions Workflow

### Step 1: Verify Workflow File

Check that `.github/workflows/docker-build.yml` has the correct GHCR configuration:

```yaml
- name: Log in to GitHub Container Registry
  if: github.event_name != 'pull_request'
  uses: docker/login-action@v2
  with:
    registry: ghcr.io  # ← Must be ghcr.io, NOT registry.hub.docker.com
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Step 2: Update the Workflow File

```powershell
# Navigate to your project
cd D:\Projects\AI_in_Education

# Open the workflow file
code .github\workflows\docker-build.yml
```

Make sure the **entire file** matches this:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main, develop ]
    tags:
      - 'v*'
  pull_request:
    branches: [ main ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to GitHub Container Registry
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ghcr.io/${{ github.repository_owner }}/ai-education
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.prod
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Image digest
      run: echo ${{ steps.meta.outputs.digest }}
    
    - name: Summary
      if: github.event_name != 'pull_request'
      run: |
        echo "### ✅ Docker Image Published" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "**Registry:** GitHub Container Registry" >> $GITHUB_STEP_SUMMARY
        echo "**Image:** \`ghcr.io/${{ github.repository_owner }}/ai-education\`" >> $GITHUB_STEP_SUMMARY
```

### Step 3: Commit and Push

```powershell
git add .github/workflows/docker-build.yml
git commit -m "Fix: Use GHCR instead of Docker Hub"
git push origin main
```

---

## 🔍 Check Repository Permissions

### Verify GITHUB_TOKEN Permissions

1. Go to your repo: https://github.com/umaraliyev0101/AI_for_Education
2. Click **Settings** → **Actions** → **General**
3. Scroll to **Workflow permissions**
4. Select: **Read and write permissions**
5. Check: ✅ **Allow GitHub Actions to create and approve pull requests**
6. Click **Save**

---

## 🧪 Test the Fix

### Option 1: Push a Change

```powershell
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test GitHub Actions"
git push origin main
```

### Option 2: Re-run Failed Workflow

1. Go to: https://github.com/umaraliyev0101/AI_for_Education/actions
2. Click on the failed workflow run
3. Click **Re-run all jobs**

---

## 🎯 Alternative: Build Locally and Push Manually

If GitHub Actions continues to have issues, build and push locally:

### Prerequisites
1. Install Docker (see `INSTALL_DOCKER.md`)
2. Get GitHub token with `write:packages` permission

### Deploy Locally

```powershell
# Navigate to project
cd D:\Projects\AI_in_Education

# Run deployment script
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_GITHUB_TOKEN"
```

This will:
- ✅ Build the Docker image locally
- ✅ Push directly to GHCR
- ✅ Bypass GitHub Actions entirely

---

## 🚫 Common Issues

### Issue 1: "DOCKER_USERNAME secret not found"

**Problem:** Old workflow is looking for Docker Hub credentials

**Solution:** Update workflow to use GHCR (see Step 2 above)

### Issue 2: "Permission denied to push to GHCR"

**Problem:** GITHUB_TOKEN doesn't have write permissions

**Solution:** 
1. Go to repo **Settings** → **Actions** → **General**
2. Set **Workflow permissions** to **Read and write**

### Issue 3: "Resource not accessible by integration"

**Problem:** Workflow missing permissions block

**Solution:** Add to workflow:
```yaml
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write  # ← This is required!
```

### Issue 4: Build fails with "no space left on device"

**Solution:** Use GitHub Actions cache:
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

---

## 📋 Checklist

- [ ] Docker installed locally (see `INSTALL_DOCKER.md`)
- [ ] Workflow file uses `ghcr.io` registry
- [ ] Workflow has `permissions.packages: write`
- [ ] Repository settings: "Read and write permissions" enabled
- [ ] No `DOCKER_USERNAME` or `DOCKER_PASSWORD` secrets needed
- [ ] Workflow uses `${{ secrets.GITHUB_TOKEN }}` (automatic)
- [ ] Committed and pushed updated workflow
- [ ] Re-run GitHub Actions workflow

---

## ✅ Expected Result

After fixing, you should see in GitHub Actions:

```
✓ Set up Docker Buildx
✓ Log in to GitHub Container Registry  ← Should be green!
✓ Extract metadata
✓ Build and push Docker image
```

And the image will be available at:
```
ghcr.io/umaraliyev0101/ai-education:latest
```

---

## 🎉 Quick Fix Summary

1. **Update workflow file** to use GHCR (not Docker Hub)
2. **Enable write permissions** in repo settings
3. **Commit and push** the changes
4. **Re-run** the workflow

OR

**Build locally:**
```powershell
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN"
```

---

## 🆘 Still Having Issues?

### Check the Logs

1. Go to: https://github.com/umaraliyev0101/AI_for_Education/actions
2. Click on the failed run
3. Look for the exact error message
4. Share it for more specific help

### Manual Deployment

You can always build and push manually:
```powershell
# Install Docker first (see INSTALL_DOCKER.md)
# Then run:
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN"
```

This bypasses GitHub Actions and pushes directly from your machine.
