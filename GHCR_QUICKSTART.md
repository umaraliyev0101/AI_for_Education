# 📦 GHCR Quick Reference

## 🚀 Quick Deploy (3 Commands)

### 1. Get GitHub Token
Go to: https://github.com/settings/tokens/new
- Select: `write:packages`
- Copy token

### 2. Run Deploy Script

**Windows:**
```powershell
.\deploy-to-ghcr.ps1 -GitHubToken "YOUR_TOKEN_HERE"
```

**Linux/Mac:**
```bash
chmod +x deploy-to-ghcr.sh
./deploy-to-ghcr.sh YOUR_TOKEN_HERE
```

### 3. Done! 🎉

Your image is at: `ghcr.io/umaraliyev0101/ai-education:latest`

---

## 📥 Pull & Run

```bash
docker pull ghcr.io/umaraliyev0101/ai-education:latest
docker run -d -p 8001:8001 ghcr.io/umaraliyev0101/ai-education:latest
```

---

## 🔧 Manual Steps

```bash
# 1. Login
echo YOUR_TOKEN | docker login ghcr.io -u umaraliyev0101 --password-stdin

# 2. Build
docker build -f Dockerfile.prod -t ai-education:latest .

# 3. Tag
docker tag ai-education:latest ghcr.io/umaraliyev0101/ai-education:latest

# 4. Push
docker push ghcr.io/umaraliyev0101/ai-education:latest
```

---

## 🤖 Automatic Deploy

Just push to GitHub:
```bash
git add .
git commit -m "Deploy update"
git push origin main
```

GitHub Actions will automatically build and push!

---

## 📚 Full Guide

See **DEPLOY_TO_GHCR.md** for complete documentation.
