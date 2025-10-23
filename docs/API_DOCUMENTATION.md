# AI Education Backend - API Documentation

## Server Information
- **Base URL**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
- **Version**: 1.0.0

## Authentication

All protected endpoints require JWT authentication. Include the token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "System Administrator",
  "role": "admin",
  "is_active": true,
  "last_login": "2025-10-23T10:30:00Z",
  "created_at": "2025-10-20T08:00:00Z",
  "updated_at": null
}
```

### Register New User (Admin Only)
```http
POST /api/auth/register
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "username": "teacher1",
  "email": "teacher1@example.com",
  "full_name": "John Teacher",
  "password": "secure_password",
  "role": "teacher",
  "is_active": true
}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

---

## Students Management

### List All Students
```http
GET /api/students?skip=0&limit=100&is_active=true
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)
- `is_active` (bool, optional): Filter by active status

**Response:**
```json
[
  {
    "id": 1,
    "student_id": "STU001",
    "name": "Ali Aliyev",
    "email": "ali@example.com",
    "phone": "+998901234567",
    "is_active": true,
    "face_image_path": "/uploads/faces/STU001_face.jpg",
    "created_at": "2025-10-20T09:00:00Z",
    "updated_at": null
  }
]
```

### Get Student by ID
```http
GET /api/students/{student_id}
Authorization: Bearer <token>
```

### Create New Student (Teacher/Admin)
```http
POST /api/students
Authorization: Bearer <token>
Content-Type: application/json

{
  "student_id": "STU002",
  "name": "Vali Valiyev",
  "email": "vali@example.com",
  "phone": "+998901234568",
  "is_active": true
}
```

### Update Student (Teacher/Admin)
```http
PUT /api/students/{student_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Vali Valiyev Updated",
  "email": "vali.updated@example.com"
}
```

### Delete Student (Admin Only)
```http
DELETE /api/students/{student_id}
Authorization: Bearer <admin_token>
```

### Enroll Student Face (Teacher/Admin)
```http
POST /api/students/{student_id}/enroll-face
Authorization: Bearer <token>
Content-Type: multipart/form-data

face_image=@/path/to/face_image.jpg
```

---

## Lessons Management

### List All Lessons
```http
GET /api/lessons?skip=0&limit=100&status_filter=scheduled
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum records to return
- `status_filter` (string, optional): Filter by status (scheduled, in_progress, completed, cancelled)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Python Asoslari",
    "description": "Python dasturlash tilining asoslari",
    "date": "2025-10-24T10:00:00Z",
    "start_time": null,
    "end_time": null,
    "duration_minutes": 90,
    "presentation_path": null,
    "materials_path": null,
    "vector_store_path": null,
    "status": "scheduled",
    "subject": "Programming",
    "notes": null,
    "created_at": "2025-10-23T08:00:00Z",
    "updated_at": null
  }
]
```

### Get Lesson by ID
```http
GET /api/lessons/{lesson_id}
Authorization: Bearer <token>
```

### Create New Lesson (Teacher/Admin)
```http
POST /api/lessons
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Python Web Development",
  "description": "Flask va FastAPI bilan web dasturlash",
  "date": "2025-10-25T10:00:00Z",
  "duration_minutes": 120,
  "subject": "Web Development",
  "notes": "Laptop kerak"
}
```

### Update Lesson (Teacher/Admin)
```http
PUT /api/lessons/{lesson_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Python Web Development - Updated",
  "duration_minutes": 150
}
```

### Delete Lesson (Teacher/Admin)
```http
DELETE /api/lessons/{lesson_id}
Authorization: Bearer <token>
```

### Start Lesson (Teacher/Admin)
```http
POST /api/lessons/{lesson_id}/start
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Python Asoslari",
  "status": "in_progress",
  "start_time": "2025-10-24T10:05:00Z",
  ...
}
```

### End Lesson (Teacher/Admin)
```http
POST /api/lessons/{lesson_id}/end
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Python Asoslari",
  "status": "completed",
  "start_time": "2025-10-24T10:05:00Z",
  "end_time": "2025-10-24T11:35:00Z",
  ...
}
```

### Upload Lesson Materials (Teacher/Admin)
```http
POST /api/lessons/{lesson_id}/upload-materials
Authorization: Bearer <token>
Content-Type: multipart/form-data

materials_file=@/path/to/materials.pdf
```

**Supported formats**: PDF, PPTX, DOCX, TXT

**Response:**
```json
{
  "message": "Materials uploaded successfully",
  "file_path": "/uploads/materials/lesson_1_materials.pdf",
  "lesson_id": 1
}
```

### Upload Lesson Presentation (Teacher/Admin)
```http
POST /api/lessons/{lesson_id}/upload-presentation
Authorization: Bearer <token>
Content-Type: multipart/form-data

presentation_file=@/path/to/presentation.pptx
```

**Supported formats**: PPTX, PDF

---

## Attendance Management

### List Attendance Records
```http
GET /api/attendance?skip=0&limit=100&lesson_id=1&student_id=2
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum records to return
- `lesson_id` (int, optional): Filter by lesson
- `student_id` (int, optional): Filter by student

**Response:**
```json
[
  {
    "id": 1,
    "student_id": 1,
    "lesson_id": 1,
    "timestamp": "2025-10-24T09:55:00Z",
    "recognition_confidence": 0.95,
    "entry_method": "face_recognition",
    "notes": null
  }
]
```

### Get Lesson Attendance
```http
GET /api/attendance/lesson/{lesson_id}
Authorization: Bearer <token>
```

### Get Student Attendance History
```http
GET /api/attendance/student/{student_id}
Authorization: Bearer <token>
```

