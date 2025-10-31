# 📘 Frontend Integration Guide - CORRECTED

**Complete & Accurate API Reference**

Base URL: `http://localhost:8001`  
Updated: October 30, 2025

---

## 🚨 KEY CORRECTIONS



### ❌ WRONG (Previous Guide)
```json
// Login response - WRONG!
{
  "access_token": "...",
  "token_type": "bearer",
  "user": { "id": 1, "username": "admin" }  // ❌ DOES NOT EXIST!
}
```

### ✅ CORRECT
```json
// Login response - ACTUAL response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
// To get user info, call /api/auth/me AFTER login
```

---

## 🔐 1. Authentication (CORRECTED)

### Login

**Endpoint:** `POST /api/auth/login`

**⚠️ MUST use form-data, NOT JSON!**

**Required Fields:** ONLY `username` and `password` (no client_id, no client_secret)

**Correct Code:**
```javascript
// ✅ CORRECT - Only username and password needed
const formData = new URLSearchParams();
formData.append('username', 'admin');
formData.append('password', 'admin123');

const response = await fetch('http://localhost:8001/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: formData
});

const { access_token, token_type } = await response.json();
localStorage.setItem('access_token', access_token);
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**❌ Common Mistakes:**
```javascript
// WRONG - Using JSON
fetch('/api/auth/login', {
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
// Result: 422 Error

// WRONG - Expecting user in response
const { user } = await response.json();
// Result: undefined
```

---

### Get User Info

**Endpoint:** `GET /api/auth/me`

**Call this AFTER login to get user details**

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8001/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const user = await response.json();
console.log(user);
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
  "last_login": "2025-10-30T10:30:00Z",
  "created_at": "2025-10-30T08:00:00Z",
  "updated_at": null
}
```

---

## Complete Login Flow (React)

```jsx
import React, { useState } from 'react';

function LoginPage() {
  const [user, setUser] = useState(null);

  const handleLogin = async (username, password) => {
    try {
      // Step 1: Login to get token
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const loginResponse = await fetch('http://localhost:8001/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      const { access_token } = await loginResponse.json();
      localStorage.setItem('access_token', access_token);

      // Step 2: Get user info
      const userResponse = await fetch('http://localhost:8001/api/auth/me', {
        headers: { 'Authorization': `Bearer ${access_token}` }
      });

      const userData = await userResponse.json();
      setUser(userData);
      
      console.log('✅ Logged in:', userData.username);
    } catch (error) {
      console.error('❌ Login failed:', error);
    }
  };

  return (
    <div>
      {user ? (
        <div>Welcome, {user.full_name}!</div>
      ) : (
        <button onClick={() => handleLogin('admin', 'admin123')}>
          Login
        </button>
      )}
    </div>
  );
}
```

---

## 🔄 2. WebSocket (CORRECTED)

### Connection

**⚠️ Token goes in QUERY PARAMETER, not header!**

```javascript
// ✅ CORRECT
const token = localStorage.getItem('access_token');
const lessonId = 5;

const ws = new WebSocket(
  `ws://localhost:8001/api/ws/lesson/${lessonId}?token=${token}`
);

ws.onopen = () => console.log('✅ Connected');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};
```

**❌ Wrong:**
```javascript
// This won't work - WebSocket doesn't support headers
new WebSocket('ws://...', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Send Messages

```javascript
// Next slide
ws.send(JSON.stringify({
  type: 'next_slide'
}));

// Ask question
ws.send(JSON.stringify({
  type: 'ask_question',
  question: 'Bu qanday ishlaydi?',
  generate_audio: true
}));

// Pause presentation
ws.send(JSON.stringify({
  type: 'pause_presentation'
}));
```

### Receive Messages

```javascript
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  switch (msg.type) {
    case 'slide_changed':
      console.log('New slide:', msg.slide_number);
      displaySlide(msg.text);
      playAudio(msg.audio_path);
      break;
      
    case 'student_detected':
      console.log('Student:', msg.student.first_name);
      showPhoto(msg.student.photo); // base64 image
      break;
      
    case 'presentation_completed':
      console.log('Presentation done!');
      switchToQAMode();
      break;
  }
};
```

---

## 📚 3. Other Endpoints

### Get All Lessons

```javascript
const response = await fetch('http://localhost:8001/api/lessons/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const lessons = await response.json();
```

### Auto Face Recognition Attendance

```javascript
const lessonId = 5;

const response = await fetch(
  `http://localhost:8001/api/attendance/auto-scan?lesson_id=${lessonId}`,
  {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

const result = await response.json();
// Returns: { students: [...], scanned_count: 3 }
// Each student has: id, name, confidence, photo (base64)
```

### Ask Question

```javascript
const response = await fetch(
  'http://localhost:8001/api/qa/?generate_audio=true',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      lesson_id: 5,
      question_text: 'Kvadrat tenglama qanday yechiladi?'
    })
  }
);

