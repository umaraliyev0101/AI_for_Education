# Frontend Visual Guide
## UI/UX Design Reference for Lesson System

---

## 📱 Screen Layouts

### 1. Login Screen
```
┌──────────────────────────────────────────────┐
│                                              │
│          🎓 AI Education System             │
│                                              │
│     ┌────────────────────────────────┐      │
│     │ Username: ________________     │      │
│     │                                │      │
│     │ Password: ________________     │      │
│     │                                │      │
│     │        [Login Button]          │      │
│     └────────────────────────────────┘      │
│                                              │
└──────────────────────────────────────────────┘
```

---

### 2. Teacher Dashboard
```
┌──────────────────────────────────────────────────────────┐
│  🏠 Dashboard    👤 Profile    🚪 Logout                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📅 Today's Lesson                                       │
│  ┌────────────────────────────────────────────────┐     │
│  │  Title: Algebra Basics                         │     │
│  │  Time: 08:00 AM - 09:30 AM                     │     │
│  │  Status: 🟡 Scheduled                          │     │
│  │                                                 │     │
│  │  [Start Attendance]  [View Details]            │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  📊 Quick Stats                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │ 25/30   │  │   10    │  │   95%   │                 │
│  │Students │  │Lessons  │  │Attendance│                 │
│  └─────────┘  └─────────┘  └─────────┘                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 3. Attendance Screen
```
┌──────────────────────────────────────────────────────────┐
│  ◀ Back    📸 Attendance    Status: Scanning...   [End] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Present: 5/30                                           │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  📸     │  │  📸     │  │  📸     │  │  📸     │   │
│  │ [PHOTO] │  │ [PHOTO] │  │ [PHOTO] │  │ [PHOTO] │   │
│  │         │  │         │  │         │  │         │   │
│  │  John   │  │  Mary   │  │  Alex   │  │  Sara   │   │
│  │  Doe    │  │  Smith  │  │ Johnson │  │  Lee    │   │
│  │  95% ✓  │  │  89% ✓  │  │  92% ✓  │  │  87% ✓  │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │  📸     │  │   ➕    │  │  Empty  │                 │
│  │ [PHOTO] │  │  Add    │  │         │                 │
│  │         │  │ Manual  │  │         │                 │
│  │  Tom    │  │         │  │         │                 │
│  │  Brown  │  │         │  │         │                 │
│  │  91% ✓  │  │         │  │         │                 │
│  └─────────┘  └─────────┘  └─────────┘                 │
│                                                          │
│              [Rescan]  [Start Lesson]                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 4. Presentation Screen
```
┌──────────────────────────────────────────────────────────┐
│  ◀ Back    📊 Presentation    Slide 3/10    [End Lesson]│
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ╔════════════════════════════════════════════════════╗ │
│  ║                                                    ║ │
│  ║        Slide Title: Introduction to Algebra      ║ │
│  ║                                                    ║ │
│  ║  • Algebra is a branch of mathematics             ║ │
│  ║  • It uses symbols to represent numbers           ║ │
│  ║  • Example: x + 5 = 10                            ║ │
│  ║  • We can solve for x: x = 5                      ║ │
│  ║                                                    ║ │
│  ║                                                    ║ │
│  ║                                                    ║ │
│  ╚════════════════════════════════════════════════════╝ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 🔊 Audio Playing...  ━━━━━━━●────  00:45 / 02:15│   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────┐  ┌────────────────┐  ┌────────┐            │
│  │   ◀    │  │   ❓ Ask       │  │   ▶    │            │
│  │Previous│  │   Question     │  │  Next  │            │
│  └────────┘  └────────────────┘  └────────┘            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 5. Question Modal (During Presentation)
```
┌──────────────────────────────────────────────────────────┐
│  📊 Presentation (Paused)                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │                                                    │ │
│  │  ❓ Ask Your Question                             │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ Type your question here...                   │ │ │
│  │  │                                              │ │ │
│  │  │                                              │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │                   OR                               │ │
│  │                                                    │ │
│  │         ┌────────────────────────┐                │ │
│  │         │  🎤  Record Audio      │                │ │
│  │         │  [Tap to start]        │                │ │
│  │         └────────────────────────┘                │ │
│  │                                                    │ │
│  │  ┌──────────┐              ┌──────────┐          │ │
│  │  │  Cancel  │              │  Submit  │          │ │
│  │  └──────────┘              └──────────┘          │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 6. Answer Display (During Presentation)
```
┌──────────────────────────────────────────────────────────┐
│  📊 Presentation (Question Answered)                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │                                                    │ │
│  │  ❓ Your Question:                                │ │
│  │  "What is the value of x in x + 5 = 10?"         │ │
│  │                                                    │ │
│  │  ✅ Answer:                                       │ │
│  │  "To find x, we subtract 5 from both sides:      │ │
│  │   x + 5 - 5 = 10 - 5                             │ │
│  │   x = 5"                                          │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ 🔊 Answer Audio  ━━━━●───  00:15 / 00:30    │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │              ┌──────────────────┐                 │ │
│  │              │  Continue Lesson │                 │ │
│  │              └──────────────────┘                 │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 7. Q&A Tab (After Presentation)
```
┌──────────────────────────────────────────────────────────┐
│  ◀ Back    💬 Q&A Session    Status: Active   [End]     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📝 Question History                                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Q: What is algebra?                                │ │
│  │ A: Algebra is a branch of mathematics that uses   │ │
│  │    symbols to represent numbers and relationships.│ │
│  │    🔊 [Play Audio]                          08:15 │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Q: Can you give an example?                       │ │
│  │ A: Sure! In the equation x + 5 = 10, x is a      │ │
│  │    symbol representing an unknown number.         │ │
│  │    🔊 [Play Audio]                          08:17 │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Q: How do we solve for x?                         │ │
│  │ A: To solve for x, we need to isolate it...      │ │
│  │    🔊 [Play Audio]                          08:19 │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  💬 Ask New Question                                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Type your question here...                         │ │
│  └────────────────────────────────────────────────────┘ │
│  [🎤 Record] [📤 Send]                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🎨 Color Scheme Suggestions

