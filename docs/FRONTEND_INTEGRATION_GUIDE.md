# Frontend Integration Guide
## AI Education Backend - Real-Time Lesson System

This guide provides everything your frontend needs to integrate with the enhanced backend system.

---

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [WebSocket Connection](#websocket-connection)
4. [Lesson Workflow](#lesson-workflow)
5. [API Endpoints](#api-endpoints)
6. [Code Examples](#code-examples)
7. [Data Structures](#data-structures)
8. [Error Handling](#error-handling)

---

## Overview

### Backend URL
```
Development: http://localhost:8000
Production: [Your production URL]
```

### Key Features
✅ Real-time lesson updates via WebSocket  
✅ Automatic attendance with face recognition  
✅ Presentation with auto-generated audio  
✅ Live Q&A during presentations  
✅ Auto-start lessons at 8AM  
✅ Automatic transition to Q&A after presentation  

---

## Authentication

### 1. Login
```javascript
const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  });
  
  const data = await response.json();
  // Store token for later use
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
};

// Example response:
// {
//   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
//   "token_type": "bearer",
//   "user": {
//     "id": 1,
//     "username": "teacher1",
//     "full_name": "John Doe",
//     "role": "teacher"
//   }
// }
```

### 2. Use Token for API Requests
```javascript
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('token')}`,
  'Content-Type': 'application/json'
};
```

---

## WebSocket Connection

### 1. Connect to Lesson
```javascript
const connectToLesson = (lessonId) => {
  const token = localStorage.getItem('token');
  const ws = new WebSocket(
    `ws://localhost:8000/api/ws/lesson/${lessonId}?token=${token}`
  );
  
  ws.onopen = () => {
    console.log('✅ Connected to lesson', lessonId);
  };
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    handleMessage(message);
  };
  
  ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('🔌 Disconnected from lesson');
  };
  
  return ws;
};
```

### 2. Handle Incoming Messages
```javascript
const handleMessage = (message) => {
  switch (message.type) {
    case 'lesson_state':
      updateLessonUI(message.data);
      break;
      
    case 'attendance_started':
      showAttendanceMode();
      break;
      
    case 'attendance_update':
      displayStudent(message.student);
      break;
      
    case 'presentation_started':
      startPresentation(message.current_slide, message.total_slides);
      break;
      
    case 'slide_changed':
      displaySlide(message.slide);
      playAudio(message.slide.audio_path);
      break;
      
    case 'presentation_paused':
      pauseAudio();
      showQuestionModal();
      break;
      
    case 'presentation_resumed':
      hideQuestionModal();
      resumeAudio();
      break;
      
    case 'presentation_completed':
      showMessage(message.message);
      switchToQATab();
      break;
      
    case 'qa_mode_started':
      enableQAInterface();
      break;
      
    case 'lesson_ended':
      closeLesson();
      break;
      
    case 'error':
      showError(message.message);
      break;
  }
};
```

### 3. Send Messages to Backend
```javascript
// Start attendance
ws.send(JSON.stringify({ type: 'start_attendance' }));

// Start presentation
ws.send(JSON.stringify({ type: 'start_presentation' }));

// Navigate slides
ws.send(JSON.stringify({ type: 'next_slide' }));
ws.send(JSON.stringify({ type: 'previous_slide' }));

// Pause for question
ws.send(JSON.stringify({ type: 'pause_presentation' }));

// Ask question
ws.send(JSON.stringify({
  type: 'ask_question',
  question: 'What is algebra?',
  method: 'text' // or 'audio'
}));

// Resume presentation
ws.send(JSON.stringify({ type: 'resume_presentation' }));

// Start Q&A mode
ws.send(JSON.stringify({ type: 'start_qa' }));

// End lesson
ws.send(JSON.stringify({ type: 'end_lesson' }));
```

---

## Lesson Workflow

### Complete User Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. TEACHER LOGIN                                            │
│    - Login as teacher                                        │
│    - System shows today's scheduled lesson                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. ATTENDANCE PHASE (Auto-start or manual)                  │
│    - Click "Start Attendance" button                         │
│    - System opens camera and scans faces                     │
│    - Display each recognized student with photo              │
│    - Teacher can manually adjust attendance                  │
│    - Click "End Attendance" when done                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. LESSON AUTO-START (8:00 AM)                              │
│    - At 8AM, lesson automatically starts                     │
│    - OR teacher can manually start lesson                    │
│    - System prepares presentation                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. PRESENTATION PHASE                                        │
│    - Display slide content (text/images)                     │
│    - Play audio narration automatically                      │
│    - Show next/previous buttons                              │
│    - Show "Ask Question" button                              │
│                                                               │
│    IF QUESTION BUTTON CLICKED:                               │
│      → Pause audio playback                                  │
│      → Show question modal (text or audio input)             │
│      → Send question to backend                              │
│      → Play answer audio                                     │
│      → Resume presentation                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. AUTO-TRANSITION TO Q&A                                   │
│    - Last slide reached                                      │
│    - Automatically switch to Q&A tab                         │
│    - Show "Presentation Complete" message                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Q&A SESSION                                              │
│    - Students ask questions (text or audio)                  │
│    - System shows answers with audio                         │
│    - All Q&A saved to database                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. END LESSON                                               │
│    - Teacher clicks "End Lesson"                             │
│    - System updates lesson status                            │
│    - Close WebSocket connection                              │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Lessons

#### Get Today's Lesson
```javascript
GET /api/lessons/?status=scheduled

const getTodaysLesson = async () => {
  const response = await fetch('http://localhost:8000/api/lessons/?status=scheduled', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};

// Response: Array of lessons
// [
//   {
//     "id": 1,
//     "title": "Algebra Basics",
//     "date": "2025-10-29T08:00:00",
//     "status": "scheduled",
//     "subject": "Mathematics"
//   }
// ]
```

#### Get Presentation Data
```javascript
GET /api/lessons/{lesson_id}/presentation

const getPresentation = async (lessonId) => {
  const response = await fetch(
    `http://localhost:8000/api/lessons/${lessonId}/presentation`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return await response.json();
};

// Response:
// {
//   "lesson_id": 1,
//   "total_slides": 10,
//   "slides": [
//     {
//       "slide_number": 1,
//       "text": "Welcome to Algebra...",
//       "audio_path": "/uploads/audio/presentations/lesson_1_slide_1.mp3",
//       "duration_estimate": 12.5
//     }
//   ]
// }
```

#### Upload Presentation (Teacher Only)
```javascript
POST /api/lessons/{lesson_id}/upload-presentation

const uploadPresentation = async (lessonId, file) => {
  const formData = new FormData();
  formData.append('presentation_file', file);
  
  const response = await fetch(
    `http://localhost:8000/api/lessons/${lessonId}/upload-presentation`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );
  return await response.json();
};
```

#### Process Presentation (Teacher Only)
```javascript
POST /api/lessons/{lesson_id}/process-presentation

const processPresentation = async (lessonId) => {
  const response = await fetch(
    `http://localhost:8000/api/lessons/${lessonId}/process-presentation`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return await response.json();
};

// This will:
// 1. Extract text from PPTX/PDF
// 2. Generate TTS audio for each slide
// 3. Return structured data
```

### Attendance

#### Auto-Scan Attendance
```javascript
POST /api/attendance/auto-scan/{lesson_id}

const autoScanAttendance = async (lessonId) => {
  const response = await fetch(
    `http://localhost:8000/api/attendance/auto-scan/${lessonId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
};

// Response:
// {
//   "lesson_id": 1,
//   "recognized_count": 5,
//   "students": [
//     {
//       "student_id": "STU001",
//       "id": 1,
//       "name": "John Doe",
//       "photo_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
//       "confidence": 0.95
//     }
//   ]
// }
```

#### Get Lesson Attendance
```javascript
GET /api/attendance/lesson/{lesson_id}

const getLessonAttendance = async (lessonId) => {
  const response = await fetch(
    `http://localhost:8000/api/attendance/lesson/${lessonId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return await response.json();
};
```

#### Manual Attendance Mark
```javascript
POST /api/attendance/

const markAttendance = async (lessonId, studentId) => {
  const response = await fetch('http://localhost:8000/api/attendance/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      lesson_id: lessonId,
      student_id: studentId,
      entry_method: 'manual'
    })
  });
  return await response.json();
};
```

### Q&A

#### Ask Question (Text)
```javascript
POST /api/qa/?generate_audio=true

const askQuestion = async (lessonId, questionText) => {
  const response = await fetch(
    'http://localhost:8000/api/qa/?generate_audio=true',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        lesson_id: lessonId,
        question_text: questionText
      })
    }
  );
  return await response.json();
};

// Response:
// {
//   "id": 1,
//   "lesson_id": 1,
//   "question_text": "What is algebra?",
//   "answer_text": "Algebra is a branch of mathematics...",
//   "answer_audio_path": "/uploads/audio/qa_1_answer_12345.mp3",
//   "found_answer": true,
//   "timestamp": "2025-10-29T08:15:00"
// }
```

#### Ask Question (Audio)
```javascript
POST /api/qa/ask-audio?lesson_id={lesson_id}

const askAudioQuestion = async (lessonId, audioBlob) => {
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'question.wav');
  
  const response = await fetch(
    `http://localhost:8000/api/qa/ask-audio?lesson_id=${lessonId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );
  return await response.json();
};

// Response includes transcribed question + answer with audio
```

#### Get Q&A History
```javascript
GET /api/qa/lesson/{lesson_id}

const getQAHistory = async (lessonId) => {
  const response = await fetch(
    `http://localhost:8000/api/qa/lesson/${lessonId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return await response.json();
};
```

---

## Code Examples

### Complete React Component Example

```jsx
import React, { useState, useEffect, useRef } from 'react';

const LessonView = ({ lessonId, token }) => {
  const [lessonState, setLessonState] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [students, setStudents] = useState([]);
  const [qaMode, setQAMode] = useState(false);
  
  const wsRef = useRef(null);
  const audioRef = useRef(null);
  
  // Connect to WebSocket
  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/api/ws/lesson/${lessonId}?token=${token}`
    );
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };
    
    wsRef.current = ws;
    
    return () => ws.close();
  }, [lessonId, token]);
  
  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'lesson_state':
        setLessonState(message.data);
        break;
        
      case 'presentation_started':
        setCurrentSlide(message.current_slide);
        playSlideAudio(message.current_slide.audio_path);
        break;
        
      case 'slide_changed':
        setCurrentSlide(message.slide);
        playSlideAudio(message.slide.audio_path);
        break;
        
      case 'presentation_paused':
        pauseAudio();
        break;
        
      case 'presentation_resumed':
        resumeAudio();
        break;
        
      case 'presentation_completed':
        setQAMode(true);
        break;
    }
  };
  
  const playSlideAudio = (audioPath) => {
    if (audioRef.current) {
      audioRef.current.src = `http://localhost:8000${audioPath}`;
      audioRef.current.play();
      setIsPlaying(true);
    }
  };
  
  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };
  
  const resumeAudio = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };
  
  const sendMessage = (message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };
  
  const handleNextSlide = () => {
    sendMessage({ type: 'next_slide' });
  };
  
  const handlePreviousSlide = () => {
    sendMessage({ type: 'previous_slide' });
  };
  
  const handleAskQuestion = () => {
    sendMessage({ type: 'pause_presentation' });
    // Show question modal
  };
  
  const submitQuestion = (question) => {
    sendMessage({
      type: 'ask_question',
      question: question,
      method: 'text'
    });
    // After answer is received, resume
    sendMessage({ type: 'resume_presentation' });
  };
  
  // Auto-scan attendance when component mounts
  useEffect(() => {
    const scanAttendance = async () => {
      const response = await fetch(
        `http://localhost:8000/api/attendance/auto-scan/${lessonId}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const data = await response.json();
      setStudents(data.students);
    };
    
    scanAttendance();
  }, [lessonId, token]);
  
  return (
    <div className="lesson-view">
      <audio ref={audioRef} />
      
      {/* Attendance Display */}
      <div className="attendance-section">
        <h2>Attendance</h2>
        <div className="student-grid">
          {students.map(student => (
            <div key={student.id} className="student-card">
              <img 
                src={`data:image/jpeg;base64,${student.photo_base64}`}
                alt={student.name}
              />
              <p>{student.name}</p>
              <span>{(student.confidence * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Presentation Display */}
      {!qaMode && currentSlide && (
        <div className="presentation-section">
          <h2>Slide {currentSlide.slide_number}</h2>
          <div className="slide-content">
            <p>{currentSlide.text}</p>
          </div>
          
          <div className="controls">
            <button onClick={handlePreviousSlide}>← Previous</button>
            <button onClick={handleAskQuestion}>❓ Ask Question</button>
            <button onClick={handleNextSlide}>Next →</button>
          </div>
          
          <div className="audio-status">
            {isPlaying ? '🔊 Playing...' : '⏸️ Paused'}
          </div>
        </div>
      )}
      
      {/* Q&A Display */}
      {qaMode && (
        <div className="qa-section">
          <h2>Q&A Session</h2>
          <input 
            type="text" 
            placeholder="Ask your question..."
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                submitQuestion(e.target.value);
                e.target.value = '';
              }
            }}
          />
        </div>
      )}
    </div>
  );
};

export default LessonView;
```

### Audio Recording Example (for Audio Questions)

```javascript
class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
  }
  
  async startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(stream);
    
    this.mediaRecorder.ondataavailable = (event) => {
      this.audioChunks.push(event.data);
    };
    
    this.mediaRecorder.start();
    console.log('🎤 Recording started');
  }
  
  stopRecording() {
    return new Promise((resolve) => {
      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        this.audioChunks = [];
        console.log('⏹️ Recording stopped');
        resolve(audioBlob);
      };
      
      this.mediaRecorder.stop();
      this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
    });
  }
}

// Usage:
const recorder = new AudioRecorder();

// Start recording
await recorder.startRecording();

// Stop recording after user finishes
const audioBlob = await recorder.stopRecording();

// Send to backend
await askAudioQuestion(lessonId, audioBlob);
```

---

## Data Structures

### Lesson Object
```typescript
interface Lesson {
  id: number;
  title: string;
  description?: string;
  date: string; // ISO 8601 format
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  presentation_path?: string;
  materials_path?: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  subject?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}
```

### Student Attendance Object
```typescript
interface StudentAttendance {
  student_id: string;
  id: number;
  name: string;
  photo_base64: string; // Base64 encoded image
  confidence: number; // 0.0 to 1.0
}
```

### Slide Object
```typescript
interface Slide {
  slide_number: number;
  text: string;
  audio_path: string;
  duration_estimate: number; // seconds
}
```

### Presentation Data
```typescript
interface PresentationData {
  lesson_id: number;
  total_slides: number;
  slides: Slide[];
  metadata_path?: string;
}
```

### Q&A Session Object
```typescript
interface QASession {
  id: number;
  lesson_id: number;
  question_text: string;
  question_audio_path?: string;
  transcription_confidence?: number;
  answer_text?: string;
  answer_audio_path?: string;
  found_answer: boolean;
  timestamp: string;
}
```

### WebSocket Message Types
```typescript
// From Server to Client
type ServerMessage = 
  | { type: 'lesson_state'; data: any }
  | { type: 'attendance_started'; timestamp: string }
  | { type: 'attendance_ended'; timestamp: string }
  | { type: 'presentation_started'; total_slides: number; current_slide: Slide }
  | { type: 'slide_changed'; slide: Slide; timestamp: string }
  | { type: 'presentation_paused'; timestamp: string }
  | { type: 'presentation_resumed'; timestamp: string }
  | { type: 'question_received'; question: string; timestamp: string }
  | { type: 'presentation_completed'; message: string; timestamp: string }
  | { type: 'qa_mode_started'; timestamp: string }
  | { type: 'lesson_ended'; timestamp: string }
  | { type: 'error'; message: string };

// From Client to Server
type ClientMessage =
  | { type: 'start_attendance' }
  | { type: 'end_attendance' }
  | { type: 'start_presentation' }
  | { type: 'next_slide' }
  | { type: 'previous_slide' }
  | { type: 'pause_presentation' }
  | { type: 'resume_presentation' }
  | { type: 'ask_question'; question: string; method: 'text' | 'audio' }
  | { type: 'start_qa' }
  | { type: 'end_lesson' };
```

---

## Error Handling

### HTTP Errors
```javascript
const fetchWithErrorHandling = async (url, options) => {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    // Show user-friendly message
    showNotification('error', error.message);
    throw error;
  }
};
```

### WebSocket Errors
```javascript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  showNotification('error', 'Connection lost. Reconnecting...');
  // Attempt reconnection
  setTimeout(() => connectToLesson(lessonId), 3000);
};

ws.onclose = (event) => {
  if (event.code !== 1000) {
    // Abnormal closure
    showNotification('warning', 'Disconnected from lesson');
  }
};
```

### Common Error Codes
```javascript
const ERROR_CODES = {
  401: 'Unauthorized - Please login again',
  403: 'Forbidden - Insufficient permissions',
  404: 'Not found',
  500: 'Server error - Please try again',
  4004: 'Lesson not found'
};
```

---

## UI/UX Recommendations

### 1. Attendance Display
```
┌─────────────────────────────────────────┐
│  ✅ Attendance (5/30)                   │
├─────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │ [📸] │  │ [📸] │  │ [📸] │          │
│  │ John │  │ Mary │  │ Alex │          │
│  │ 95%  │  │ 89%  │  │ 92%  │          │
│  └──────┘  └──────┘  └──────┘          │
└─────────────────────────────────────────┘
```

### 2. Presentation View
```
┌─────────────────────────────────────────┐
│  Slide 3/10                              │
├─────────────────────────────────────────┤
│                                          │
│  [Slide Content Here]                    │
│  • Point 1                               │
│  • Point 2                               │
│  • Point 3                               │
│                                          │
├─────────────────────────────────────────┤
│  [◀ Previous]  [❓ Question]  [Next ▶]  │
│  🔊 Audio: 00:12 / 01:30                │
└─────────────────────────────────────────┘
```

### 3. Question Modal
```
┌─────────────────────────────────────────┐
│  ❓ Ask a Question                      │
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐   │
│  │ Type your question...            │   │
│  └──────────────────────────────────┘   │
│                                          │
│  OR                                      │
│                                          │
│  [🎤 Record Audio]                      │
│                                          │
│  [Cancel]          [Submit]              │
└─────────────────────────────────────────┘
```

---

## Testing

### Test WebSocket Connection
```javascript
// test-websocket.html
<!DOCTYPE html>
<html>
<head>
  <title>WebSocket Test</title>
</head>
<body>
  <h1>WebSocket Connection Test</h1>
  <div id="status">Connecting...</div>
  <div id="messages"></div>
  
  <script>
    const token = prompt('Enter your JWT token:');
    const lessonId = prompt('Enter lesson ID:');
    
    const ws = new WebSocket(
      `ws://localhost:8000/api/ws/lesson/${lessonId}?token=${token}`
    );
    
    ws.onopen = () => {
      document.getElementById('status').textContent = '✅ Connected';
    };
    
    ws.onmessage = (event) => {
      const div = document.createElement('div');
      div.textContent = event.data;
      document.getElementById('messages').appendChild(div);
    };
    
    ws.onerror = (error) => {
      document.getElementById('status').textContent = '❌ Error';
      console.error(error);
    };
  </script>
</body>
</html>
```

### Test API Endpoints
```bash
# Install httpie or use curl
pip install httpie

# Login
http POST http://localhost:8000/api/auth/login \
  username=teacher1 \
  password=password123 \
  --form

# Get lessons
http GET http://localhost:8000/api/lessons/ \
  Authorization:"Bearer YOUR_TOKEN"

# Get presentation
http GET http://localhost:8000/api/lessons/1/presentation \
  Authorization:"Bearer YOUR_TOKEN"
```

---

## Performance Tips

### 1. Audio Preloading
```javascript
// Preload next slide audio
const preloadNextSlide = (nextSlideNumber) => {
  const audio = new Audio();
  audio.src = `/uploads/audio/presentations/lesson_${lessonId}_slide_${nextSlideNumber}.mp3`;
  audio.preload = 'auto';
};
```

### 2. Image Optimization
```javascript
// Compress base64 images before display
const displayCompressedImage = (base64) => {
  const img = new Image();
  img.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 200; // thumbnail size
    canvas.height = 200;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, 200, 200);
    // Use canvas.toDataURL() for display
  };
  img.src = `data:image/jpeg;base64,${base64}`;
};
```

### 3. WebSocket Reconnection
```javascript
class ReconnectingWebSocket {
  constructor(url) {
    this.url = url;
    this.reconnectInterval = 3000;
    this.connect();
  }
  
  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onclose = () => {
      console.log('Reconnecting...');
      setTimeout(() => this.connect(), this.reconnectInterval);
    };
  }
  
  send(data) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data);
    }
  }
}
```

---

## Security Considerations

### 1. Token Storage
```javascript
// DON'T store in localStorage in production
// Use httpOnly cookies or secure session storage

