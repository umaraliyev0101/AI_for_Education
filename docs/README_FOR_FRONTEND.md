# 👋 Hey Frontend Friend!

Welcome to the AI Education System integration docs! Here's everything you need to build the frontend.

---

## 📚 Documentation Files

I've created **3 comprehensive guides** for you:

### 1. **FRONTEND_INTEGRATION_GUIDE.md** 📖
**The Complete Technical Guide**
- Full API documentation
- WebSocket implementation details
- Complete React component examples
- TypeScript interfaces
- Error handling patterns
- Testing strategies
- Performance tips

👉 **Use this when**: Building features, implementing code, debugging

---

### 2. **FRONTEND_QUICK_REFERENCE.md** ⚡
**Quick Copy-Paste Reference**
- Essential API calls
- WebSocket message formats
- Code snippets ready to use
- Common issues & solutions
- Quick testing commands

👉 **Use this when**: You need code fast, checking syntax, quick lookup

---

### 3. **FRONTEND_VISUAL_GUIDE.md** 🎨
**UI/UX Design Reference**
- Complete screen layouts
- Visual mockups (ASCII art)
- Color schemes
- Component states
- Responsive breakpoints
- Accessibility guidelines

👉 **Use this when**: Designing UI, planning layouts, styling components

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Test Backend
```bash
# Check backend is running
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Step 2: Get JWT Token
```javascript
const formData = new URLSearchParams();
formData.append('username', 'teacher1');
formData.append('password', 'password');

const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  body: formData
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);
```

### Step 3: Connect WebSocket
```javascript
const ws = new WebSocket(
  `ws://localhost:8000/api/ws/lesson/1?token=${access_token}`
);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('📨', message.type, message);
};
```

### Step 4: Test API
```javascript
// Get today's lessons
fetch('http://localhost:8000/api/lessons/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
}).then(r => r.json()).then(console.log);
```

That's it! You're connected! 🎉

---

## 🎯 What You Need to Build

### 6 Main Views:

1. **Login Screen** 🔐
   - Username/password form
   - Store JWT token

2. **Dashboard** 🏠
   - Show today's lesson
   - Quick stats
   - Start attendance button

3. **Attendance View** 📸
   - Display student photos (auto-scan)
   - Grid layout
   - Manual adjustments

4. **Presentation View** 📊
   - Show slide content
   - Play audio narration
   - Next/Previous buttons
   - "Ask Question" button

5. **Question Modal** ❓
   - Text input OR audio recording
   - Show answer with audio
   - Resume button

6. **Q&A Tab** 💬
   - Question history
   - New question input
   - Answer display with audio

---

## 📡 Key Features

### Real-Time Updates (WebSocket)
The backend sends you updates automatically:
- Lesson starts at 8AM → You receive notification
- New student recognized → You receive photo
- Presentation advances → You receive new slide
- Question answered → You receive answer
- Presentation ends → Auto-switch to Q&A tab

### Automatic Attendance
When teacher logs in:
1. Call `/api/attendance/auto-scan/{lesson_id}`
2. Backend opens camera, scans faces
3. You receive array of students with photos (base64)
4. Display them in a grid

### Presentation with Audio
1. Get presentation: `/api/lessons/{id}/presentation`
2. Display slide text
3. Play audio from `audio_path`
4. On "Next" → WebSocket: `{type: 'next_slide'}`
5. Receive new slide data

### Questions During Presentation
1. User clicks "Ask Question"
2. Send WebSocket: `{type: 'pause_presentation'}`
3. Audio pauses automatically
4. Show question modal
5. Submit question to `/api/qa/`
6. Play answer audio
7. Send: `{type: 'resume_presentation'}`

---

## 🎨 Design Tips

### Colors
```css
Primary:   #1976D2  (Blue)
Success:   #4CAF50  (Green)
Warning:   #FF9800  (Orange)
Error:     #F44336  (Red)
```

### Student Card
```
┌─────────┐
│  📸     │
│ [PHOTO] │
│ John    │
│ 95% ✓   │
└─────────┘
```

### Presentation Layout
```
+------------------------+
|   Slide Content        |
|   • Point 1            |
|   • Point 2            |
+------------------------+
| 🔊 Audio: ━━━━●────── |
+------------------------+
| [◀ Prev] [❓] [Next ▶]|
+------------------------+
```

---

## 🔑 Important Endpoints

```javascript
// Login
POST /api/auth/login

// Get lessons
GET /api/lessons/?status=scheduled

// Get presentation
GET /api/lessons/{id}/presentation

// Auto-scan attendance
POST /api/attendance/auto-scan/{lesson_id}

// Ask question
POST /api/qa/?generate_audio=true

