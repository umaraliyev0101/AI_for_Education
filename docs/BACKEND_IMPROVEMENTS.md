# Backend Improvements Documentation

## Overview
This document describes the major improvements made to the AI Education backend system to support automated lesson management, real-time attendance tracking, presentation delivery, and interactive Q&A sessions.

---

## New Features Implemented

### 1. Automated Lesson Scheduling & Management

**Service**: `backend/services/lesson_session_service.py`

#### Features:
- ✅ **Auto-start lessons at 8:00 AM** - Background scheduler automatically starts lessons at the configured time
- ✅ **Manual lesson start** - Teachers can manually start lessons when they log in
- ✅ **Session state management** - Tracks lesson phases (attendance, presentation, Q&A)
- ✅ **Lifecycle management** - Handles lesson start, pause, resume, and end

#### Key Methods:
```python
# Get the service
from backend.services.lesson_session_service import get_lesson_session_service
lesson_service = get_lesson_session_service()

# Start a lesson manually
await lesson_service.start_lesson_manually(lesson_id, db)

# Get session state
state = lesson_service.get_session_state(lesson_id)

# Pause/Resume lesson (for questions)
await lesson_service.pause_lesson(lesson_id)
await lesson_service.resume_lesson(lesson_id)
```

#### Session State Structure:
```json
{
  "lesson_id": 1,
  "started_at": "2025-10-29T08:00:00",
  "attendance_started": true,
  "presentation_started": false,
  "qa_mode": false,
  "paused": false,
  "current_slide": 0
}
```

---

### 2. Automatic Face Recognition Attendance

**Enhanced Routes**: `backend/routes/attendance.py`

#### Features:
- ✅ **Auto-scan attendance** - Automatically takes attendance using webcam when teacher logs in
- ✅ **Face recognition integration** - Uses existing `face_recognition` module
- ✅ **Student photo delivery** - Returns student photos (base64 encoded) with attendance data
- ✅ **Real-time updates** - Can be integrated with WebSocket for live updates

#### New Endpoints:

**1. Auto-Scan Attendance**
```
POST /api/attendance/auto-scan/{lesson_id}
```
Automatically scans for student faces and marks attendance.

**Response:**
```json
{
  "lesson_id": 1,
  "recognized_count": 5,
  "students": [
    {
      "student_id": "STU001",
      "id": 1,
      "name": "John Doe",
      "photo_base64": "base64_encoded_image_data",
      "confidence": 0.95
    }
  ]
}
```

**2. Manual Face Scan**
```
POST /api/attendance/scan?lesson_id=1
Content-Type: multipart/form-data
```
Upload a face image for attendance marking.

---

### 3. Presentation Processing Service

**Service**: `backend/services/presentation_service.py`

#### Features:
- ✅ **PPTX & PDF support** - Extracts text from presentations
- ✅ **TTS audio generation** - Creates audio narration for each slide using Uzbek TTS
- ✅ **Slide-by-slide data** - Provides structured data for frontend display
- ✅ **Duration estimation** - Estimates audio duration for each slide

#### Workflow:
1. Teacher uploads presentation → `POST /api/lessons/{lesson_id}/upload-presentation`
2. System processes presentation → `POST /api/lessons/{lesson_id}/process-presentation`
3. Frontend retrieves slides → `GET /api/lessons/{lesson_id}/presentation`

#### Presentation Data Structure:
```json
{
  "lesson_id": 1,
  "total_slides": 10,
  "slides": [
    {
      "slide_number": 1,
      "text": "Welcome to today's lesson...",
      "audio_path": "/uploads/audio/presentations/lesson_1_slide_1.mp3",
      "duration_estimate": 12.5
    }
  ],
  "metadata_path": "/uploads/audio/presentations/lesson_1_presentation_metadata.json"
}
```

---

### 4. Real-Time WebSocket Communication

**Routes**: `backend/routes/websocket.py`

#### Features:
- ✅ **Real-time lesson updates** - Live sync of lesson state across all clients
- ✅ **Presentation control** - Next/previous slide, pause/resume
- ✅ **Live Q&A** - Ask questions during presentation
- ✅ **Automatic transitions** - Auto-switch to Q&A after presentation ends

#### WebSocket Endpoint:
```
ws://localhost:8000/api/ws/lesson/{lesson_id}?token=<jwt_token>
```

