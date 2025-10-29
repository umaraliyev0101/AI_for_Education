# Frontend Quick Reference
## Essential API Calls & WebSocket Messages

---

## 🚀 Quick Start

### 1. Login & Get Token
```javascript
// POST /api/auth/login
const formData = new URLSearchParams();
formData.append('username', 'teacher1');
formData.append('password', 'password');

fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  body: formData
}).then(r => r.json()).then(data => {
  localStorage.setItem('token', data.access_token);
});
```

### 2. Connect to Lesson
```javascript
const token = localStorage.getItem('token');
const ws = new WebSocket(
  `ws://localhost:8000/api/ws/lesson/${lessonId}?token=${token}`
);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log(msg.type, msg);
};
```

---

## 📡 WebSocket Messages

### Send to Server
```javascript
// Start attendance
ws.send(JSON.stringify({ type: 'start_attendance' }));

// Start presentation
ws.send(JSON.stringify({ type: 'start_presentation' }));

// Next slide
ws.send(JSON.stringify({ type: 'next_slide' }));

// Previous slide
ws.send(JSON.stringify({ type: 'previous_slide' }));

// Pause (for question)
ws.send(JSON.stringify({ type: 'pause_presentation' }));

// Ask question
ws.send(JSON.stringify({
  type: 'ask_question',
  question: 'What is X?',
  method: 'text'
}));

// Resume presentation
ws.send(JSON.stringify({ type: 'resume_presentation' }));

// End lesson
ws.send(JSON.stringify({ type: 'end_lesson' }));
```

### Receive from Server
```javascript
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  switch(msg.type) {
    case 'lesson_state':
      // Update UI with lesson state
      break;
    case 'attendance_started':
      // Show attendance mode
      break;
    case 'presentation_started':
      // Display first slide: msg.current_slide
      // Play audio: msg.current_slide.audio_path
      break;
    case 'slide_changed':
      // Display new slide: msg.slide
      break;
    case 'presentation_paused':
      // Pause audio, show question modal
      break;
    case 'presentation_resumed':
      // Resume audio
      break;
    case 'presentation_completed':
      // Switch to Q&A tab
      break;
  }
};
```

---

## 🔑 API Endpoints

### Get Today's Lesson
```javascript
GET /api/lessons/?status=scheduled
Headers: { Authorization: "Bearer TOKEN" }
```

### Get Presentation
```javascript
GET /api/lessons/{lesson_id}/presentation
Headers: { Authorization: "Bearer TOKEN" }

Response:
{
  "lesson_id": 1,
  "total_slides": 10,
  "slides": [
    {
      "slide_number": 1,
      "text": "...",
      "audio_path": "/uploads/audio/presentations/lesson_1_slide_1.mp3",
      "duration_estimate": 12.5
    }
  ]
}
```

### Auto-Scan Attendance
```javascript
POST /api/attendance/auto-scan/{lesson_id}
Headers: { Authorization: "Bearer TOKEN" }

Response:
{
  "recognized_count": 5,
  "students": [
    {
      "id": 1,
      "name": "John Doe",
      "photo_base64": "iVBORw0KGgo...",
      "confidence": 0.95
    }
  ]
}
```

### Ask Text Question
```javascript
POST /api/qa/?generate_audio=true
Headers: { 
  Authorization: "Bearer TOKEN",
  Content-Type: "application/json"
}
Body: {
  "lesson_id": 1,
  "question_text": "What is algebra?"
}

Response:
{
  "question_text": "What is algebra?",
  "answer_text": "Algebra is...",
  "answer_audio_path": "/uploads/audio/qa_1_answer_123.mp3",
  "found_answer": true
}
```

### Ask Audio Question
```javascript
POST /api/qa/ask-audio?lesson_id={lesson_id}
Headers: { Authorization: "Bearer TOKEN" }
Body: FormData with audio file

// Creates transcription + answer with audio
```

---

## 🎨 UI Components Needed

### 1. Attendance View
```
Display grid of students with:
- Photo (from photo_base64)
- Name
- Confidence percentage
```

### 2. Presentation View
```
- Slide content (text)
- Audio player (auto-play from audio_path)
- Previous/Next buttons
- "Ask Question" button
- Progress: "Slide X/Y"
```

### 3. Question Modal
```
- Text input OR
- Audio recorder button
- Submit button
```

### 4. Q&A View
```
- Question history
- Input for new questions
- Display answers with audio playback
```

---

## 🎵 Audio Handling

### Play Slide Audio
```javascript
const audio = new Audio();
audio.src = `http://localhost:8000${slide.audio_path}`;
audio.play();
```

### Record Audio Question
```javascript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const mediaRecorder = new MediaRecorder(stream);
const chunks = [];

mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
mediaRecorder.start();

// Stop recording
mediaRecorder.stop();
const audioBlob = new Blob(chunks, { type: 'audio/wav' });

// Send to backend
const formData = new FormData();
formData.append('audio_file', audioBlob, 'question.wav');
```

---

## 📷 Display Student Photos

```javascript
// Convert base64 to image
<img 
  src={`data:image/jpeg;base64,${student.photo_base64}`}
  alt={student.name}
/>
```

---

## 🔄 Complete Flow

```
1. Teacher logs in
   ↓
2. GET /api/lessons/ (get today's lesson)
   ↓
3. Connect WebSocket to lesson
   ↓
4. POST /api/attendance/auto-scan/{lesson_id}
   Display student photos
   ↓
5. At 8AM or manual: send {type: 'start_presentation'}
   ↓
6. Display slides from presentation data
   Play audio for each slide
   ↓
7. On question button: 
   - Send {type: 'pause_presentation'}
   - Show question modal
   - POST /api/qa/ with question
   - Play answer audio
   - Send {type: 'resume_presentation'}
   ↓
8. When last slide:
   - Receive {type: 'presentation_completed'}
   - Auto-switch to Q&A tab
   ↓
9. Q&A session:
   - Students ask questions
   - Display answers
   ↓
10. Teacher ends: send {type: 'end_lesson'}
```

---

## ⚠️ Important Notes

1. **Audio Autoplay**: User must interact with page first (browser policy)
2. **WebSocket Reconnection**: Implement auto-reconnect on disconnect
3. **Token Expiry**: Refresh token if needed (24 hour expiry)
4. **Base URL**: Change `localhost:8000` to production URL
5. **Camera Permission**: Browser will ask for camera access for attendance

---

## 🐛 Common Issues

**WebSocket won't connect**
- Check token is valid
- Check lesson_id exists
- Check backend is running

**Audio won't play**
- Check audio path exists
- User must click something first (browser policy)
- Check CORS settings

**No students recognized**
- Check camera permissions
- Ensure students are enrolled
- Try manual attendance fallback

---

## 📞 Quick Test

```bash
# Test backend is running
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=teacher1&password=password"

# Test with token
curl http://localhost:8000/api/lessons/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔗 Full Documentation

See `FRONTEND_INTEGRATION_GUIDE.md` for:
- Complete React examples
- TypeScript interfaces
- Error handling
- Testing strategies
- Performance tips

---

## 📱 Minimum Requirements

**Browser Support:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Features Needed:**
- WebSocket support
- Audio playback
- Camera access (for attendance)
- Microphone access (for audio questions)

---

**Backend URL**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs  
**WebSocket**: ws://localhost:8000/api/ws/lesson/{id}?token={token}