### Status Colors
```
🟢 Active/Present  - #4CAF50 (Green)
🟡 Scheduled       - #FFC107 (Amber)
🔴 Absent/Error    - #F44336 (Red)
🔵 In Progress     - #2196F3 (Blue)
⚪ Completed       - #9E9E9E (Gray)
```

### UI Elements
```
Primary:    #1976D2 (Blue)
Secondary:  #424242 (Dark Gray)
Accent:     #FF4081 (Pink)
Background: #FAFAFA (Light Gray)
Text:       #212121 (Almost Black)
Success:    #4CAF50 (Green)
Warning:    #FF9800 (Orange)
Error:      #F44336 (Red)
```

---

## 📐 Layout Dimensions

### Mobile (Portrait)
```
Screen Width: 360px - 414px
Card Height: 120px
Image Size: 80x80px
Button Height: 48px
Font Sizes:
  - Title: 20px
  - Body: 16px
  - Caption: 14px
```

### Tablet
```
Screen Width: 768px - 1024px
Card Height: 160px
Image Size: 120x120px
Button Height: 56px
Font Sizes:
  - Title: 24px
  - Body: 18px
  - Caption: 16px
```

### Desktop
```
Screen Width: 1280px+
Card Height: 200px
Image Size: 150x150px
Button Height: 64px
Font Sizes:
  - Title: 28px
  - Body: 20px
  - Caption: 18px
```

---

## 🎬 Animations

### Page Transitions
```css
/* Slide in from right */
.page-enter {
  transform: translateX(100%);
  transition: transform 0.3s ease-out;
}

/* Fade in */
.fade-enter {
  opacity: 0;
  transition: opacity 0.3s ease-in;
}
```

### Button Feedback
```css
.button:active {
  transform: scale(0.95);
  transition: transform 0.1s;
}

.button:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  transition: box-shadow 0.2s;
}
```

### Student Card Appearance
```css
.student-card {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 🔔 Notification Examples

### Success
```
┌────────────────────────────────┐
│ ✅ Attendance marked!          │
│ 5 students recognized          │
└────────────────────────────────┘
```

### Warning
```
┌────────────────────────────────┐
│ ⚠️ Low confidence detected     │
│ Please verify attendance       │
└────────────────────────────────┘
```

### Error
```
┌────────────────────────────────┐
│ ❌ Connection lost             │
│ Reconnecting...                │
└────────────────────────────────┘
```

### Info
```
┌────────────────────────────────┐
│ ℹ️ Lesson will start at 8:00 AM│
│ Tap to start early             │
└────────────────────────────────┘
```

---

## 🎯 Interactive Elements

### Audio Player
```
┌──────────────────────────────────────────┐
│ 🔊 Slide Audio                           │
│ ━━━━━━━━━━━●──────── 01:23 / 02:45      │
│ [⏮] [⏯️] [⏭] [🔇] [⚙️]                  │
└──────────────────────────────────────────┘
```

### Progress Bar
```
Slide Progress:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
████████████████████░░░░░░░░░░░░░░░░░░░░
Slide 5 of 10 (50%)
```

### Loading Spinner
```
    ⚙️
   Processing...
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
.container {
  width: 100%;
  padding: 16px;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    max-width: 720px;
    padding: 24px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 960px;
    padding: 32px;
  }
}

/* Large Desktop */
@media (min-width: 1280px) {
  .container {
    max-width: 1200px;
  }
}
```

---

## 🎭 Component States

### Button States
```
Normal:   [  Submit  ]
Hover:    [  Submit  ] (darker + shadow)
Active:   [  Submit  ] (slightly smaller)
Disabled: [  Submit  ] (gray + no hover)
Loading:  [  ⚙️ ...  ] (spinner + disabled)
```

### Input States
```
Normal:   ┌──────────────┐
          │              │
          └──────────────┘

Focus:    ┌══════════════┐ (blue border)
          ║              ║
          └══════════════┘

