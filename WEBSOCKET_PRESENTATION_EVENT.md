# 📡 WebSocket "presentation_started" Event

## Event Trigger

When teacher sends:
```json
{
  "type": "start_presentation"
}
```

## Frontend Receives

```json
{
  "type": "presentation_started",
  "lesson_id": 2,
  "lesson_title": "Introduction to AI in Education",
  "total_slides": 5,
  "current_slide_number": 1,
  "timestamp": "2025-10-31T14:30:00.123456",
  "slides": [
    {
      "slide_number": 1,
      "text": "O'zbekiston tarixi: Qadimgi davr",
      "audio_path": "uploads/audio/presentations/lesson_2_slide_1.mp3",
      "image_path": "uploads/slides/lesson_2/slide_1.png",
      "duration_estimate": 3.5
    },
    {
      "slide_number": 2,
      "text": "Qadimgi shaharlar va madaniyat",
      "audio_path": "uploads/audio/presentations/lesson_2_slide_2.mp3",
      "image_path": "uploads/slides/lesson_2/slide_2.png",
      "duration_estimate": 5.2
    },
    {
      "slide_number": 3,
      "text": "Amir Temur davri",
      "audio_path": "uploads/audio/presentations/lesson_2_slide_3.mp3",
      "image_path": "uploads/slides/lesson_2/slide_3.png",
      "duration_estimate": 4.8
    }
    // ... more slides
  ]
}
```

## Frontend Implementation

```javascript
// Connect to WebSocket
const token = localStorage.getItem('access_token');
const lessonId = 2;
const ws = new WebSocket(`ws://localhost:8001/api/ws/lesson/${lessonId}?token=${token}`);

let allSlides = [];
let currentSlideIndex = 0;