// WebSocket
ws://localhost:8000/api/ws/lesson/{id}?token={token}
```

---

## 🎯 User Flow

```
Login
  ↓
Dashboard (see today's lesson)
  ↓
Start Attendance → Camera scans faces → Display students
  ↓
Lesson auto-starts at 8AM (or manual)
  ↓
Presentation → Display slides + play audio
  ↓
[Optional] Question → Pause → Answer → Resume
  ↓
Last slide → Auto-switch to Q&A tab
  ↓
Q&A Session → Open questions & answers
  ↓
End Lesson
```

---

## 🐛 Common Issues

### WebSocket won't connect
```javascript
// Check:
1. Backend running on port 8000?
2. Token valid?
3. Lesson ID exists?

// Debug:
console.log('Token:', token);
console.log('Lesson ID:', lessonId);
```

### Audio won't play
```javascript
// Browser autoplay policy requires user interaction first
// Solution: Add play button or require click before audio
audio.play().catch(err => {
  console.log('Autoplay blocked:', err);
  // Show play button
});
```

### No students recognized
```javascript
// Fallback: Show manual attendance form
// Or: Try re-scanning
```

---

## 📱 Browser Support

**Required:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Features needed:**
- WebSocket
- Audio playback
- Camera access (for attendance)
- Microphone (for audio questions)

---

## 🎁 Bonus Features

If you have time:
- [ ] Dark mode
- [ ] Keyboard shortcuts
- [ ] Offline indicator
- [ ] Export Q&A as PDF
- [ ] Presentation fullscreen mode
- [ ] Student search/filter
- [ ] Lesson history/statistics

---

## 🤝 Need Help?

1. **Check API docs**: http://localhost:8000/docs
2. **Read the guides**: 
   - Technical: `FRONTEND_INTEGRATION_GUIDE.md`
   - Quick ref: `FRONTEND_QUICK_REFERENCE.md`
   - Design: `FRONTEND_VISUAL_GUIDE.md`
3. **Test endpoints**: Use Postman or curl
4. **Check console**: Look for WebSocket messages
5. **Ask backend dev**: If something's not working

---

## ✅ Checklist

Before you start:
- [ ] Backend running on localhost:8000
- [ ] Can login and get JWT token
- [ ] Can connect to WebSocket
- [ ] Test lesson exists in database
- [ ] Students enrolled for face recognition
- [ ] Presentation uploaded and processed

While building:
- [ ] Login form works
- [ ] Dashboard shows lessons
- [ ] Attendance grid displays photos
- [ ] Presentation displays slides
- [ ] Audio plays automatically
- [ ] Question modal works
- [ ] Q&A tab functional
- [ ] WebSocket reconnects on disconnect
- [ ] Error messages shown to user

---

## 🚀 Development Tips

### Use React DevTools
```javascript
// Add this to see WebSocket messages
useEffect(() => {
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log('📨 WS:', msg.type, msg);
  };
}, []);
```

### Mock Data for Development
```javascript
// If backend not ready, use mock data
const mockStudents = [
  { id: 1, name: 'John Doe', photo_base64: '...', confidence: 0.95 }
];

const mockSlide = {
  slide_number: 1,
  text: 'Welcome to the lesson...',
  audio_path: '/mock-audio.mp3',
  duration_estimate: 30
};
```

### Environment Variables
```javascript
// .env.local
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

---

## 📊 Example Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Attendance.jsx
│   │   ├── Presentation.jsx
│   │   ├── QuestionModal.jsx
│   │   └── QATab.jsx
│   ├── services/
│   │   ├── api.js          // API calls
│   │   └── websocket.js    // WebSocket logic
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useWebSocket.js
│   │   └── useAudio.js
│   └── utils/
│       ├── constants.js
│       └── helpers.js
└── package.json
```

---

## 🎓 Learning Resources

### WebSocket
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [WebSocket Tutorial](https://javascript.info/websocket)

### Audio API
- [MDN Audio](https://developer.mozilla.org/en-US/docs/Web/API/HTMLAudioElement)
- [MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)

### Camera Access
- [MediaDevices getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)

---

## 🎉 Final Words

You have **everything you need** to build an amazing frontend!

The backend is **fully ready** with:
✅ Real-time WebSocket updates
✅ Automatic attendance with face recognition
✅ Presentation with TTS audio
✅ Live Q&A with audio responses
✅ Auto-scheduling at 8AM
✅ Comprehensive API

All the endpoints are **tested and working**. The documentation has **code examples** for everything.

**You got this!** 💪

Start with the login and dashboard, then work through each view step by step. Test each feature as you build it.

Good luck! 🚀

---

**Questions?** Check the docs or test the API at http://localhost:8000/docs

**Happy coding!** 👨‍💻👩‍💻