const qa = await response.json();
// Returns: question, answer_text, answer_audio_path, found_answer
```

---

## ⚠️ 4. Common Errors & Solutions

### 422 Unprocessable Entity (Login)
**Cause:** Wrong Content-Type or JSON body

**Fix:**
```javascript
// Use form-data, not JSON!
const formData = new URLSearchParams();
formData.append('username', username);
formData.append('password', password);
// Content-Type: application/x-www-form-urlencoded
```

### 401 Unauthorized
**Cause:** Missing/invalid token

**Fix:**
1. Check: `localStorage.getItem('access_token')`
2. Format: `Bearer {token}` (with space!)
3. Token expires after 24 hours - login again

### WebSocket Won't Connect
**Cause:** Token in wrong place

**Fix:**
```javascript
// Token must be in URL query, not header!
ws://localhost:8001/api/ws/lesson/5?token=YOUR_TOKEN
```

### CORS Error
**Already fixed** - Backend allows all origins in development

---

## 📦 5. TypeScript Interfaces

```typescript
// Login
interface LoginResponse {
  access_token: string;
  token_type: string;
}

// User (from /api/auth/me)
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'teacher' | 'student' | 'viewer';
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string | null;
}

// Student
interface Student {
  id: number;
  first_name: string;
  last_name: string;
  student_id: string;
  class_name: string;
  email: string | null;
  phone_number: string | null;
  photo_path: string | null;
  is_active: boolean;
}

// Lesson
interface Lesson {
  id: number;
  title: string;
  description: string | null;
  class_name: string;
  subject: string;
  teacher_id: number;
  scheduled_time: string;
  duration_minutes: number;
  presentation_path: string | null;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
}

// Presentation Slide (CORRECTED - includes image_path)
interface Slide {
  slide_number: number;
  text: string;
  audio_path: string;
  image_path: string;  // ← NEW: Path to slide PNG image
  duration_estimate: number;
}

// WebSocket Messages
interface SlideChangedMessage {
  type: 'slide_changed';
  slide_number: number;
  text: string;
  audio_path: string;
  duration: number;
}

interface StudentDetectedMessage {
  type: 'student_detected';
  student: {
    id: number;
    first_name: string;
    last_name: string;
    confidence: number;
    photo: string; // base64
  };
}
```

---

## 🎯 6. Complete Workflow

```javascript
// 1. Login
const formData = new URLSearchParams();
formData.append('username', 'admin');
formData.append('password', 'admin123');

const loginRes = await fetch('http://localhost:8001/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: formData
});

const { access_token } = await loginRes.json();

