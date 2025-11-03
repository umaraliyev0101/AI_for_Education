# Automatic Redeployment from GHCR

## Current Behavior

When you push changes to GitHub:
1. ✅ GitHub Actions builds new Docker image
2. ✅ Image pushed to GHCR with `latest` tag
3. ❌ Server **does NOT automatically redeploy**

You must manually pull and restart on your server.

## Solutions for Automatic Redeployment

### Option 1: Watchtower (Easiest - Recommended)

Watchtower automatically checks for new images and redeploys.

**On Your Server:**

1. Create `docker-compose.watchtower.yml`:

```yaml
version: '3.8'

services:
  # Your application
  app:
    image: ghcr.io/umaraliyev0101/ai_for_education:latest
    container_name: ai-education-app
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=sqlite:///./ai_education.db
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
    volumes:
      - ./uploads:/app/uploads
      - ./vector_stores:/app/vector_stores
      - ./lesson_materials:/app/lesson_materials
      - ./ai_education.db:/app/ai_education.db
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  # Watchtower - auto-updates containers
  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ~/.docker/config.json:/config.json:ro
    environment:
      - WATCHTOWER_POLL_INTERVAL=300  # Check every 5 minutes
      - WATCHTOWER_CLEANUP=true       # Remove old images
      - WATCHTOWER_INCLUDE_RESTARTING=true
      - WATCHTOWER_LABEL_ENABLE=true  # Only update labeled containers
      - WATCHTOWER_NOTIFICATIONS=shoutrrr://telegram://token@telegram?channels=channel
    command: --interval 300 --cleanup
```

2. Authenticate Docker with GHCR:

```bash
# Create GitHub Personal Access Token with read:packages permission
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin
```

3. Start services:

```bash
docker-compose -f docker-compose.watchtower.yml up -d
```

4. Verify Watchtower is running:

```bash
docker logs watchtower -f
```

**How it works:**
- Watchtower checks GHCR every 5 minutes (300 seconds)
- If new image found, automatically pulls and restarts
- Old images are cleaned up
- Zero downtime deployment
- Optional: Get notifications via Telegram/Slack/Email

**Pros:**
- ✅ Simple setup
- ✅ No GitHub secrets needed
- ✅ Works with any registry
- ✅ Automatic cleanup

**Cons:**
- ❌ Polls every 5 minutes (slight delay)
- ❌ No deployment history
- ❌ Less control over deployment

---

### Option 2: GitHub Actions SSH Deploy (More Control)

Deploy directly from GitHub Actions to your server via SSH.

**Step 1: Add Server Secrets to GitHub**

Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:
- `SERVER_HOST`: Your server IP/domain (e.g., `123.45.67.89`)
- `SERVER_USER`: SSH username (e.g., `root`, `ubuntu`)
- `SERVER_SSH_KEY`: Your private SSH key (content of `~/.ssh/id_rsa`)

**Step 2: Create Deployment Script**

Save this as `deploy.sh` in your project root:

```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Authenticate with GHCR
echo "$GITHUB_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin

# Pull latest image
echo "📥 Pulling latest image..."
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest

# Stop current container
echo "🛑 Stopping current container..."
docker-compose -f docker-compose.prod.yml down || true

# Start with new image
echo "▶️ Starting new container..."
docker-compose -f docker-compose.prod.yml up -d

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -af --filter "until=24h"

echo "✅ Deployment complete!"

# Show status
docker ps
```

Make it executable:
```bash
chmod +x deploy.sh
```

**Step 3: Update GitHub Actions Workflow**

Add this deploy job to `.github/workflows/docker-build.yml`:

```yaml
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        port: 22
        envs: GITHUB_TOKEN
        script: |
          cd /path/to/your/app
          export GITHUB_TOKEN=$GITHUB_TOKEN
          ./deploy.sh
    
    - name: Deployment Summary
      run: |
        echo "### 🚀 Deployment Complete" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "**Server:** ${{ secrets.SERVER_HOST }}" >> $GITHUB_STEP_SUMMARY
        echo "**Time:** $(date)" >> $GITHUB_STEP_SUMMARY
        echo "**Image:** ghcr.io/umaraliyev0101/ai_for_education:latest" >> $GITHUB_STEP_SUMMARY
```