ws.onopen = () => {
  console.log('✅ Connected to lesson WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('📨 Received:', data.type);
  
  switch(data.type) {
    case 'presentation_started':
      handlePresentationStarted(data);
      break;
    
    case 'slide_changed':
      handleSlideChanged(data.slide);
      break;
    
    case 'presentation_paused':
      handlePresentationPaused();
      break;
    
    case 'presentation_resumed':
      handlePresentationResumed();
      break;
    
    case 'presentation_completed':
      handlePresentationCompleted();
      break;
  }
};

function handlePresentationStarted(data) {
  console.log(`📊 Presentation started: ${data.lesson_title}`);
  console.log(`Total slides: ${data.total_slides}`);
  
  // Store all slides
  allSlides = data.slides;
  currentSlideIndex = 0;
  
  // Display first slide
  displaySlide(allSlides[0]);
  
  // Update UI
  document.getElementById('lesson-title').textContent = data.lesson_title;
  document.getElementById('slide-counter').textContent = `1 / ${data.total_slides}`;
  document.getElementById('presentation-container').style.display = 'block';
}

function displaySlide(slide) {
  // Display slide image (MAIN CONTENT)
  const slideImage = document.getElementById('slide-image');
  slideImage.src = `http://localhost:8001/${slide.image_path}`;
  slideImage.alt = `Slide ${slide.slide_number}`;
  
  // Show slide text (for transcript/accessibility)
  const slideText = document.getElementById('slide-text');
  slideText.textContent = slide.text;
  
  // Play audio narration
  const audio = new Audio(`http://localhost:8001/${slide.audio_path}`);
  audio.play();
  
  // Auto-advance to next slide when audio ends
  audio.onended = () => {
    console.log('Audio finished, ready for next slide');
    // Teacher will send next_slide command or you can auto-advance
  };
  
  // Update slide number
  document.getElementById('current-slide-number').textContent = slide.slide_number;
  
  console.log(`✅ Displaying slide ${slide.slide_number}: ${slide.text.substring(0, 30)}...`);
}

function handleSlideChanged(slide) {
  currentSlideIndex = slide.slide_number - 1;
  displaySlide(slide);
  document.getElementById('slide-counter').textContent = 
    `${slide.slide_number} / ${allSlides.length}`;
}

function handlePresentationPaused() {
  console.log('⏸️ Presentation paused');
  const audio = document.querySelector('audio');
  if (audio) audio.pause();
  
  document.getElementById('pause-indicator').style.display = 'block';
}

function handlePresentationResumed() {
  console.log('▶️ Presentation resumed');
  const audio = document.querySelector('audio');
  if (audio) audio.play();
  
  document.getElementById('pause-indicator').style.display = 'none';
}

function handlePresentationCompleted() {
  console.log('🎉 Presentation completed! Starting Q&A mode...');
  document.getElementById('presentation-container').style.display = 'none';
  document.getElementById('qa-container').style.display = 'block';
}

// Teacher controls (send commands)
function nextSlide() {
  ws.send(JSON.stringify({ type: 'next_slide' }));
}

function previousSlide() {
  ws.send(JSON.stringify({ type: 'previous_slide' }));
}

function pausePresentation() {
  ws.send(JSON.stringify({ type: 'pause_presentation' }));
}

function resumePresentation() {
  ws.send(JSON.stringify({ type: 'resume_presentation' }));
}
```

## HTML Structure

```html
<div id="presentation-container" style="display: none;">
  <div class="presentation-header">
    <h2 id="lesson-title">Lesson Title</h2>
    <span id="slide-counter">1 / 5</span>
  </div>
  
  <div class="slide-display">
    <!-- Main slide image -->
    <img id="slide-image" src="" alt="Slide" class="slide-image"/>
    
    <!-- Pause indicator -->
    <div id="pause-indicator" style="display: none;" class="pause-overlay">
      ⏸️ PAUSED
    </div>
  </div>
  
  <div class="slide-transcript">
    <h4>Transcript:</h4>
    <p id="slide-text"></p>
  </div>
  
  <div class="presentation-controls" v-if="userRole === 'teacher'">
    <button onclick="previousSlide()">⬅️ Previous</button>
    <button onclick="pausePresentation()">⏸️ Pause</button>
    <button onclick="resumePresentation()">▶️ Resume</button>
    <button onclick="nextSlide()">Next ➡️</button>
  </div>
</div>
```

## CSS Styling

```css
.slide-display {
  position: relative;
  width: 100%;
  max-width: 1200px;
  margin: 20px auto;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.slide-image {
  width: 100%;
  height: auto;
  display: block;
}

.pause-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 40px 80px;
  border-radius: 10px;
  font-size: 48px;
  font-weight: bold;
}

.slide-transcript {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 20px 0;
}

.presentation-controls {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 20px;
}

.presentation-controls button {
  padding: 12px 24px;
  font-size: 16px;
  border: none;
  border-radius: 6px;
  background: #007bff;
  color: white;
  cursor: pointer;
  transition: background 0.3s;
}

.presentation-controls button:hover {
  background: #0056b3;
}
```

## Key Points

### ✅ What Frontend Gets:
1. **All slide data** at once (not just current slide)
2. **Image paths** to display actual slides
3. **Audio paths** for TTS narration
4. **Text content** for transcripts/accessibility
5. **Slide count** for progress tracking

### ✅ Static File Access Fixed:
- Backend now serves files via `/uploads` mount
- Frontend can access: `http://localhost:8001/uploads/slides/lesson_2/slide_1.png`
- CORS allows all origins for development

### ✅ Teacher Flow:
1. Upload presentation → `POST /api/lessons/{id}/presentation`
2. Process presentation → `POST /api/lessons/{id}/presentation/process`
3. Start lesson WebSocket → `ws://localhost:8001/api/ws/lesson/{id}?token={token}`
4. Start presentation → Send `{"type": "start_presentation"}`
5. Frontend receives `presentation_started` with ALL slide data
6. Control slides with `next_slide`, `previous_slide`, `pause_presentation`

### ✅ Student Flow:
1. Connect to lesson WebSocket
2. Receive `presentation_started` event
3. Display current slide image
4. Listen to audio narration
5. Follow along as slides change
6. See pause indicator when teacher pauses

---

**Status:** ✅ Fully Implemented  
**Date:** October 31, 2025  
**Fixes:**
- Static files now accessible via `/uploads` mount
- `presentation_started` includes ALL slide data with images
- Complete frontend integration examples provided
