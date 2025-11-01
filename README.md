# 🎓 AI Education Platform

> AI-powered education platform with Face Recognition Attendance, Speech-to-Text Q&A, Live Presentations, and Lesson Management for Uzbek schools

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🌟 Features

- 👤 **Face Recognition Attendance** - Automatic attendance using FaceNet
- 🎤 **Speech-to-Text Q&A** - Uzbek speech recognition with XLS-R model  
- 📊 **Live Presentations** - WebSocket-based presentation delivery with TTS
- 📚 **Lesson Management** - Complete CRUD for lessons, students, and materials
- 🔐 **Role-Based Access Control** - Admin, Teacher, and Viewer roles
- 🤖 **AI-Powered Q&A** - RAG-based question answering with LLM

---

##  Quick Start

### Prerequisites
- Python 3.11+
- Webcam (for face recognition)
- 8GB+ RAM recommended

### Local Development

```bash
# Clone repository
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_for_Education

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env and set SECRET_KEY

# Initialize database
python backend/init_db.py

# Start development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

### First Login

Default admin credentials:
- Username: `admin`
- Password: `admin123`

Access:
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs


---

## 📁 Project Structure

```
AI_in_Education/
├── backend/                      # FastAPI Backend
│   ├── main.py                  # Main application entry point
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection
│   ├── auth.py                  # JWT authentication
│   ├── dependencies.py          # Access control dependencies
│   │
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py             # User model (Admin/Teacher/Viewer)
│   │   ├── student.py          # Student model
│   │   ├── lesson.py           # Lesson model
│   │   ├── attendance.py       # Attendance records
│   │   └── qa_session.py       # Q&A sessions
│   │
│   ├── routes/                  # API endpoints
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── students.py         # Student CRUD
│   │   ├── lessons.py          # Lesson management
│   │   ├── attendance.py       # Attendance tracking
│   │   ├── qa.py               # Q&A system
│   │   └── websocket.py        # WebSocket for real-time
│   │
│   ├── schemas/                 # Pydantic schemas
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── lesson.py
│   │   ├── attendance.py
│   │   └── qa_session.py
│   │
│   └── services/                # Business logic
│       ├── lesson_session_service.py
│       └── presentation_service.py
│
├── face_recognition/            # Face recognition system
│   ├── face_enrollment.py      # Student face enrollment
│   ├── face_attendance.py      # Attendance tracking
│   └── face_recognition_db.py  # Face database
│
├── stt_pipelines/               # Speech-to-Text pipelines
│   ├── uzbek_xlsr_pipeline.py  # XLS-R STT (primary, 15% WER)
│   ├── uzbek_whisper_pipeline.py
│   ├── uzbek_hf_pipeline.py
│   └── uzbek_tts_pipeline.py   # Text-to-Speech
│
├── utils/                       # Utilities
│   ├── uzbek_llm_qa_service.py # RAG-based Q&A
│   ├── uzbek_materials_processor.py
│   └── uzbek_text_postprocessor.py
│
├── uploads/                     # User uploads
│   ├── faces/                  # Student face images
│   ├── materials/              # Lesson materials
│   ├── presentations/          # Presentation files
│   ├── slides/                 # Generated slide images
│   └── audio/                  # Audio files
│
├── vector_stores/               # Vector databases for RAG
│
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

---

## 🎯 Features Overview

### 1. **Face Recognition Attendance** 👤

- **Automatic Check-in**: Students recognized via webcam
- **High Accuracy**: 99.3% recognition rate with FaceNet
- **Fast Processing**: ~100ms per frame
- **Multiple Methods**: Auto-scan, manual scan, manual entry
- **Reports**: Daily/weekly/monthly attendance analytics

**Key Files:**
- `face_recognition/face_attendance.py`
- `backend/routes/attendance.py`

### 2. **Speech-to-Text Q&A** 🎤

- **Uzbek Language Support**: Native Uzbek speech recognition
- **High Accuracy**: 15% WER with XLS-R model
- **Multiple Input**: Text or audio questions
- **AI Answers**: RAG-based responses using lesson materials
- **Confidence Scores**: Transcription and answer relevance

**Key Files:**
- `stt_pipelines/uzbek_xlsr_pipeline.py`
- `utils/uzbek_llm_qa_service.py`
- `backend/routes/qa.py`

### 3. **Live Presentations** 📊

