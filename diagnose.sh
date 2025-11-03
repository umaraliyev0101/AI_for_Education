#!/bin/bash
# Server Diagnostic Script for Error 503

echo "=================================="
echo "AI Education Platform Diagnostics"
echo "=================================="
echo ""

# Check Docker
echo "1. Docker Status:"
docker --version 2>/dev/null || echo "❌ Docker not found"
echo ""

# Check containers
echo "2. Containers Status:"
docker ps -a | grep -E "CONTAINER|ai-education|watchtower" || echo "❌ No containers found"
echo ""

# Check logs
echo "3. Application Logs (last 30 lines):"
docker logs ai-education-app --tail 30 2>/dev/null || echo "❌ Cannot access logs"
echo ""

# Health check
echo "4. Health Check:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health check passed (200 OK)"
    curl -s http://localhost:8001/health
elif [ "$HTTP_CODE" = "503" ]; then
    echo "❌ Error 503 - Service Unavailable"
else
    echo "❌ Health check failed with HTTP $HTTP_CODE"
fi
echo ""

# Port check
echo "5. Port 8001 Status:"
netstat -tlnp 2>/dev/null | grep 8001 || lsof -i :8001 2>/dev/null || echo "❌ Port 8001 not listening"
echo ""

# Resources
echo "6. System Resources:"
echo "Disk Space:"
df -h | grep -E "Filesystem|/$"
echo ""
echo "Memory:"
free -h
echo ""
echo "Docker Stats:"
docker stats --no-stream 2>/dev/null | grep -E "CONTAINER|ai-education" || echo "No container stats"
echo ""

# Images
echo "7. Docker Images:"
docker images | grep -E "REPOSITORY|ai_for_education|ai-education" || echo "No images found"
echo ""

# Environment
echo "8. Environment File:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    echo "Keys found: $(grep -o '^[A-Z_]*=' .env | tr '\n' ', ' | sed 's/,$//')"
else
    echo "❌ .env file not found"
fi
echo ""

# Network
echo "9. Network Connectivity:"
ping -c 1 ghcr.io > /dev/null 2>&1 && echo "✅ Can reach ghcr.io" || echo "❌ Cannot reach ghcr.io"
echo ""

# Recommendations
echo "=================================="
echo "RECOMMENDATIONS:"
echo "=================================="

if ! docker ps | grep -q ai-education-app; then
    echo "⚠️  Container not running!"
    echo "   Try: docker-compose -f docker-compose.prod.yml up -d"
    echo ""
fi

if [ "$HTTP_CODE" = "503" ]; then
    echo "⚠️  Error 503 detected!"
    echo "   1. Check logs: docker logs ai-education-app -f"
    echo "   2. Restart: docker restart ai-education-app"
    echo "   3. Rebuild: docker-compose -f docker-compose.prod.yml up -d --force-recreate"
    echo ""
fi

# Show most recent log errors
echo "10. Recent Errors in Logs:"
docker logs ai-education-app 2>&1 | grep -i "error\|exception\|failed\|traceback" | tail -10 || echo "No recent errors found"
echo ""

echo "=================================="
echo "Diagnostic Complete"
echo "=================================="
