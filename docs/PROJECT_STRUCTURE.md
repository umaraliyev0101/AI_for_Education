# Project Structure

## Directory Organization

```
AI_in_Education/
├── main.py                          # Main CLI entry point
├── requirements.txt                 # Python dependencies
├── pyproject.toml                  # Project configuration
├── README.md                        # Main project documentation
│
├── stt_pipelines/                   # Speech-to-Text Pipelines
│   ├── __init__.py
│   ├── uzbek_xlsr_pipeline.py      # XLS-R model (primary, 15.07% WER)
│   ├── uzbek_whisper_pipeline.py   # Whisper model (backup, ~30-35% WER)
│   ├── uzbek_hf_pipeline.py        # Hugging Face ASR pipeline
│   └── uzbek_tts_pipeline.py       # Text-to-Speech pipeline
│
├── face_recognition/                # Face Recognition System
│   ├── __init__.py
│   ├── face_recognition_db.py      # SQLite database management
│   ├── face_enrollment.py          # Student enrollment with FaceNet
│   └── face_attendance.py          # Real-time attendance tracking
│
├── utils/                           # Utility Modules
│   ├── __init__.py
│   ├── uzbek_text_postprocessor.py # Text post-processing
│   └── uzbek_accuracy_testing_framework.py  # WER/CER testing
│
├── docs/                            # Documentation
│   ├── FACE_RECOGNITION_README.md  # Face recognition guide
│   ├── COMPLETE_SYSTEM_DOCS.md     # Complete system documentation
│   └── PROJECT_STRUCTURE.md        # This file
│
├── data/                            # Data Files
│   ├── uzbek_xlsr_accuracy_report_xlsr_baseline.json
│   └── students.db                 # SQLite database (created at runtime)
│
└── venv/                            # Virtual environment (not in git)
```

## Module Organization

### STT Pipelines (`stt_pipelines/`)
All speech-to-text related functionality:
- **uzbek_xlsr_pipeline.py**: Primary STT using XLS-R model (best accuracy for Uzbek)
- **uzbek_whisper_pipeline.py**: Alternative STT using OpenAI Whisper
- **uzbek_hf_pipeline.py**: Generic Hugging Face ASR pipeline
- **uzbek_tts_pipeline.py**: Text-to-speech for interactive teaching

### Face Recognition (`face_recognition/`)
Complete attendance system:
- **face_recognition_db.py**: Database operations (students, attendance, reports)
- **face_enrollment.py**: Enroll students via webcam or images
- **face_attendance.py**: Real-time recognition at entrance camera

### Utils (`utils/`)
Supporting functionality:
- **uzbek_text_postprocessor.py**: Clean and normalize STT output
- **uzbek_accuracy_testing_framework.py**: Measure WER/CER metrics

### Docs (`docs/`)
Comprehensive documentation for all features

### Data (`data/`)
Datasets, reports, and runtime databases

## Import Examples

### Using STT Pipelines
```python
from stt_pipelines.uzbek_xlsr_pipeline import create_uzbek_xlsr_stt
from stt_pipelines.uzbek_whisper_pipeline import create_uzbek_whisper_stt

# Primary model (best accuracy)
stt = create_uzbek_xlsr_stt()
result = stt.transcribe_file("audio.wav")
```

### Using Face Recognition
```python
from face_recognition.face_enrollment import FaceEnrollmentSystem
from face_recognition.face_recognition_db import FaceRecognitionDB
from face_recognition.face_attendance import FaceRecognitionAttendance

# Enroll student
enrollment = FaceEnrollmentSystem()
db = FaceRecognitionDB()
student_id, name, class_name, encoding = enrollment.enroll_student_interactive()
db.add_student(student_id, name, class_name, encoding)

# Run attendance
attendance = FaceRecognitionAttendance()
attendance.run_entrance_camera(camera_id=0)
```

### Using Utils
```python
from utils.uzbek_text_postprocessor import UzbekTextPostProcessor
from utils.uzbek_accuracy_testing_framework import run_xlsr_accuracy_test

# Post-process text
processor = UzbekTextPostProcessor()
clean_text = processor.process(raw_text)

# Test accuracy
run_xlsr_accuracy_test()
```

## Benefits of This Structure

1. **Clear Separation**: Each module type has its own folder
2. **Easy Navigation**: Find files quickly by category
3. **Maintainability**: Changes isolated to specific areas
4. **Scalability**: Easy to add new pipelines or features
5. **Clean Imports**: Explicit package structure
6. **Professional**: Standard Python project layout

## Adding New Modules

### New STT Pipeline
1. Create file in `stt_pipelines/`
2. Add import to `stt_pipelines/__init__.py`
3. Update `main.py` if needed

### New Face Recognition Feature
1. Create file in `face_recognition/`
2. Add import to `face_recognition/__init__.py`
3. Add command to `main.py` if needed

### New Utility
1. Create file in `utils/`
2. Add import to `utils/__init__.py`
