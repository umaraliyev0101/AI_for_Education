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
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
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