**Pros:**
- ✅ Instant deployment after build
- ✅ Full deployment history in GitHub Actions
- ✅ Can run tests before deploy
- ✅ More control

**Cons:**
- ❌ Requires SSH access setup
- ❌ Needs GitHub secrets configuration
- ❌ More complex

---

### Option 3: Manual Deployment Script (Simple)

If you prefer manual control, create this script on your server.

Save as `update.sh`:

```bash
#!/bin/bash
echo "🔄 Updating AI Education Platform..."

# Authenticate
echo "$GITHUB_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin

# Pull and restart
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Cleanup
docker image prune -af

echo "✅ Update complete!"
```

Run when you want to update:
```bash
./update.sh
```

---

## Comparison Table

| Feature | Watchtower | GitHub Actions | Manual |
|---------|-----------|----------------|--------|
| Setup Difficulty | ⭐ Easy | ⭐⭐⭐ Medium | ⭐ Easy |
| Deployment Speed | 5 min delay | Instant | Instant |
| Automation | Fully automatic | Fully automatic | Manual |
| GitHub Secrets | Not needed | Required | Not needed |
| Deployment History | None | Full logs | None |
| Rollback | Manual | Can automate | Manual |
| Best For | Small projects | Production apps | Dev/Testing |

---

## Recommended Setup

**For Your Use Case:** I recommend **Watchtower** because:

1. ✅ Simple to set up (just add watchtower service)
2. ✅ No GitHub secrets needed
3. ✅ Automatic deployment
4. ✅ Low maintenance
5. ✅ Good enough for most production apps

---

## Quick Start with Watchtower

Run these commands on your server:

```bash
# 1. Create the compose file
cat > docker-compose.watchtower.yml << 'EOF'
version: '3.8'
services:
  app:
    image: ghcr.io/umaraliyev0101/ai_for_education:latest
    container_name: ai-education-app
    restart: unless-stopped
    ports:
      - "8001:8001"
    volumes:
      - ./uploads:/app/uploads
      - ./vector_stores:/app/vector_stores
      - ./ai_education.db:/app/ai_education.db
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ~/.docker/config.json:/config.json:ro
    environment:
      - WATCHTOWER_POLL_INTERVAL=300
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_LABEL_ENABLE=true
    command: --interval 300 --cleanup
EOF

# 2. Login to GHCR
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin

# 3. Start everything
docker-compose -f docker-compose.watchtower.yml up -d

# 4. Watch logs
docker logs watchtower -f
```

**Done!** Now when you push to GitHub:
1. GitHub Actions builds new image (15-25 min)
2. Image pushed to GHCR
3. Within 5 minutes, Watchtower detects new image
4. Watchtower pulls and restarts your app
5. Old images cleaned up

Total time from push to live: ~20-30 minutes

---

## Testing the Setup

1. Make a small change (e.g., update README.md)
2. Commit and push to GitHub
3. Watch GitHub Actions complete
4. Wait 5 minutes
5. Check Watchtower logs: `docker logs watchtower`
6. Verify app is updated: `docker ps` and check the image ID

---

## Troubleshooting

### Watchtower Not Pulling Updates

```bash
# Check Watchtower logs
docker logs watchtower

# Force update now
docker exec watchtower watchtower --run-once

# Verify authentication
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest
```

### Authentication Issues

```bash
# Re-login to GHCR
echo "YOUR_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin

# Verify login
cat ~/.docker/config.json
```

### Image Not Updating

```bash
# Check if new image exists
docker pull ghcr.io/umaraliyev0101/ai_for_education:latest

# Compare image IDs
docker images | grep ai_for_education

# Check Watchtower interval
docker inspect watchtower | grep WATCHTOWER_POLL_INTERVAL
```

<function_calls>
<invoke name="read_file">
<parameter name="filePath">d:\Projects\AI_in_Education\.github\workflows\docker-build.yml
