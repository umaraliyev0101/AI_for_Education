# Server Deployment with Auto-Update

## Quick Setup (5 minutes)

This guide shows you how to deploy your AI Education Platform on your server with automatic updates.

### Step 1: Upload Files to Server

Upload these files to your server (e.g., in `/opt/ai-education/`):

1. `docker-compose.watchtower.yml`
2. `.env` file with your secrets

```bash
# On your local machine
scp docker-compose.watchtower.yml user@your-server:/opt/ai-education/
scp .env user@your-server:/opt/ai-education/
```

### Step 2: Connect to Your Server

```bash
ssh user@your-server
cd /opt/ai-education
```

### Step 3: Create Required Directories

```bash
mkdir -p uploads/audio uploads/faces uploads/materials uploads/presentations uploads/slides
mkdir -p vector_stores/lesson_materials
mkdir -p lesson_materials
```

### Step 4: Login to GitHub Container Registry

You need a GitHub Personal Access Token with `read:packages` permission.

**Create Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `GHCR Read Access`
4. Select scopes: `read:packages`
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)

**Login:**
```bash
echo "ghp_YOUR_TOKEN_HERE" | docker login ghcr.io -u umaraliyev0101 --password-stdin
```

You should see: `Login Succeeded`

### Step 5: Start the Application

```bash
docker-compose -f docker-compose.watchtower.yml up -d
```

### Step 6: Verify It's Running

```bash
# Check containers
docker ps

# You should see:
# - ai-education-app (your application)
# - watchtower (auto-updater)

# Check logs
docker logs ai-education-app
docker logs watchtower
```

### Step 7: Test the Application

```bash
# Test health endpoint
curl http://localhost:8001/health

# Should return: {"status":"healthy"}

# Or test from browser
# http://your-server-ip:8001/docs
```

## ✅ Done!

Your application is now:
- ✅ Running on port 8001
- ✅ Automatically updates when you push to GitHub
- ✅ Restarts automatically if it crashes
- ✅ Cleans up old images

---

## How It Works

1. **You push code to GitHub** → GitHub Actions builds new Docker image
2. **Image pushed to GHCR** → Within 5 minutes, Watchtower detects it
3. **Watchtower pulls and restarts** → Your server now runs the new version
4. **Old images cleaned up** → No disk space wasted

**Total time from push to live: 20-30 minutes**

---

## Daily Operations

### View Logs

```bash
# Application logs
docker logs ai-education-app -f

# Watchtower logs (to see update activity)
docker logs watchtower -f

# Last 100 lines
docker logs ai-education-app --tail 100
```

### Restart Application

```bash
docker-compose -f docker-compose.watchtower.yml restart app
```

### Force Update Now

```bash
# Don't wait for Watchtower's 5-minute check
docker exec watchtower watchtower --run-once
```

### Stop Everything

```bash
docker-compose -f docker-compose.watchtower.yml down
```

### Start Again

```bash
docker-compose -f docker-compose.watchtower.yml up -d
```

### Check Update Status

```bash
# See when last update happened
docker logs watchtower | grep "Updated"

# Check current image version
docker inspect ai-education-app | grep Image
```

---

## Environment Variables

Edit your `.env` file on the server:

```bash
nano .env
```

Add:

```env
# Security (CHANGE THIS!)
SECRET_KEY=your-very-secret-key-minimum-32-characters

# Database
DATABASE_URL=sqlite:///./ai_education.db

# API
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# CORS (your frontend URLs)
ALLOWED_ORIGINS=http://localhost:3000,http://yourfrontend.com

# LLM Settings (if using OpenAI/Anthropic)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Debug
DEBUG=false
```

Then restart:
```bash
docker-compose -f docker-compose.watchtower.yml down
docker-compose -f docker-compose.watchtower.yml up -d
```

---

