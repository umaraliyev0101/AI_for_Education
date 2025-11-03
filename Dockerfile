<<<<<<< HEAD
# Multi-stage build for AI Education Platform
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libsndfile1 \
    ffmpeg \
    portaudio19-dev \
    python3-dev \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt backend_requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r backend_requirements.txt && \
=======
# Dockerfile for AI Education Platform
# Optimized for Salad.com GPU deployment

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    libsndfile1 \
    portaudio19-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
>>>>>>> 9d3194643313e828d1a935b9119966e8df07bda4
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
<<<<<<< HEAD
RUN mkdir -p \
    uploads/audio \
    uploads/faces \
    uploads/materials \
    uploads/presentations \
    uploads/slides \
    vector_stores/lesson_materials \
    lesson_materials \
    sample_materials

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Run database initialization and start server
CMD ["sh", "-c", "python backend/init_db.py && uvicorn backend.main:app --host 0.0.0.0 --port 8001"]
=======
RUN mkdir -p uploads/faces \
    uploads/materials \
    uploads/presentations \
    uploads/audio \
    uploads/slides \
    uploads/audio/presentations \
    vector_stores

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Initialize database on startup and run the application
CMD python backend/init_db.py && \
    uvicorn backend.main:app --host 0.0.0.0 --port ${PORT} --workers 1
>>>>>>> 9d3194643313e828d1a935b9119966e8df07bda4