- **Real-time Delivery**: WebSocket-based streaming
- **Auto TTS**: Text-to-speech for each slide
- **Slide Navigation**: Next/previous/pause controls
- **Progress Tracking**: Real-time slide progress
- **Format Support**: PPTX and PDF

**Key Files:**
- `backend/services/presentation_service.py`
- `backend/routes/websocket.py`

### 4. **Lesson Management** 📚

- **Complete CRUD**: Create, read, update, delete lessons
- **Material Upload**: PDF, DOCX, TXT for Q&A
- **Presentation Upload**: PPTX, PDF for delivery
- **Status Tracking**: Scheduled → In Progress → Completed
- **Auto-scheduling**: Lessons start/end automatically

**Key Files:**
- `backend/routes/lessons.py`
- `backend/services/lesson_session_service.py`

### 5. **Student Management** 👥

- **Student Records**: Store student information
- **Face Enrollment**: Easy face registration
- **Attendance History**: Track student presence
- **Active/Inactive**: Student status management

**Key Files:**
- `backend/routes/students.py`
- `backend/models/student.py`

---

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints (except login) require JWT token:
```bash
Authorization: Bearer <your_jwt_token>
```

### Key Endpoints

#### **Authentication**
```
POST   /api/auth/login          # Login (form-data: username, password)
GET    /api/auth/me             # Get current user
POST   /api/auth/logout         # Logout
```

#### **Students**
```
GET    /api/students/           # List all students
GET    /api/students/{id}       # Get student by ID
POST   /api/students/           # Create student (Teacher+)
PUT    /api/students/{id}       # Update student (Teacher+)
DELETE /api/students/{id}       # Delete student (Admin only)
POST   /api/students/{id}/enroll-face  # Enroll face (Teacher+)
```

#### **Lessons**
```
GET    /api/lessons/            # List all lessons
GET    /api/lessons/{id}        # Get lesson by ID
POST   /api/lessons/            # Create lesson (Teacher+)
PUT    /api/lessons/{id}        # Update lesson (Teacher+)
DELETE /api/lessons/{id}        # Delete lesson (Teacher+)
POST   /api/lessons/{id}/start  # Start lesson (Teacher+)
POST   /api/lessons/{id}/end    # End lesson (Teacher+)
POST   /api/lessons/{id}/upload-materials  # Upload materials (Teacher+)
POST   /api/lessons/{id}/presentation      # Upload presentation (Teacher+)
POST   /api/lessons/{id}/presentation/process  # Process presentation (Teacher+)
GET    /api/lessons/{id}/presentation      # Get presentation data
```

#### **Attendance**
```
GET    /api/attendance/         # List attendance records
GET    /api/attendance/lesson/{id}   # Get attendance for lesson
GET    /api/attendance/student/{id}  # Get attendance for student
POST   /api/attendance/         # Mark attendance manually (Teacher+)
POST   /api/attendance/scan     # Scan face for attendance (Teacher+)
POST   /api/attendance/auto-scan/{id}  # Auto-scan attendance (Teacher+)
DELETE /api/attendance/{id}     # Delete attendance (Teacher+)
```

#### **Q&A Sessions**
```
GET    /api/qa/                 # List Q&A sessions
GET    /api/qa/lesson/{id}      # Get Q&A for lesson
GET    /api/qa/{id}             # Get Q&A session by ID
POST   /api/qa/                 # Ask question (text)
POST   /api/qa/ask-audio        # Ask question (audio)
POST   /api/qa/process-lesson-materials/{id}  # Process materials (Teacher+)
DELETE /api/qa/{id}             # Delete Q&A (Teacher+)
```

#### **WebSocket**
```
WS     /api/ws/lesson/{id}?token=<jwt>  # Real-time lesson updates
```

### Interactive API Docs
Visit `http://localhost:8000/docs` for Swagger UI documentation.

---

## 🔐 User Roles & Permissions

### Role Hierarchy

```
ADMIN (Level 2)
  ├── Full system access
  ├── Delete students
  └── All teacher permissions
  
TEACHER (Level 1)
  ├── Create/Update/Delete lessons
  ├── Create/Update students
  ├── Mark attendance
  ├── Upload materials & presentations
  └── Process lesson materials
  
VIEWER (Level 0)
  ├── View students, lessons, attendance, Q&A
  └── Ask questions (participate in Q&A)
```

### Permission Matrix

