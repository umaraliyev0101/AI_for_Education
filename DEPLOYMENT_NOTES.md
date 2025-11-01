# Deployment Notes

This is the AI Education Platform application code.

## What You Have

- Complete FastAPI backend application
- Face recognition system
- Speech-to-text pipelines
- Q&A system with RAG
- All necessary Python dependencies

## What You Need to Add

Your friend should handle:
- Dockerfile / Docker Compose setup
- Nginx configuration (if needed)
- SSL certificates
- CI/CD pipeline
- Monitoring & logging
- Backup strategy

## Quick Start for Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY

# Initialize database
python backend/init_db.py

# Run server
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

## What Your Friend Will Do

They will create their own:
- Production Dockerfile
- docker-compose.yml for orchestration
- Deployment scripts
- Infrastructure setup
- Monitoring tools

## Application Details

- **Port**: 8001 (default)
- **Database**: SQLite (default), PostgreSQL ready
- **Requirements**: Python 3.11+, 8GB RAM recommended
- **ML Models**: Downloaded automatically on first run

## API Documentation

Once running:
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

---

Hand this repository to your friend and they'll handle the deployment infrastructure! 🚀
