# Essential Files for Deployment

This document lists the files needed for deployment and those that can be removed.

## ✅ KEEP - Essential Files

### Core Application
- `backend/` - All backend Python code
- `face_recognition/` - Face recognition modules
- `stt_pipelines/` - Speech-to-text pipelines
- `utils/` - Utility functions
- `requirements.txt` - Python dependencies
- `backend_requirements.txt` - Backend-specific dependencies (duplicate, but keeping for now)

### Docker & Deployment
- `Dockerfile.prod` - Production Docker image
- `docker-compose.prod.yml` - Production deployment
- `.dockerignore` - What to exclude from Docker builds
- `start.sh` - Production startup script
- `nginx.conf` - Nginx reverse proxy config

### GitHub Actions
- `.github/workflows/docker-build.yml` - Auto-build and push to GHCR

### Configuration
- `.env` (not in repo, created on server)
- `pyproject.toml` - Python project config
- `README.md` - Main documentation

### Database & Data
- `ai_education.db` (created at runtime)
- `lesson_materials/` - Lesson content
- `uploads/` - User uploads (created at runtime)
- `vector_stores/` - Vector database (created at runtime)

---

## ❌ REMOVE - Unnecessary Documentation

These are helpful guides but not needed for production deployment:

### Deployment Guides (DELETE)
- `AUTO_DEPLOY_SUMMARY.md`
- `AUTO_REDEPLOY.md`
- `COMPLETE_SETUP.md`
- `DEPLOY_TO_GHCR.md`
- `DEPLOYMENT.md`
- `DEPLOYMENT_DIAGRAM.txt`
- `DEPLOYMENT_SUMMARY.md`
- `DOCKER_README.md`
- `DOCKER_SUMMARY.md`
- `GHCR_QUICKSTART.md`
- `QUICKSTART.md`
- `SERVER_SETUP.md`

### Troubleshooting Guides (DELETE)
- `ERROR_503_QUICKFIX.md`
- `FIX_DOCKER_BUILD.md`
- `FIX_GITHUB_ACTIONS.md`
- `FIX_MODULE_NOT_FOUND.md`
- `INSTALL_DOCKER.md`
- `LOCAL_BUILD_GUIDE.md`
- `QUICKFIX_MODULE_ERROR.md`
- `START_HERE.md`
- `TROUBLESHOOT_503.md`

### Test/Development Scripts (DELETE)
- `deploy-to-ghcr.ps1` - Manual deployment script
- `deploy-to-ghcr.sh` - Manual deployment script
- `diagnose.sh` - Diagnostic script
- `test_deployment.ps1` - Testing script
- `test_deployment.sh` - Testing script
- `test-docker-build.ps1` - Local testing script

### Development Files (DELETE OR KEEP LOCAL)
- `Dockerfile` - Development Dockerfile (keep prod only)
- `docker-compose.yml` - Development compose file
- `docker-compose.watchtower.yml` - Watchtower setup (optional)
- `start.ps1` - Windows development script
- `test_backend_setup.py` - Backend tests
- `test_qa_system.py` - QA system tests
- `main.py` - Root-level duplicate (backend/main.py is used)

---

## 🔧 Optional - Deployment Helpers

Keep these if your friend wants easier deployment:

### Keep for Easy Deployment
- `docker-compose.watchtower.yml` - Auto-update setup
- `diagnose.sh` - Server troubleshooting
- One simple deployment guide (create new one below)

### Remove Everything Else
All the other MD files and scripts are redundant.

---

## Cleanup Commands

Run these to clean up:

```powershell
# Remove documentation
Remove-Item AUTO_DEPLOY_SUMMARY.md
Remove-Item AUTO_REDEPLOY.md
Remove-Item COMPLETE_SETUP.md
Remove-Item DEPLOY_TO_GHCR.md
Remove-Item DEPLOYMENT.md
Remove-Item DEPLOYMENT_DIAGRAM.txt
Remove-Item DEPLOYMENT_SUMMARY.md
Remove-Item DOCKER_README.md
Remove-Item DOCKER_SUMMARY.md
Remove-Item ERROR_503_QUICKFIX.md
Remove-Item FIX_DOCKER_BUILD.md
Remove-Item FIX_GITHUB_ACTIONS.md
Remove-Item FIX_MODULE_NOT_FOUND.md
Remove-Item GHCR_QUICKSTART.md
Remove-Item INSTALL_DOCKER.md
Remove-Item LOCAL_BUILD_GUIDE.md
Remove-Item QUICKFIX_MODULE_ERROR.md
Remove-Item QUICKSTART.md
Remove-Item SERVER_SETUP.md
Remove-Item START_HERE.md
Remove-Item TROUBLESHOOT_503.md

# Remove scripts
Remove-Item deploy-to-ghcr.ps1
Remove-Item deploy-to-ghcr.sh
Remove-Item test_deployment.ps1
Remove-Item test_deployment.sh
Remove-Item test-docker-build.ps1
Remove-Item start.ps1

# Remove dev Docker files
Remove-Item Dockerfile
Remove-Item docker-compose.yml

# Remove test files (optional - might want to keep for CI/CD)
Remove-Item test_backend_setup.py
Remove-Item test_qa_system.py

# Remove duplicate
Remove-Item main.py
Remove-Item backend_requirements.txt  # Duplicate of requirements.txt

# Commit changes
git add .
git commit -m "cleanup: remove unnecessary documentation and scripts"
git push
```

---

## Final Essential File List

After cleanup, you should have:

```
AI_in_Education/
├── .github/
│   └── workflows/
│       └── docker-build.yml          # Auto-build on push
├── backend/                          # All backend code
├── face_recognition/                 # Face recognition
├── stt_pipelines/                    # Speech-to-text
├── utils/                            # Utilities
├── lesson_materials/                 # Lesson content
├── sample_materials/                 # Sample data
├── .dockerignore                     # Docker exclusions
├── .gitignore                        # Git exclusions
├── Dockerfile.prod                   # Production image
├── docker-compose.prod.yml           # Production deployment
├── docker-compose.watchtower.yml     # (Optional) Auto-update
├── diagnose.sh                       # (Optional) Troubleshooting
├── nginx.conf                        # Nginx config
├── pyproject.toml                    # Python config
├── README.md                         # Main docs
├── requirements.txt                  # Dependencies
└── start.sh                          # Startup script
```

Clean, simple, production-ready! 🚀
