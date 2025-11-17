"""
System Health Check Script
Comprehensive verification of all AI Education Platform components
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_item(name, status, details=""):
    """Print check result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def main():
    print_header("System Health Check")
    
    all_good = True
    
    # 1. Python Environment
    print("\n[Python Environment]")
    check_item("Python Version", sys.version_info >= (3, 9), 
               f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # 2. Core Dependencies
    print("\n[Core Dependencies]")
    dependencies = {
        "torch": "PyTorch (Deep Learning)",
        "transformers": "Hugging Face Transformers",
        "fastapi": "FastAPI (Backend)",
        "sqlalchemy": "SQLAlchemy (Database)",
        "langchain": "LangChain (LLM Chain)",
        "faiss": "FAISS (Vector Store)",
        "uvicorn": "Uvicorn (ASGI Server)"
    }
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            check_item(description, True, f"Module: {module}")
        except ImportError:
            check_item(description, False, f"Module: {module} - NOT FOUND")
            all_good = False
    
    # 3. CUDA/GPU Check
    print("\n[GPU/CUDA Status]")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        check_item("CUDA Available", cuda_available)
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            device_count = torch.cuda.device_count()
            check_item("GPU Device", True, f"{device_name} (Count: {device_count})")
            check_item("CUDA Version", True, f"PyTorch compiled with CUDA {torch.version.cuda}")
        else:
            print("   ⚠️  Running on CPU - Inference will be slower")
            print("   💡 For faster performance, install CUDA-enabled PyTorch:")
            print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
    except Exception as e:
        check_item("GPU Check", False, str(e))
    
    # 4. LLM Model
    print("\n[LLM Model Status]")
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        model_name = "google/flan-t5-base"
        print(f"   Loading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        check_item("Tokenizer", True, "Loaded successfully")
        
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        check_item("Model", True, "Loaded successfully")
        
        # Test inference
        inputs = tokenizer("Hello, how are you?", return_tensors="pt")
        outputs = model.generate(**inputs, max_length=20)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        check_item("Inference Test", True, f"Output: '{result}'")
    except Exception as e:
        check_item("Model Loading", False, str(e))
        all_good = False
    
    # 5. STT Pipelines
    print("\n[Speech-to-Text Pipelines]")
    stt_modules = [
        ("stt_pipelines.uzbek_hf_pipeline", "Uzbek HF Pipeline"),
        ("stt_pipelines.uzbek_whisper_pipeline", "Uzbek Whisper Pipeline"),
        ("stt_pipelines.uzbek_tts_pipeline", "Uzbek TTS Pipeline")
    ]
    
    for module_path, name in stt_modules:
        try:
            __import__(module_path)
            check_item(name, True, f"Module: {module_path}")
        except ImportError as e:
            check_item(name, False, f"{module_path} - {str(e)}")
    
    # 6. Utils/Services
    print("\n[Utility Services]")
    util_modules = [
        ("utils.uzbek_llm_qa_service", "LLM Q&A Service"),
        ("utils.uzbek_text_postprocessor", "Text Post-processor"),
        ("utils.uzbek_materials_processor", "Materials Processor")
    ]
    
    for module_path, name in util_modules:
        try:
            __import__(module_path)
            check_item(name, True, f"Module: {module_path}")
        except ImportError as e:
            check_item(name, False, f"{module_path} - {str(e)}")
    
    # 7. Backend Components
    print("\n[Backend Components]")
    backend_modules = [
        ("backend.main", "Main Application"),
        ("backend.database", "Database"),
        ("backend.auth", "Authentication"),
        ("backend.routes.lessons", "Lessons Routes"),
        ("backend.routes.qa", "Q&A Routes"),
        ("backend.routes.students", "Students Routes")
    ]
    
    for module_path, name in backend_modules:
        try:
            __import__(module_path)
            check_item(name, True, f"Module: {module_path}")
        except ImportError as e:
            check_item(name, False, f"{module_path} - {str(e)}")
    
    # 8. Directory Structure
    print("\n[Directory Structure]")
    required_dirs = [
        "uploads/audio",
        "uploads/faces",
        "uploads/materials",
        "uploads/presentations",
        "uploads/slides",
        "vector_stores/lesson_materials",
        "lesson_materials",
        "backend",
        "utils",
        "stt_pipelines"
    ]
    
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        check_item(f"Directory: {dir_path}", exists)
        if not exists:
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"   📁 Created missing directory")
            except Exception as e:
                all_good = False
    
    # 9. Database
    print("\n[Database]")
    db_path = "ai_education.db"
    db_exists = os.path.exists(db_path)
    check_item("Database File", db_exists, f"Location: {db_path}")
    
    if db_exists:
        try:
            from sqlalchemy import create_engine, inspect
            engine = create_engine(f"sqlite:///{db_path}")
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            check_item("Database Tables", len(tables) > 0, f"Found {len(tables)} tables: {', '.join(tables)}")
        except Exception as e:
            check_item("Database Connection", False, str(e))
    
    # 10. Configuration
    print("\n[Configuration]")
    try:
        from backend.config import settings
        check_item("Settings Module", True, "Loaded successfully")
        check_item("Secret Key", hasattr(settings, 'SECRET_KEY'), 
                  "Present" if hasattr(settings, 'SECRET_KEY') else "Missing")
        check_item("Upload Directories", hasattr(settings, 'UPLOAD_DIR'),
                  f"{settings.UPLOAD_DIR}" if hasattr(settings, 'UPLOAD_DIR') else "Not configured")
    except Exception as e:
        check_item("Configuration", False, str(e))
        all_good = False
    
    # Summary
    print_header("Summary")
    if all_good:
        print("\n✅ All critical components are operational!")
        print("✅ System is ready to run")
        print("\n💡 Next steps:")
        print("   1. Run: start_backend.bat")
        print("   2. Access API at: http://localhost:8000")
        print("   3. View API docs at: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some components have issues")
        print("⚠️  Please review the errors above")
        print("\n💡 Common fixes:")
        print("   1. Reinstall dependencies: pip install -r requirements.txt")
        print("   2. Check Python version: python --version (need 3.9+)")
        print("   3. Run database init: python -m backend.init_db")
    
    print("\n" + "="*60)
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
