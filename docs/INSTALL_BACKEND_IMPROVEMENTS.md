# Installation Guide for Backend Improvements

## Quick Installation

### Option 1: Install All Requirements (Recommended)
```bash
# Activate your virtual environment first
venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate   # Linux/Mac

# Install all dependencies
pip install -r requirements.txt
```

### Option 2: Install Only Backend Requirements
```bash
# Activate your virtual environment
venv\Scripts\Activate.ps1  # Windows PowerShell

# Install backend-specific dependencies
pip install -r backend_requirements.txt
```

## New Dependencies Added

### Core Backend Enhancements
- **websockets>=12.0** - Real-time WebSocket communication for live lessons
- **apscheduler>=3.10.4** - Task scheduling for auto-starting lessons at 8AM

### Presentation Processing
- **PyPDF2>=3.0.0** - PDF text extraction
- **python-pptx>=0.6.21** - PowerPoint presentation processing

### Face Recognition (Already included, but ensuring compatibility)
- **facenet-pytorch>=2.5.0** - Face recognition model
- **opencv-python>=4.8.0** - Computer vision for face detection
- **Pillow>=10.0.0** - Image processing

### Text-to-Speech
- **edge-tts>=6.1.0** - Microsoft Edge TTS for Uzbek language
- **pygame>=2.5.0** - Audio playback

### Speech-to-Text (Already included)
- **librosa>=0.10.0** - Audio processing
- **soundfile>=0.12.0** - Audio file handling
- **transformers>=4.30.0** - Hugging Face models

### LLM & RAG (Already included)
- **sentence-transformers>=2.2.0** - Embeddings for RAG
- **langchain>=0.1.0** - LLM framework
- **faiss-cpu>=1.7.0** - Vector similarity search

## Verification

After installation, verify the key packages:

```bash
# Check FastAPI
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# Check WebSocket support
python -c "import websockets; print(f'WebSockets {websockets.__version__}')"

# Check TTS
python -c "import edge_tts; print('Edge TTS installed')"

# Check Presentation processing
python -c "import pptx; print('python-pptx installed')"
python -c "import PyPDF2; print('PyPDF2 installed')"

# Check Face Recognition
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"
python -c "from facenet_pytorch import MTCNN; print('FaceNet PyTorch installed')"

# Check Scheduler
python -c "import apscheduler; print('APScheduler installed')"
```

## Troubleshooting

### Issue: PyTorch installation fails
**Solution**: Install PyTorch separately first:
```bash
# CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU version (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: OpenCV import error
**Solution**: Try installing opencv-python-headless:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### Issue: Edge TTS not working
**Solution**: Ensure you have internet connection (Edge TTS uses Microsoft's cloud service)

### Issue: WebSocket connection fails
**Solution**: Make sure uvicorn supports WebSockets:
```bash
pip install uvicorn[standard]
```

## Running the Server

After installation:

```bash
# Navigate to backend directory
cd backend

# Run the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✅ AI Education Backend v1.0.0 started
📊 Database: sqlite:///./ai_education.db
🔧 Debug mode: True
📅 Lesson scheduler: Active
```

## Testing Installation

Quick test script:

```python
# test_installation.py
import sys

packages = [
    ('fastapi', 'FastAPI'),
    ('websockets', 'WebSockets'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('edge_tts', 'Edge TTS'),
    ('pptx', 'python-pptx'),
    ('PyPDF2', 'PyPDF2'),
    ('cv2', 'OpenCV'),
    ('apscheduler', 'APScheduler'),
]

print("Checking installed packages...\n")

for module, name in packages:
    try:
        __import__(module)
        print(f"✅ {name}")
    except ImportError:
        print(f"❌ {name} - NOT INSTALLED")

print("\nInstallation check complete!")
```

Run it:
```bash
python test_installation.py
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Run the server
3. ✅ Check the documentation: `BACKEND_IMPROVEMENTS.md`
4. ✅ Test WebSocket connection
5. ✅ Upload a test presentation
6. ✅ Configure face recognition database

## Support

If you encounter any issues:
1. Check the error message carefully
2. Verify Python version (3.10+ recommended)
3. Ensure virtual environment is activated
4. Try installing packages individually
5. Check system compatibility (Windows/Linux/Mac)

## Minimal Requirements (If Full Install Fails)

If you can't install everything, here's the minimal set for basic functionality:

```bash
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings
pip install python-jose passlib python-multipart python-dotenv
pip install websockets
```

This will give you the core backend without AI features.
