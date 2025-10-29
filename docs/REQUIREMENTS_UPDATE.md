# Requirements Update Summary

## Changes Made to Dependencies

### New Packages Added

#### 1. **websockets>=12.0**
- **Purpose**: Real-time WebSocket communication for live lesson management
- **Used in**: `backend/routes/websocket.py`
- **Features**: Live attendance updates, presentation control, Q&A during lessons

#### 2. **apscheduler>=3.10.4**
- **Purpose**: Task scheduling for automatic lesson start at 8AM
- **Used in**: `backend/services/lesson_session_service.py`
- **Features**: Background scheduler, time-based lesson automation

#### 3. **python-dateutil>=2.8.2**
- **Purpose**: Enhanced date/time utilities for scheduling
- **Used in**: Lesson scheduling and time comparisons

### Existing Packages (Already in requirements)

These packages were already present and are used for the new features:

- **PyPDF2>=3.0.0** - PDF presentation processing
- **python-pptx>=0.6.21** - PowerPoint presentation processing
- **edge-tts>=6.1.0** - Uzbek text-to-speech for audio generation
- **pygame** - Audio playback for TTS
- **facenet-pytorch** - Face recognition for attendance
- **opencv-python** - Computer vision for face detection
- **transformers** - STT models for audio questions

## Installation Instructions

### Quick Install (Recommended)

```bash
# Activate virtual environment
venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate    # Linux/Mac

# Install/update all dependencies
pip install -r requirements.txt --upgrade
```

### Install Only New Packages

If you already have the base installation:

```bash
pip install websockets>=12.0 apscheduler>=3.10.4 python-dateutil>=2.8.2
```

### Verify Installation

Run the test script:

```bash
python test_backend_setup.py
```

Expected output:
```
✅ WebSocket Support
✅ Task Scheduling
✅ Presentation Processing
✅ Text-to-Speech
✅ Face Recognition
🎉 All packages installed successfully!
```

## Files Updated

### 1. **requirements.txt**
- ✅ Cleaned up and organized
- ✅ Removed duplicate entries
- ✅ Added version constraints
- ✅ Added new dependencies

### 2. **backend_requirements.txt**
- ✅ Updated with complete backend stack
- ✅ Includes all necessary dependencies
- ✅ Organized by category

### 3. **New Documentation Files**
- ✅ `INSTALL_BACKEND_IMPROVEMENTS.md` - Installation guide
- ✅ `test_backend_setup.py` - Verification script
- ✅ `REQUIREMENTS_UPDATE.md` - This file

## Dependency Categories

### Core Backend (Required)
- FastAPI, Uvicorn, SQLAlchemy, Pydantic
- Authentication: python-jose, passlib
- WebSocket: websockets

### AI/ML (Required for AI features)
- PyTorch, Transformers
- Sentence Transformers, LangChain, FAISS
- Face Recognition: facenet-pytorch, opencv-python

### Audio Processing (Required for TTS/STT)
- Edge TTS, pygame
- Librosa, soundfile

### Document Processing (Required for presentations)
- PyPDF2, python-pptx

### Scheduling (Required for auto-start)
- APScheduler

## Breaking Changes

None! All changes are **backward compatible**.

Existing functionality remains intact. The new dependencies only add new features.

## Troubleshooting

### Issue: "No module named 'websockets'"
```bash
pip install websockets>=12.0
```

### Issue: "No module named 'apscheduler'"
```bash
pip install apscheduler>=3.10.4
```

### Issue: PyTorch installation fails
```bash
# Install PyTorch separately first
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue: All installations fail
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then try again
pip install -r requirements.txt
```

## What Works Without New Packages?

If you can't install the new packages immediately:

| Feature | Works Without? |
|---------|---------------|
| Basic CRUD operations | ✅ Yes |
| User authentication | ✅ Yes |
| Manual attendance | ✅ Yes |
| Q&A (without audio) | ✅ Yes |
| **Real-time updates** | ❌ No (needs websockets) |
| **Auto-start lessons** | ❌ No (needs apscheduler) |
| **Presentation audio** | ❌ No (needs edge-tts) |
| **Face recognition** | ⚠️ Partial (needs opencv, facenet) |

## Recommended Installation Order

For systems with limited resources or slow internet:

1. **First (Core)**:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic
   ```

2. **Second (Backend Features)**:
   ```bash
   pip install websockets apscheduler python-jose passlib
   ```

3. **Third (Document Processing)**:
   ```bash
   pip install PyPDF2 python-pptx
   ```

4. **Fourth (Audio - Can be slow)**:
   ```bash
   pip install edge-tts pygame librosa soundfile
   ```

5. **Fifth (AI - Largest downloads)**:
   ```bash
   pip install torch transformers sentence-transformers
   pip install facenet-pytorch opencv-python
   ```

## Size Estimates

Approximate download sizes for new packages:

- **websockets**: ~50 KB
- **apscheduler**: ~100 KB
- **python-dateutil**: ~300 KB

**Total new dependencies**: < 1 MB (very lightweight!)

The heavy packages (PyTorch, Transformers, etc.) were already in requirements.

## Next Steps

After installation:

1. ✅ Run test script: `python test_backend_setup.py`
2. ✅ Start server: `python -m uvicorn backend.main:app --reload`
3. ✅ Check WebSocket: Connect to `ws://localhost:8000/api/ws/lesson/1`
4. ✅ Test presentation upload
5. ✅ Try auto-attendance scan

## Support

If you encounter issues:
- Check Python version (3.10+ recommended)
- Verify virtual environment is activated
- Review installation logs for specific errors
- Try installing packages individually
- See `INSTALL_BACKEND_IMPROVEMENTS.md` for detailed troubleshooting

---

**Summary**: Only 3 new lightweight packages added (~1MB total). All major dependencies were already present. Installation should be quick and smooth!