Error:    ┌──────────────┐ (red border)
          │              │
          └──────────────┘
          ⚠️ Error message

Success:  ┌──────────────┐ (green border)
          │              │
          └──────────────┘
          ✓ Valid
```

---

## 🎪 Modal Patterns

### Confirmation Modal
```
┌────────────────────────────────────────┐
│                                        │
│  ⚠️  End Lesson?                      │
│                                        │
│  Are you sure you want to end         │
│  this lesson? This cannot be undone.  │
│                                        │
│  ┌────────┐         ┌────────┐        │
│  │ Cancel │         │   End  │        │
│  └────────┘         └────────┘        │
│                                        │
└────────────────────────────────────────┘
```

### Loading Modal
```
┌────────────────────────────────────────┐
│                                        │
│            ⚙️                          │
│                                        │
│      Processing Presentation...        │
│                                        │
│  ████████████░░░░░░░░░ 60%            │
│                                        │
└────────────────────────────────────────┘
```

---

## 📊 Data Visualization

### Attendance Stats
```
┌─────────────────────────────────────┐
│  Attendance Rate                    │
│                                     │
│  ████████████████████░░░  85%       │
│                                     │
│  Present:   25 students             │
│  Absent:     5 students             │
│  Total:     30 students             │
└─────────────────────────────────────┘
```

### Lesson Timeline
```
Timeline:
08:00 ━━━━━━━ Lesson Started
08:05 ━━━━━━━ Attendance Completed
08:10 ━━━━━━━ Presentation Started
08:45 ━━━━━━━ Q&A Session
09:30 ━━━━━━━ Lesson Ended
```

---

## 🎤 Audio Recording UI

### Recording State
```
┌────────────────────────────────────┐
│                                    │
│         🎤  Recording...           │
│                                    │
│         ●●●●●●●●●●                 │
│         00:15                       │
│                                    │
│    [Stop]            [Cancel]      │
│                                    │
└────────────────────────────────────┘
```

### Playback State
```
┌────────────────────────────────────┐
│                                    │
│    🔊  Your Question               │
│                                    │
│    ━━━━●────────── 00:03 / 00:15  │
│                                    │
│    [Replay]         [Submit]       │
│                                    │
└────────────────────────────────────┘
```

---

## 🖼️ Image Guidelines

### Student Photos
- **Format**: JPEG or PNG
- **Size**: 150x150px (display), 400x400px (uploaded)
- **Aspect Ratio**: 1:1 (square)
- **Fallback**: Show initials if no photo

### Slide Images
- **Format**: JPEG, PNG
- **Max Size**: 1920x1080px
- **Aspect Ratio**: 16:9 preferred
- **Quality**: 80% JPEG compression

---

## ♿ Accessibility

### Required Attributes
```html
<!-- Buttons -->
<button aria-label="Next slide">▶</button>

<!-- Images -->
<img alt="Student photo: John Doe" />

<!-- Forms -->
<input aria-label="Question text" />

<!-- Status -->
<div role="status" aria-live="polite">
  Lesson started
</div>
```

### Keyboard Navigation
```
Tab       - Navigate between elements
Enter     - Activate button/submit
Space     - Toggle/select
Esc       - Close modal
Arrow keys - Navigate slides
```

---

## 🔧 Browser Support

### Required Features
- ✅ WebSocket
- ✅ Audio API
- ✅ MediaDevices API (camera/mic)
- ✅ FormData
- ✅ Fetch API
- ✅ ES6+ JavaScript

### Fallbacks
- No WebSocket → Show error, use polling
- No camera → Manual attendance entry
- No microphone → Text-only questions
- No audio → Display text only

---

## 📦 Component Checklist

### Must Have
- [ ] Login form
- [ ] Lesson list/dashboard
- [ ] Attendance grid with photos
- [ ] Presentation viewer
- [ ] Audio player
- [ ] Question modal
- [ ] Q&A history
- [ ] Navigation buttons
- [ ] Status indicators

### Nice to Have
- [ ] Animations
- [ ] Progress bars
- [ ] Toast notifications
- [ ] Dark mode
- [ ] Keyboard shortcuts
- [ ] Offline mode indicator
- [ ] Export Q&A as PDF

---

## 🎨 CSS Framework Suggestions

### Option 1: Tailwind CSS
- Fast development
- Utility-first
- Easy responsive design

### Option 2: Material-UI (React)
- Pre-built components
- Professional look
- Good accessibility

### Option 3: Custom CSS
- Full control
- Smaller bundle size
- Match exact design

---

## 🚀 Performance Tips

1. **Lazy load** student photos
2. **Preload** next slide audio
3. **Debounce** WebSocket reconnection
4. **Cache** presentation data
5. **Optimize** images (WebP format)
6. **Minimize** re-renders
7. **Use** virtual scrolling for long lists

---

**Need more details?** Check:
- `FRONTEND_INTEGRATION_GUIDE.md` - Technical implementation
- `FRONTEND_QUICK_REFERENCE.md` - API quick reference
- `http://localhost:8000/docs` - Live API documentation