// For development:
localStorage.setItem('token', token);

// For production:
// Let backend set httpOnly cookie
```

### 2. Input Sanitization
```javascript
const sanitizeInput = (input) => {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};
```

### 3. CORS Configuration
Backend is configured to allow:
```javascript
// In production, update backend config to:
CORS_ORIGINS = ["https://yourdomain.com"]
```

---

## Troubleshooting

### WebSocket won't connect
```
✅ Check token is valid
✅ Check lesson ID exists
✅ Check backend is running
✅ Check CORS settings
✅ Try http:// instead of https:// for local dev
```

### Audio won't play
```
✅ Check browser autoplay policy
✅ Check audio path is correct
✅ Check file exists on server
✅ User must interact with page first (browser policy)
```

### Face recognition not working
```
✅ Check camera permissions
✅ Check students are enrolled in system
✅ Check lighting conditions
✅ Try manual attendance as fallback
```

---

## Support & Resources

### Documentation
- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **Backend Guide**: `BACKEND_IMPROVEMENTS.md`
- **Installation**: `INSTALL_BACKEND_IMPROVEMENTS.md`

### Contact
- Backend Developer: [Your contact]
- Issues: GitHub Issues

### Quick Start Checklist
- [ ] Backend server running on port 8000
- [ ] JWT token obtained from login
- [ ] WebSocket connection established
- [ ] First lesson created and scheduled
- [ ] Presentation uploaded and processed
- [ ] Students enrolled for face recognition
- [ ] Frontend can display attendance
- [ ] Frontend can show presentation
- [ ] Frontend can handle Q&A

---

## Summary

You now have everything needed to integrate with the backend:

✅ Authentication flow  
✅ WebSocket real-time communication  
✅ All API endpoints documented  
✅ Complete code examples  
✅ Data structure definitions  
✅ Error handling patterns  
✅ UI/UX recommendations  
✅ Testing strategies  

**Need Help?** Check the Swagger docs at http://localhost:8000/docs or refer to the backend improvements documentation.

Happy coding! 🚀
