# 🐳 Install Docker on Windows

Complete guide to install Docker Desktop on Windows.

---

## 📋 Prerequisites

### System Requirements
- **Windows 10/11** (64-bit)
- **Pro, Enterprise, or Education** edition (for Hyper-V)
  - Or Windows 10/11 Home with WSL 2
- **Minimum**: 4GB RAM (8GB recommended)
- **Virtualization**: Enabled in BIOS

---

## 🚀 Installation Steps

### Step 1: Download Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop/
2. Click **"Download for Windows"**
3. Save `Docker Desktop Installer.exe`

**Direct Link:**
```
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
```

---

### Step 2: Install Docker Desktop

1. **Run the installer**
   ```powershell
   # Run as Administrator
   .\Docker Desktop Installer.exe
   ```

2. **Configuration options:**
   - ✅ Use WSL 2 instead of Hyper-V (recommended)
   - ✅ Add shortcut to desktop (optional)

3. **Click "Ok"** and wait for installation

4. **Restart your computer** when prompted

---

### Step 3: Enable WSL 2 (If Not Already Enabled)

#### Check WSL Version
```powershell
wsl --version
```

#### Install WSL 2
```powershell
# Open PowerShell as Administrator

# Enable WSL
wsl --install

# Set WSL 2 as default
wsl --set-default-version 2

# Update WSL kernel
wsl --update
```

#### Install Ubuntu (Optional but Recommended)
```powershell
wsl --install -d Ubuntu
```

---

### Step 4: Start Docker Desktop

1. **Launch Docker Desktop** from Start Menu
2. **Accept the Service Agreement**
3. **Skip Tutorial** (optional)
4. **Wait for Docker to start** (green icon in system tray)

---

### Step 5: Verify Installation

Open PowerShell and run:

```powershell
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Test Docker
docker run hello-world
```

**Expected Output:**
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## ⚙️ Configure Docker Settings

### Open Docker Desktop Settings

1. Click Docker icon in system tray
2. Click **Settings** (gear icon)

### Recommended Settings

#### **Resources** → **Advanced**
```
CPUs: 4 (or half of your CPU cores)
Memory: 8 GB
Swap: 2 GB
Disk image size: 60 GB
```

#### **Resources** → **File Sharing**
Add your project directory:
```
D:\Projects\AI_in_Education
```

#### **General**
- ✅ Start Docker Desktop when you log in
- ✅ Use Docker Compose V2

#### **Docker Engine** (Optional)
Edit JSON if needed:
```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  }
}
```

---

## 🧪 Test Your Installation

### Test 1: Run Hello World
```powershell
docker run hello-world
```

### Test 2: Check System Info
```powershell
docker info
```

### Test 3: Build a Simple Image
```powershell
# Create test Dockerfile
@"
FROM alpine:latest
CMD echo 'Docker is working!'
"@ | Out-File -FilePath Dockerfile.test -Encoding utf8

# Build
docker build -f Dockerfile.test -t test-image .

# Run
docker run test-image

# Clean up
del Dockerfile.test
docker rmi test-image
```

---

## 🔧 Troubleshooting

### Issue 1: "Docker Desktop requires a newer WSL kernel version"

**Solution:**
```powershell
# Update WSL
wsl --update

# Restart Docker Desktop
```

### Issue 2: "WSL 2 installation is incomplete"

**Solution:**
```powershell
# Download WSL 2 kernel update
# Visit: https://aka.ms/wsl2kernel

# Or use Windows Update
wsl --update
```

### Issue 3: "Virtualization is not enabled"

**Solution:**
1. Restart computer
2. Enter BIOS (usually F2, F10, or DEL during startup)
3. Find "Virtualization Technology" or "VT-x"
4. Enable it
5. Save and restart

### Issue 4: "Docker daemon is not running"

**Solution:**
```powershell
# Restart Docker Desktop
# Or restart Docker service
Restart-Service docker
```

### Issue 5: "Access denied" errors

**Solution:**
```powershell
# Run PowerShell as Administrator
# Or add your user to docker-users group
net localgroup docker-users "YOUR_USERNAME" /add
```

Then log out and log back in.

---

## 📦 Now Deploy Your Project

Once Docker is installed, you can:

### Option 1: Deploy Locally
```powershell
cd D:\Projects\AI_in_Education
docker-compose up -d
```

### Option 2: Deploy to GHCR
```powershell
cd D:\Projects\AI_in_Education
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN"
```

---

## 🎯 Quick Commands Reference

```powershell
# Start Docker Desktop
# (Use GUI or wait for auto-start)

# Check if Docker is running
docker ps

# View Docker version
docker --version

# List images
docker images

# List containers
docker ps -a

# Stop all containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Clean up everything
docker system prune -a --volumes
```

---

## 🌐 Alternative: Docker on Linux (WSL2)

If you want to use Docker inside WSL2:

```bash
# Inside WSL2 Ubuntu
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo service docker start

# Add user to docker group
sudo usermod -aG docker $USER

# Restart WSL
exit
# (Close and reopen WSL)

# Test
docker run hello-world
```

---

## ✅ Installation Checklist

- [ ] Download Docker Desktop
- [ ] Install Docker Desktop
- [ ] Enable WSL 2
- [ ] Restart computer
- [ ] Start Docker Desktop
- [ ] Run `docker --version`
- [ ] Run `docker run hello-world`
- [ ] Configure resources (8GB RAM)
- [ ] Test with your project

---

## 📚 Next Steps

After Docker is installed:

1. **Test Local Deployment**
   ```powershell
   cd D:\Projects\AI_in_Education
   docker-compose up -d
   ```

2. **Build Your Image**
   ```powershell
   docker build -f Dockerfile.prod -t ai-education:latest .
   ```

3. **Deploy to GHCR**
   - See `DEPLOY_TO_GHCR.md`
   - Run `deploy-to-ghcr.ps1`

---

## 🆘 Need Help?

- **Docker Docs**: https://docs.docker.com/desktop/install/windows-install/
- **WSL 2 Setup**: https://learn.microsoft.com/en-us/windows/wsl/install
- **Docker Forum**: https://forums.docker.com/

---

## 🎉 Success!

Once you see:
```
docker --version
Docker version 24.x.x, build xxxxx
```

You're ready to containerize your AI Education Platform! 🐳🚀
