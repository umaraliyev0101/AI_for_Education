# ============================================================================
# AI Education Platform - Dockerfile
# ============================================================================
# Multi-stage build for optimized production image

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# ============================================================================
# Builder Stage - Install dependencies
# ============================================================================
FROM base as builder

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================================
# Runtime Stage - Final image
# ============================================================================
FROM base as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p \
    uploads/faces \
    uploads/materials \
    uploads/presentations \
    uploads/audio \
    uploads/slides \
    uploads/audio/presentations \
    vector_stores/lesson_materials \
    logs \
    && chmod -R 755 uploads vector_stores logs

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run database initialization and start server
CMD ["sh", "-c", "python -m backend.init_db && gunicorn backend.main:app --workers ${GUNICORN_WORKERS:-4} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8001} --timeout 300 --keepalive 5 --access-logfile - --error-logfile - --log-level info"]