#### Message Types (Client → Server):
```json
{"type": "start_attendance"}
{"type": "end_attendance"}
{"type": "start_presentation"}
{"type": "next_slide"}
{"type": "previous_slide"}
{"type": "pause_presentation"}
{"type": "resume_presentation"}
{"type": "ask_question", "question": "What is X?", "method": "text"}
{"type": "start_qa"}
{"type": "end_lesson"}
```

#### Message Types (Server → Client):
```json
{"type": "lesson_state", "data": {...}}
{"type": "attendance_started", "timestamp": "..."}
{"type": "presentation_started", "total_slides": 10, "current_slide": {...}}
{"type": "slide_changed", "slide": {...}}
{"type": "presentation_paused"}
{"type": "presentation_resumed"}
{"type": "question_received", "question": "..."}
{"type": "presentation_completed", "message": "Starting Q&A..."}
{"type": "qa_mode_started"}
{"type": "lesson_ended"}
```

---

### 5. Enhanced Q&A with TTS Responses

**Enhanced Routes**: `backend/routes/qa.py`

#### Features:
- ✅ **TTS audio responses** - Generates audio narration for answers
- ✅ **Text and audio questions** - Supports both input methods
- ✅ **Pause/resume integration** - Pauses presentation to answer questions
- ✅ **LLM-powered answers** - Uses Llama-3.1-8B-Instruct-Uz with RAG

#### Enhanced Endpoint:
```
POST /api/qa/?generate_audio=true
```

**Request:**
```json
{
  "lesson_id": 1,
  "question_text": "What is algebra?",
  "transcription_confidence": 0.95
}
```

**Response:**
```json
{
  "id": 1,
  "lesson_id": 1,
  "question_text": "What is algebra?",
  "answer_text": "Algebra is a branch of mathematics...",
  "answer_audio_path": "/uploads/audio/qa_1_answer_12345.mp3",
  "found_answer": true,
  "confidence": 0.92
}
```

---

## Complete Lesson Flow

### Phase 1: Teacher Login & Attendance (Before 8AM or at login)
1. Teacher logs in → System identifies scheduled lesson
2. **Auto-attendance starts** → `POST /api/attendance/auto-scan/{lesson_id}`
3. System scans faces via webcam
4. Recognized students displayed with photos via WebSocket
5. Teacher can manually adjust attendance

### Phase 2: Lesson Start (At 8:00 AM)
1. Scheduler automatically starts lesson
2. WebSocket broadcasts `lesson_state` update
3. System transitions from attendance to presentation

### Phase 3: Presentation Delivery
1. Frontend receives presentation data → `GET /api/lessons/{lesson_id}/presentation`
2. For each slide:
   - Display slide text and content
   - Play TTS audio narration
   - Allow navigation (next/previous)
3. **Question interruption**:
   - Student clicks question button
   - WebSocket sends `pause_presentation`
   - System pauses audio
   - Question processed (text or audio)
   - Answer returned with TTS audio
   - WebSocket sends `resume_presentation`

### Phase 4: Auto-Transition to Q&A
1. Last slide reached
2. System detects completion
3. WebSocket broadcasts `presentation_completed`
4. Frontend automatically switches to Q&A tab
5. Open Q&A session begins

### Phase 5: Q&A Session
1. Students ask questions (text or audio)
2. System processes with LLM
3. Answers returned with TTS audio
4. All Q&A logged in database

### Phase 6: Lesson End
1. Teacher ends lesson → WebSocket `end_lesson`
2. System updates lesson status to COMPLETED
3. All connections notified
4. Session data cleaned up

---

## Installation & Setup

### 1. Install New Dependencies
```bash
pip install python-pptx PyPDF2 edge-tts pygame
```

### 2. Database Migration
The existing database should work, but if you need to add fields:
```python
# QASession model already has answer_audio_path field
# No migration needed for basic functionality
```

### 3. Configuration
Update `backend/config.py` or `.env`:
```env
# Lesson scheduling
LESSON_START_TIME=08:00

# Audio output
AUDIO_DIR=./uploads/audio
TTS_VOICE=uz-UZ-MadinaNeural

# Face recognition
FACE_DB_PATH=./uploads/attendance.db
```

### 4. Start the Server
```bash
cd backend
python -m uvicorn main:app --reload
```

The lesson scheduler will start automatically!

---

## API Documentation

### New Endpoints Added

#### Lessons
- `POST /api/lessons/{lesson_id}/process-presentation` - Process presentation and generate audio
- `GET /api/lessons/{lesson_id}/presentation` - Get processed presentation data

