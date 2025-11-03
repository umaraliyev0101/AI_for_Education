# 🚀 Complete Setup Guide - From Zero to Deployed

Everything you need to deploy your AI Education Platform to GitHub Container Registry.

---

## 📝 Overview

This guide will help you:
1. ✅ Install Docker on Windows
2. ✅ Fix GitHub Actions errors
3. ✅ Deploy to GitHub Container Registry
4. ✅ Test your deployment

**Estimated Time:** 30-45 minutes

---

## 🎯 Step-by-Step Guide

### Phase 1: Install Docker (15 minutes)

#### 1.1 Download Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop/
2. Click **"Download for Windows"**
3. Save and run `Docker Desktop Installer.exe`

**Or use PowerShell:**
```powershell
# Download installer
Invoke-WebRequest -Uri "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -OutFile "DockerInstaller.exe"

# Run installer
.\DockerInstaller.exe
```

#### 1.2 Install and Configure

1. **Run installer** (as Administrator)
2. Check: ✅ **Use WSL 2** (not Hyper-V)
3. Click **"Ok"** and wait
4. **Restart your computer** when prompted

#### 1.3 Start Docker Desktop

1. Launch **Docker Desktop** from Start Menu
2. Accept the **Service Agreement**
3. Wait for Docker to start (green icon in tray)

#### 1.4 Verify Installation

```powershell
# Check Docker version
docker --version

# Test Docker
docker run hello-world
```

**Expected:**
```
Hello from Docker!
✓ Your installation is working correctly.
```

**Need help?** See [`INSTALL_DOCKER.md`](INSTALL_DOCKER.md)

---

### Phase 2: Fix GitHub Actions (5 minutes)

Your GitHub Actions had an error because it was trying to use Docker Hub instead of GHCR.

#### 2.1 Verify Workflow File

Check that `.github/workflows/docker-build.yml` contains:

```yaml
- name: Log in to GitHub Container Registry  # ← Correct name
  uses: docker/login-action@v2
  with:
    registry: ghcr.io  # ← Must be ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

#### 2.2 Enable Repository Permissions

1. Go to: https://github.com/umaraliyev0101/AI_for_Education/settings/actions
2. Scroll to **"Workflow permissions"**
3. Select: ⚪ **Read and write permissions**
4. Check: ✅ **Allow GitHub Actions to create and approve pull requests**
5. Click **"Save"**

#### 2.3 Commit the Fix

```powershell
cd D:\Projects\AI_in_Education

# Verify the workflow file is correct
cat .github\workflows\docker-build.yml

# If it needs updating, commit the changes
git add .github\workflows\docker-build.yml
git commit -m "Fix: Use GHCR instead of Docker Hub"
git push origin main
```

**Need help?** See [`FIX_GITHUB_ACTIONS.md`](FIX_GITHUB_ACTIONS.md)

---

### Phase 3: Deploy to GHCR (10 minutes)

You have **two options**:

---

#### **Option A: Automatic Deployment (GitHub Actions)**

Let GitHub build and push automatically.

**Steps:**
1. ✅ Phase 2 complete (GitHub Actions fixed)
2. Push any change to trigger build:
   ```powershell
   echo "# Deploy" >> README.md
   git add README.md
   git commit -m "Trigger deployment"
   git push origin main
   ```
3. Watch build: https://github.com/umaraliyev0101/AI_for_Education/actions
4. Wait 10-15 minutes for build to complete

**Pros:** Automatic, no local setup needed  
**Cons:** Slower, needs GitHub Actions working

---

#### **Option B: Manual Deployment (Recommended for First Time)**

Build and push from your local machine.

**Steps:**

1. **Get GitHub Token**
   - Go to: https://github.com/settings/tokens/new
   - Name: `GHCR Deploy Token`
   - Select: ✅ `write:packages`
   - Click **"Generate token"**
   - **Copy the token** (you won't see it again!)

2. **Run Deployment Script**
   ```powershell
   cd D:\Projects\AI_in_Education
   
   # Deploy (replace YOUR_TOKEN with actual token)
   .\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN_HERE"
   ```

3. **Wait for completion** (10-15 minutes)

**Pros:** Faster, you control the process  
**Cons:** Requires Docker installed locally

**Need help?** See [`DEPLOY_TO_GHCR.md`](DEPLOY_TO_GHCR.md)

---

### Phase 4: Verify Deployment (5 minutes)

#### 4.1 Check Package on GitHub

1. Go to: https://github.com/umaraliyev0101?tab=packages
2. You should see: **ai-education** package

#### 4.2 Make Package Public (Optional)

1. Click on **ai-education** package
2. Click **"Package settings"** (bottom right)
3. Scroll to **"Danger Zone"**
4. Click **"Change visibility"** → **"Public"**
5. Confirm

#### 4.3 Test Pull

```powershell
# Pull your image
docker pull ghcr.io/umaraliyev0101/ai-education:latest