### Mark Attendance Manually (Teacher/Admin)
```http
POST /api/attendance
Authorization: Bearer <token>
Content-Type: application/json

{
  "student_id": 1,
  "lesson_id": 1,
  "entry_method": "manual",
  "recognition_confidence": null,
  "notes": "Arrived late"
}
```

### Scan Face for Attendance (Teacher/Admin)
```http
POST /api/attendance/scan?lesson_id=1
Authorization: Bearer <token>
Content-Type: multipart/form-data

face_image=@/path/to/student_face.jpg
```

**Note**: Face recognition service integration pending (returns 501 Not Implemented)

### Delete Attendance Record (Teacher/Admin)
```http
DELETE /api/attendance/{attendance_id}
Authorization: Bearer <token>
```

---

## Q&A Sessions

### List Q&A Sessions
```http
GET /api/qa?skip=0&limit=100&lesson_id=1&found_answer=true
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum records to return
- `lesson_id` (int, optional): Filter by lesson
- `found_answer` (bool, optional): Filter by answer status

**Response:**
```json
[
  {
    "id": 1,
    "lesson_id": 1,
    "question_text": "Python qanday dasturlash tili?",
    "question_audio_path": "/uploads/audio/question_1.wav",
    "transcription_confidence": 0.96,
    "answer_text": "Python yuqori darajali, interpretatsiya qilinadigan dasturlash tilidir...",
    "answer_audio_path": "/uploads/audio/answer_1.mp3",
    "found_answer": true,
    "relevance_score": 0.89,
    "source_documents": "[1, 2, 3]",
    "processing_time_ms": 2500,
    "timestamp": "2025-10-24T11:20:00Z"
  }
]
```

### Get Lesson Q&A Sessions
```http
GET /api/qa/lesson/{lesson_id}
Authorization: Bearer <token>
```

### Get Q&A Session by ID
```http
GET /api/qa/{qa_id}
Authorization: Bearer <token>
```

### Create Q&A Session (Text Question)
```http
POST /api/qa
Authorization: Bearer <token>
Content-Type: application/json

{
  "lesson_id": 1,
  "question_text": "FastAPI nima?",
  "transcription_confidence": null,
  "question_audio_path": null
}
```

**Note**: NLP service integration pending (returns placeholder answer)

### Ask Question via Audio
```http
POST /api/qa/ask-audio?lesson_id=1
Authorization: Bearer <token>
Content-Type: multipart/form-data

audio_file=@/path/to/question.wav
```

**Note**: STT + NLP integration pending (returns 501 Not Implemented)

### Process Lesson Materials (Teacher/Admin)
```http
POST /api/qa/process-lesson-materials/{lesson_id}
Authorization: Bearer <token>
```

Creates vector store from uploaded lesson materials for Q&A.

**Note**: Materials processing integration pending (returns 501 Not Implemented)

### Delete Q&A Session (Teacher/Admin)
```http
DELETE /api/qa/{qa_id}
Authorization: Bearer <token>
```

---

## User Roles

### Role Hierarchy
1. **Admin** (Highest)
   - Full access to all endpoints
   - Can create/update/delete users
   - Can manage all resources

2. **Teacher**
   - Can create/update lessons
   - Can mark attendance
   - Can manage students
   - Cannot delete students or manage users

3. **Viewer** (Lowest)
   - Can view all resources
   - Cannot create, update, or delete

### Role-Based Access Examples

| Endpoint | Admin | Teacher | Viewer |
|----------|-------|---------|--------|
| List students | ✅ | ✅ | ✅ |
| Create student | ✅ | ✅ | ❌ |
| Delete student | ✅ | ❌ | ❌ |
| Register user | ✅ | ❌ | ❌ |
| Start lesson | ✅ | ✅ | ❌ |
| View Q&A | ✅ | ✅ | ✅ |

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Student ID already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions. Required role: teacher"
}
```

### 404 Not Found
```json
{
  "detail": "Student with ID 999 not found"
}
```

### 501 Not Implemented
```json
{
  "detail": "Face recognition service integration pending"
}
```

---

## Testing with cURL

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Create Student
```bash
curl -X POST "http://localhost:8000/api/students" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU001",
    "name": "Test Student",
    "email": "test@example.com",
    "is_active": true
  }'
```

### List Lessons
```bash
curl -X GET "http://localhost:8000/api/lessons" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Integration Status

### ✅ Implemented
- Database models and schemas
- JWT authentication
- Role-based access control
- CRUD operations for all resources
- File upload endpoints
- API documentation (Swagger/ReDoc)

### ⏳ Pending Integration
- **Face Recognition Service**: Face encoding generation and recognition
- **STT Service**: Audio transcription (Uzbek XLSR model)
- **TTS Service**: Text-to-speech audio generation (Edge TTS)
- **NLP/QA Service**: Question answering with vector search
- **Materials Processor**: PDF/PPTX/DOCX text extraction and chunking

---

## Next Steps

1. **Integrate AI Services**
   - Create service wrappers in `backend/services/`
   - Connect existing STT, TTS, NLP/QA modules
   - Implement face recognition integration

2. **Complete Endpoints**
   - Implement `/api/attendance/scan` with face recognition
   - Implement `/api/qa/ask-audio` with STT + NLP
   - Implement `/api/qa/process-lesson-materials` with materials processor

3. **Add Real-time Features**
   - WebSocket for live transcription during lessons
   - WebSocket for real-time attendance updates

4. **Testing**
   - Unit tests for all route handlers
   - Integration tests for complete workflows
   - Load testing for concurrent users

---

## Support

For questions or issues:
- Check API documentation: http://localhost:8000/docs
- Review implementation docs: `docs/BACKEND_IMPLEMENTATION.md`
- Check NLP/QA docs: `docs/NLP_QA_SYSTEM_README.md`