#### Attendance
- `POST /api/attendance/auto-scan/{lesson_id}` - Auto-scan faces for attendance
- `POST /api/attendance/scan` - Manual face scan (improved)

#### WebSocket
- `WS /api/ws/lesson/{lesson_id}` - Real-time lesson management

#### Q&A
- `POST /api/qa/?generate_audio=true` - Create Q&A with audio response

---

## Frontend Integration Guide

### 1. WebSocket Connection
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/ws/lesson/${lessonId}?token=${jwtToken}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'lesson_state':
      updateLessonState(message.data);
      break;
    case 'presentation_started':
      displaySlide(message.current_slide);
      playAudio(message.current_slide.audio_path);
      break;
    case 'slide_changed':
      displaySlide(message.slide);
      playAudio(message.slide.audio_path);
      break;
    case 'presentation_paused':
      pauseAudio();
      break;
    case 'presentation_resumed':
      resumeAudio();
      break;
    case 'presentation_completed':
      switchToQATab();
      break;
  }
};
```

### 2. Attendance Display
```javascript
async function showAttendance() {
  const response = await fetch(`/api/attendance/auto-scan/${lessonId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await response.json();
  
  data.students.forEach(student => {
    displayStudentCard({
      name: student.name,
      photo: `data:image/jpeg;base64,${student.photo_base64}`,
      confidence: student.confidence
    });
  });
}
```

### 3. Presentation Control
```javascript
function nextSlide() {
  ws.send(JSON.stringify({type: 'next_slide'}));
}

function askQuestion() {
  ws.send(JSON.stringify({
    type: 'pause_presentation'
  }));
  
  // Show question input
  const question = getQuestionInput();
  
  ws.send(JSON.stringify({
    type: 'ask_question',
    question: question,
    method: 'text'
  }));
}
```

---

## Testing

### Test Lesson Flow
```bash
# 1. Create a test lesson
POST /api/lessons/
{
  "title": "Test Lesson",
  "date": "2025-10-29T08:00:00",
  "subject": "Math"
}

# 2. Upload presentation
POST /api/lessons/1/upload-presentation
[Upload PPTX file]

# 3. Process presentation
POST /api/lessons/1/process-presentation

# 4. Connect via WebSocket
wscat -c "ws://localhost:8000/api/ws/lesson/1?token=YOUR_TOKEN"

# 5. Send commands
{"type": "start_presentation"}
{"type": "next_slide"}
{"type": "pause_presentation"}
```

---

## Performance Considerations

1. **TTS Generation**: Async processing prevents blocking
2. **Face Recognition**: Processes every 5th frame for performance
3. **WebSocket**: Efficient broadcast to multiple clients
4. **Audio Files**: Cached and reused when possible

---

## Security Notes

1. **WebSocket Auth**: JWT token required in query string
2. **File Uploads**: Validated extensions and sizes
3. **Face Data**: Stored securely, base64 encoded for transport
4. **Role-Based Access**: Teacher role required for management

---

## Troubleshoads

### Issue: Scheduler not starting
**Solution**: Check async event loop, ensure `@app.on_event("startup")` is called

### Issue: TTS not generating audio
**Solution**: Install edge-tts: `pip install edge-tts`

### Issue: Face recognition failing
**Solution**: Check camera permissions and face_recognition database path

### Issue: WebSocket connection refused
**Solution**: Verify JWT token and lesson_id exist

---

## Next Steps for Frontend Team

1. **Connect to WebSocket** - Use the endpoint with JWT token
2. **Display attendance** - Show student cards with photos from auto-scan
3. **Implement presentation player** - Display slides with audio playback
4. **Add question button** - Pause/resume with Q&A modal
5. **Handle auto-transitions** - Listen for `presentation_completed` event
6. **Build Q&A interface** - Text and audio input options

---

## Summary

All 6 requirements have been successfully implemented:

✅ **1. Auto-start lesson at 8AM** - Scheduler service with background task  
✅ **2. Auto-attendance before lesson** - Face recognition with photo delivery  
✅ **3. Display student photos** - Base64 encoded images in response  
✅ **4. Presentation with TTS audio** - Slide-by-slide processing and delivery  
✅ **5. Pausable questions with TTS answers** - WebSocket pause/resume + audio responses  
✅ **6. Auto-transition to Q&A** - Automatic phase switching after presentation  

The backend is now ready for full integration with the frontend!