# Check it exists
docker images | Select-String "ai-education"
```

#### 4.4 Test Run

```powershell
# Run your image
docker run -d `
  --name ai-education-test `
  -p 8001:8001 `
  -e SECRET_KEY=test-secret-key `
  ghcr.io/umaraliyev0101/ai-education:latest

# Wait 10 seconds for startup
Start-Sleep -Seconds 10

# Test health check
curl http://localhost:8001/health

# Clean up
docker stop ai-education-test
docker rm ai-education-test
```

**Expected:**
```json
{"status":"healthy"}
```

---

## 🎉 Success!

Your image is now on GitHub Container Registry at:
```
ghcr.io/umaraliyev0101/ai-education:latest
```

---

## 📦 Deploy to Production

### On Any Server with Docker

```bash
# Pull and run
docker pull ghcr.io/umaraliyev0101/ai-education:latest

docker run -d \
  --name ai-education \
  -p 8001:8001 \
  -e SECRET_KEY=your-production-secret \
  -v $(pwd)/uploads:/app/uploads \
  ghcr.io/umaraliyev0101/ai-education:latest
```

### With Docker Compose

Update your `docker-compose.yml`:
```yaml
services:
  app:
    image: ghcr.io/umaraliyev0101/ai-education:latest
    # Remove the 'build' section
```

Then:
```bash
docker-compose pull
docker-compose up -d
```

---

## 🔄 Update Your Image

### Automatic (GitHub Actions)
```powershell
# Just push changes
git add .
git commit -m "Update app"
git push origin main

# GitHub will automatically rebuild and push
```

### Manual
```powershell
# Re-run the deployment script
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN"
```

---

## 📚 Detailed Documentation

- **INSTALL_DOCKER.md** - Complete Docker installation guide
- **FIX_GITHUB_ACTIONS.md** - Troubleshooting GitHub Actions
- **DEPLOY_TO_GHCR.md** - Comprehensive GHCR deployment guide
- **GHCR_QUICKSTART.md** - Quick reference card

---

## 🐛 Troubleshooting

### Docker installation fails
→ See `INSTALL_DOCKER.md` - Troubleshooting section

### GitHub Actions still failing
→ See `FIX_GITHUB_ACTIONS.md`

### Cannot push to GHCR
→ Check your GitHub token has `write:packages` permission

### Build is very slow
→ This is normal for first build (10-15 min)

### "Cannot connect to Docker daemon"
→ Make sure Docker Desktop is running

---

## ✅ Checklist

### Before Starting
- [ ] Windows 10/11 (64-bit)
- [ ] 8GB+ RAM available
- [ ] Good internet connection
- [ ] GitHub account

### Phase 1: Docker
- [ ] Download Docker Desktop
- [ ] Install Docker Desktop
- [ ] Restart computer
- [ ] Start Docker Desktop
- [ ] Run `docker --version`
- [ ] Test with `docker run hello-world`

### Phase 2: GitHub Actions
- [ ] Workflow file uses `ghcr.io`
- [ ] Repository permissions set to "Read and write"
- [ ] Workflow has `permissions.packages: write`
- [ ] No Docker Hub credentials needed

### Phase 3: Deploy
- [ ] Choose deployment method (Auto or Manual)
- [ ] Get GitHub token (if manual)
- [ ] Run deployment
- [ ] Wait for completion

### Phase 4: Verify
- [ ] Package visible on GitHub
- [ ] Can pull image
- [ ] Can run image
- [ ] Health check passes

---

## 🎯 Quick Commands

```powershell
# Install Docker
# → Use GUI installer from docker.com

# Verify Docker
docker --version

# Fix GitHub Actions
git add .github\workflows\docker-build.yml
git commit -m "Fix: Use GHCR"
git push origin main

# Deploy manually
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN"

# Test deployment
docker pull ghcr.io/umaraliyev0101/ai-education:latest
docker run -d -p 8001:8001 ghcr.io/umaraliyev0101/ai-education:latest
curl http://localhost:8001/health
```

---

## 🆘 Get Help

1. Check the detailed guides in this directory
2. Read error messages carefully
3. Check Docker Desktop is running
4. Verify GitHub permissions

---

## 🎊 Congratulations!

You've successfully:
- ✅ Installed Docker
- ✅ Fixed GitHub Actions
- ✅ Deployed to GHCR
- ✅ Published your AI Education Platform

Your application is now containerized and accessible worldwide! 🌍🚀
