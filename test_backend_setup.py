#!/usr/bin/env python3
"""
Test Backend Improvements Installation
Verify all new dependencies are properly installed
"""

import sys
from typing import List, Tuple

def check_package(module_name: str, display_name: str = None) -> bool:
    """Check if a package is installed"""
    if display_name is None:
        display_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {display_name}")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - NOT INSTALLED")
        print(f"   Error: {e}")
        return False

def check_version(module_name: str, display_name: str = None) -> bool:
    """Check package and display version"""
    if display_name is None:
        display_name = module_name
    
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {display_name} v{version}")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - NOT INSTALLED")
        return False

def main():
    print("="*60)
    print("Backend Improvements Installation Test")
    print("="*60)
    print()
    
    # Core Backend
    print("📦 Core Backend Packages:")
    print("-" * 60)
    core_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('pydantic', 'Pydantic'),
        ('jose', 'python-jose'),
    ]
    
    core_ok = all(check_version(pkg, name) for pkg, name in core_packages)
    print()
    
    # New WebSocket Support
    print("🔌 WebSocket Support:")
    print("-" * 60)
    websocket_ok = check_version('websockets', 'WebSockets')
    print()
    
    # Presentation Processing
    print("📊 Presentation Processing:")
    print("-" * 60)
    presentation_packages = [
        ('pptx', 'python-pptx'),
        ('PyPDF2', 'PyPDF2'),
    ]
    presentation_ok = all(check_version(pkg, name) for pkg, name in presentation_packages)
    print()
    
    # TTS Support
    print("🗣️ Text-to-Speech:")
    print("-" * 60)
    tts_ok = check_package('edge_tts', 'Edge TTS')
    pygame_ok = check_package('pygame', 'Pygame (Audio playback)')
    print()
    
    # Face Recognition
    print("👤 Face Recognition:")
    print("-" * 60)
    face_packages = [
        ('cv2', 'OpenCV'),
        ('PIL', 'Pillow'),
        ('facenet_pytorch', 'FaceNet PyTorch'),
    ]
    face_ok = all(check_package(pkg, name) for pkg, name in face_packages)
    print()
    
    # STT Support
    print("🎤 Speech-to-Text:")
    print("-" * 60)
    stt_packages = [
        ('librosa', 'Librosa'),
        ('soundfile', 'SoundFile'),
        ('transformers', 'Transformers'),
    ]
    stt_ok = all(check_package(pkg, name) for pkg, name in stt_packages)
    print()
    
    # LLM & RAG
    print("🤖 LLM & RAG:")
    print("-" * 60)
    llm_packages = [
        ('sentence_transformers', 'Sentence Transformers'),
        ('langchain', 'LangChain'),
        ('faiss', 'FAISS'),
    ]
    llm_ok = all(check_package(pkg, name) for pkg, name in llm_packages)
    print()
    
    # Task Scheduling
    print("⏰ Task Scheduling:")
    print("-" * 60)
    scheduler_ok = check_package('apscheduler', 'APScheduler')
    print()
    
    # Summary
    print("="*60)
    print("Installation Summary")
    print("="*60)
    
    results = {
        "Core Backend": core_ok,
        "WebSocket Support": websocket_ok,
        "Presentation Processing": presentation_ok,
        "Text-to-Speech": tts_ok and pygame_ok,
        "Face Recognition": face_ok,
        "Speech-to-Text": stt_ok,
        "LLM & RAG": llm_ok,
        "Task Scheduling": scheduler_ok,
    }
    
    for feature, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {feature}")
    
    print()
    
    all_ok = all(results.values())
    
    if all_ok:
        print("🎉 All packages installed successfully!")
        print("✅ Backend improvements are ready to use!")
        print()
        print("Next steps:")
        print("1. Start the server: python -m uvicorn backend.main:app --reload")
        print("2. Check documentation: BACKEND_IMPROVEMENTS.md")
        print("3. Test WebSocket connection")
        return 0
    else:
        print("⚠️ Some packages are missing!")
        print("Please install missing packages:")
        print("  pip install -r requirements.txt")
        print()
        print("Or install backend-specific packages:")
        print("  pip install -r backend_requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
