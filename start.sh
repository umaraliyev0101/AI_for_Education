#!/bin/bash
# Production startup script

set -e  # Exit on error

echo "🚀 Starting AI Education Platform..."

# Set PYTHONPATH to ensure imports work
export PYTHONPATH=/app:$PYTHONPATH

# Wait for database to be ready (if using external DB)
# echo "⏳ Waiting for database..."
# python -c "import time; time.sleep(5)"

# Run database initialization
echo "📊 Initializing database..."
python -m backend.init_db || echo "⚠️  Database initialization skipped (may already exist)"

# Start the application with Gunicorn
echo "🔧 Starting application server..."
if [ -n "$GUNICORN_WORKERS" ]; then
    WORKERS=$GUNICORN_WORKERS
else
    WORKERS=4
fi

echo "✅ Starting with $WORKERS workers on port ${PORT:-8001}"

exec gunicorn backend.main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8001} \
    --timeout 300 \
    --keepalive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