## Monitoring

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
df -h
du -sh /opt/ai-education/*

# Memory usage
free -h
```

### Health Checks

```bash
# Manual health check
curl http://localhost:8001/health

# Check if container is healthy
docker inspect ai-education-app --format='{{.State.Health.Status}}'
```

---

## Backup

### Backup Database

```bash
# Copy database
cp ai_education.db ai_education.db.backup.$(date +%Y%m%d)

# Or create daily backups with cron
crontab -e
# Add: 0 2 * * * cp /opt/ai-education/ai_education.db /opt/ai-education/backups/db.$(date +\%Y\%m\%d).bak
```

### Backup Uploads

```bash
# Tar all uploads
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/
```

### Restore from Backup

```bash
# Stop application
docker-compose -f docker-compose.watchtower.yml down

# Restore database
cp ai_education.db.backup.20250101 ai_education.db

# Start again
docker-compose -f docker-compose.watchtower.yml up -d
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker logs ai-education-app

# Common issues:
# - Port 8001 already in use: Change port in docker-compose.watchtower.yml
# - Database error: Delete ai_education.db and restart (will recreate)
# - Permission error: sudo chown -R 1000:1000 /opt/ai-education
```

### Watchtower Not Updating

```bash
# Check Watchtower logs
docker logs watchtower

# Re-authenticate with GHCR
echo "ghp_YOUR_TOKEN" | docker login ghcr.io -u umaraliyev0101 --password-stdin

# Force check now
docker exec watchtower watchtower --run-once
```

### Out of Disk Space

```bash
# Clean up old Docker images
docker system prune -a

# Clean up logs
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Check what's using space
du -sh /var/lib/docker/*
```

### Can't Access from Outside

```bash
# Check if port is open
sudo ufw allow 8001/tcp

# Or using firewalld
sudo firewall-cmd --add-port=8001/tcp --permanent
sudo firewall-cmd --reload

# Check if Docker is listening
netstat -tlnp | grep 8001
```

---

## Security Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Enable firewall (ufw/firewalld)
- [ ] Use strong passwords
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Consider adding SSL/TLS with nginx reverse proxy
- [ ] Limit SSH access (disable password auth, use keys only)

---

## Updating Configuration

If you need to change environment variables or settings:

1. Edit `.env` or `docker-compose.watchtower.yml`
2. Restart:
   ```bash
   docker-compose -f docker-compose.watchtower.yml down
   docker-compose -f docker-compose.watchtower.yml up -d
   ```

---

## Getting Updates

To check if there's a new version:

```bash
# Check GitHub for new commits
# Your server will auto-update within 5 minutes after GitHub Actions completes

# Or force update now
docker exec watchtower watchtower --run-once
```

---

## Monitoring Logs in Real-Time

```bash
# All logs together
docker-compose -f docker-compose.watchtower.yml logs -f

# Just application
docker logs ai-education-app -f

# Just updates
docker logs watchtower -f
```

---

## Notifications (Optional)

Want to get notified when updates happen?

Edit `docker-compose.watchtower.yml` and add to Watchtower environment:

### Telegram

```yaml
- WATCHTOWER_NOTIFICATIONS=shoutrrr://telegram://YOUR_BOT_TOKEN@telegram?channels=YOUR_CHAT_ID
```

### Slack

```yaml
- WATCHTOWER_NOTIFICATIONS=shoutrrr://slack://YOUR_WEBHOOK_URL
```

### Email

```yaml
- WATCHTOWER_NOTIFICATIONS=shoutrrr://smtp://username:password@smtp.gmail.com:587/?from=you@gmail.com&to=you@gmail.com
```

Then restart Watchtower:
```bash
docker-compose -f docker-compose.watchtower.yml restart watchtower
```

---

## Production Checklist

Before going live:

- [ ] Application running: `docker ps`
- [ ] Health check passing: `curl http://localhost:8001/health`
- [ ] Watchtower running and authenticated
- [ ] Environment variables configured
- [ ] Firewall rules set
- [ ] SSL certificate installed (if needed)
- [ ] Database backed up
- [ ] Monitoring set up
- [ ] Logs being captured
- [ ] Test auto-update by pushing a small change

---

## Support

If you have issues:

1. Check logs: `docker logs ai-education-app`
2. Check Watchtower: `docker logs watchtower`
3. Test connection: `curl http://localhost:8001/health`
4. Verify authentication: `docker pull ghcr.io/umaraliyev0101/ai_for_education:latest`

Common GitHub Actions build time: 15-25 minutes
Watchtower check interval: 5 minutes
Total update time: ~20-30 minutes from git push