// 2. Get user
const userRes = await fetch('http://localhost:8001/api/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const user = await userRes.json();

// 3. Get lessons
const lessonsRes = await fetch('http://localhost:8001/api/lessons/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const lessons = await lessonsRes.json();

// 4. Connect WebSocket
const ws = new WebSocket(
  `ws://localhost:8001/api/ws/lesson/${lessons[0].id}?token=${access_token}`
);

// 5. Handle messages
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log('Message:', msg.type);
};

// 6. Control lesson
ws.send(JSON.stringify({ type: 'start_attendance' }));
ws.send(JSON.stringify({ type: 'start_presentation' }));
ws.send(JSON.stringify({ type: 'next_slide' }));
```

---

## � 7. Presentation Handling (CORRECTED)

### 🚨 IMPORTANT: Frontend Needs Actual Slide Images!

**❌ WRONG Assumption:**  
"Frontend can display presentations using just text and audio"

**✅ CORRECT Approach:**  
Frontend needs actual slide images (PNG files) to display presentations properly.

### How It Works

1. **Teacher uploads presentation** (PPTX or PDF)
2. **Backend processes it:**
   - Converts each slide/page to PNG image
   - Extracts text from each slide
   - Generates TTS audio for each slide
3. **Frontend receives:**
   - `image_path`: PNG image to display
   - `text`: Extracted text (for transcripts/accessibility)
   - `audio_path`: TTS narration audio

### Upload Presentation

**Endpoint:** `POST /api/lessons/{lesson_id}/presentation`

```javascript
const fileInput = document.querySelector('input[type="file"]');
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch(`http://localhost:8001/api/lessons/${lessonId}/presentation`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
// { message: "Presentation uploaded", filename: "lesson_1_presentation.pptx" }
```

### Process Presentation (Generate Images + Audio)

**Endpoint:** `POST /api/lessons/{lesson_id}/presentation/process`

```javascript
const response = await fetch(`http://localhost:8001/api/lessons/${lessonId}/presentation/process`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const result = await response.json();
// Processing happens in background
// { message: "Processing started", status: "processing" }
```

### Get Presentation Data

**Endpoint:** `GET /api/lessons/{lesson_id}/presentation`

```javascript
const response = await fetch(`http://localhost:8001/api/lessons/${lessonId}/presentation`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
```

**Response:**
```json
{
  "lesson_id": 1,
  "total_slides": 5,
  "slides": [
    {
      "slide_number": 1,
      "text": "O'zbekiston tarixi",
      "audio_path": "uploads/audio/presentations/lesson_1_slide_1.mp3",
      "image_path": "uploads/slides/lesson_1/slide_1.png",
      "duration_estimate": 3.5
    },
    {
      "slide_number": 2,
      "text": "Qadimgi davr...",
      "audio_path": "uploads/audio/presentations/lesson_1_slide_2.mp3",
      "image_path": "uploads/slides/lesson_1/slide_2.png",
      "duration_estimate": 5.2
    }
  ]
}
```

### Display Slide in Frontend

```javascript
function displaySlide(slide) {
  // Display the actual slide image (PRIMARY)
  const imgElement = document.getElementById('slide-image');
  imgElement.src = `http://localhost:8001/${slide.image_path}`;
  
  // Optionally show text (for transcript/accessibility)
  const textElement = document.getElementById('slide-text');
  textElement.textContent = slide.text;
  
  // Play audio narration
  const audio = new Audio(`http://localhost:8001/${slide.audio_path}`);
  audio.play();
}
```

### Pre-Posted Presentations

Presentations can be uploaded days before the lesson:

1. **Upload at any time:**
   ```javascript
   POST /api/lessons/{id}/presentation
   ```

2. **Process when ready:**
   ```javascript
   POST /api/lessons/{id}/presentation/process
   ```

3. **During lesson, slides are already available:**
   ```javascript
   GET /api/lessons/{id}/presentation
   ```

**Note:** Processing (image conversion + TTS) can take 30-60 seconds per slide depending on content.

---

## �📞 8. Resources

- **API Docs:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/health
- **Default Login:** admin / admin123
- **Server Status:** Backend running on port 8001

---

## 📋 9. API Endpoints Quick Reference

### Authentication
- `POST /api/auth/login` - Login (form-data only!)
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Students
- `GET /api/students/` - List students
- `GET /api/students/{id}` - Get student
- `POST /api/students/` - Create student

### Lessons
- `GET /api/lessons/` - List lessons
- `POST /api/lessons/` - Create lesson
- `POST /api/lessons/{id}/presentation` - Upload presentation
- `POST /api/lessons/{id}/presentation/process` - Generate TTS
- `GET /api/lessons/{id}/presentation` - Get presentation data

### Attendance
- `GET /api/attendance/lesson/{lesson_id}` - Get attendance
- `POST /api/attendance/` - Mark attendance
- `POST /api/attendance/auto-scan?lesson_id={id}` - Auto face scan

### Q&A
- `GET /api/qa/lesson/{lesson_id}` - Get Q&A history
- `POST /api/qa/?generate_audio=true` - Ask question
- `POST /api/qa/audio?lesson_id={id}` - Ask with audio

### WebSocket
- `ws://localhost:8001/api/ws/lesson/{lesson_id}?token={token}` - Connect

---

**✅ Status:** Corrected & Complete  
**Version:** 1.0.0  
**Date:** October 30, 2025