| Operation | Admin | Teacher | Viewer |
|-----------|-------|---------|--------|
| **View Data** | ✅ | ✅ | ✅ |
| **Create Students** | ✅ | ✅ | ❌ |
| **Update Students** | ✅ | ✅ | ❌ |
| **Delete Students** | ✅ | ❌ | ❌ |
| **Manage Lessons** | ✅ | ✅ | ❌ |
| **Mark Attendance** | ✅ | ✅ | ❌ |
| **Ask Questions** | ✅ | ✅ | ✅ |
| **Delete Q&A** | ✅ | ✅ | ❌ |

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and update:

```env
SECRET_KEY=your-secret-key-here-minimum-32-characters
DATABASE_URL=sqlite:///./ai_education.db
ALLOWED_ORIGINS=http://localhost:3000
```

See `.env.example` for all available options.

---

## 💻 Usage Examples

### Python Client

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "teacher", "password": "teacher123"}
)
token = response.json()["access_token"]

# Headers for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Create a student
student_data = {
    "student_id": "ST001",
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": True
}
response = requests.post(
    "http://localhost:8000/api/students/",
    json=student_data,
    headers=headers
)

# Create a lesson
lesson_data = {
    "title": "Algebra Basics",
    "description": "Introduction to algebra",
    "date": "2025-11-01T08:00:00",
    "duration_minutes": 90,
    "subject": "Mathematics"
}
response = requests.post(
    "http://localhost:8000/api/lessons/",
    json=lesson_data,
    headers=headers
)

# Upload presentation
lesson_id = response.json()["id"]
with open("presentation.pptx", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"http://localhost:8000/api/lessons/{lesson_id}/presentation",
        files=files,
        headers=headers
    )

# Start lesson
response = requests.post(
    f"http://localhost:8000/api/lessons/{lesson_id}/start",
    headers=headers
)

# Ask a question
question_data = {
    "lesson_id": lesson_id,
    "question_text": "What is algebra?"
}
response = requests.post(
    "http://localhost:8000/api/qa/",
    json=question_data,
    headers=headers
)
```

### cURL Examples

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -F "username=teacher" \
  -F "password=teacher123"

# Get students
curl -X GET http://localhost:8000/api/students/ \
  -H "Authorization: Bearer <your_token>"

# Create lesson
curl -X POST http://localhost:8000/api/lessons/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Math Class",
    "date": "2025-11-01T08:00:00",
    "duration_minutes": 90
  }'
```

---

## 🧪 Testing

Use the interactive API documentation:
```bash
# Start server
uvicorn backend.main:app --reload

# Open browser
http://localhost:8001/docs
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Reinitialize database
python backend/init_db.py
```

**2. Face Recognition Not Working**
```bash
# Check camera access
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Reinstall face recognition
pip install facenet-pytorch opencv-python
```

**3. STT Model Download Fails**
```bash
# Download manually
from transformers import Wav2Vec2ForCTC
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-xls-r-300m")
```

**4. CUDA Not Available**
```bash
# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**5. Permission Denied (403)**
- Check your user role
- Verify JWT token is valid
- Ensure you're using correct credentials

---

## 📊 Performance

### Model Performance

| Model | Metric | Value | Use Case |
|-------|--------|-------|----------|
| XLS-R | WER | 15.07% | Uzbek STT |
| XLS-R | CER | 3.08% | Uzbek STT |
| Whisper | WER | ~30-35% | Backup STT |
| FaceNet | Accuracy | 99.3% | Face Recognition |
| FLAN-T5 | - | Lightweight | Q&A (Testing) |

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 10 GB
- GPU: Optional

**Recommended:**
- CPU: 8 cores
- RAM: 16 GB
- Storage: 50 GB
- GPU: NVIDIA with 4GB+ VRAM

---

## 🔧 Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn backend.main:app --reload --port 8001
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use type hints
- Write docstrings for functions/classes
- Add tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Umar Aliyev**
- GitHub: [@umaraliyev0101](https://github.com/umaraliyev0101)
- Repository: [AI_for_Education](https://github.com/umaraliyev0101/AI_for_Education)

---

## 🙏 Acknowledgments

- **Meta AI** - XLS-R speech recognition model
- **OpenAI** - Whisper model
- **Google** - FaceNet face recognition
- **Hugging Face** - Transformers library
- **FastAPI** - Modern web framework
- **Uzbek speech data contributors**

---

## 📞 Contact

- GitHub: [@umaraliyev0101](https://github.com/umaraliyev0101)
- Issues: [GitHub Issues](https://github.com/umaraliyev0101/AI_for_Education/issues)

---

**Made with ❤️ for Uzbek Education**
