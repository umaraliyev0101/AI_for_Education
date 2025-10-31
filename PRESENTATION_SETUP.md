# 📊 Presentation Processing Setup

## Overview

The backend now converts presentation files (PPTX/PDF) to PNG slide images for proper frontend display.

## Required Libraries

### Python Packages (Already Installed)

```bash
pip install pillow pdf2image comtypes
```

- **Pillow (PIL)**: Image processing
- **pdf2image**: Converts PDF pages to images
- **comtypes**: Windows COM interface for PowerPoint

### System Requirements

#### For PDF Processing

**pdf2image** requires **Poppler** to be installed on your system:

**Windows:**
1. Download Poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\poppler` (or any directory)
3. Add `C:\poppler\Library\bin` to your PATH environment variable

**Or use Chocolatey:**
```powershell
choco install poppler
```

**Verify Installation:**
```powershell
pdftoppm -v
```

#### For PPTX Processing (Windows Only)

- **Microsoft PowerPoint** must be installed
- **comtypes** uses PowerPoint COM automation
- Only works on Windows with PowerPoint installed

**Alternative for Linux/Mac:**
- Use LibreOffice: `libreoffice --headless --convert-to pdf presentation.pptx`
- Then use pdf2image on the converted PDF

## How It Works

### 1. Upload Presentation

```http
POST /api/lessons/{id}/presentation
Content-Type: multipart/form-data

file: [presentation.pptx or presentation.pdf]
```

### 2. Process Presentation

```http
POST /api/lessons/{id}/presentation/process
```

**Backend Processing:**
1. **PPTX Files:**
   - Opens PowerPoint via COM
   - Exports each slide as PNG (`slide_1.png`, `slide_2.png`, etc.)
   - Saves to `uploads/slides/lesson_{id}/`

2. **PDF Files:**
   - Uses Poppler (via pdf2image)
   - Converts each page to PNG image
   - Saves to `uploads/slides/lesson_{id}/`

3. **For Both:**
   - Extracts text content
   - Generates TTS audio for each slide
   - Creates metadata JSON

### 3. Get Presentation Data

```http
GET /api/lessons/{id}/presentation
```

**Response:**
```json
{
  "lesson_id": 1,
  "total_slides": 5,
  "slides": [
    {
      "slide_number": 1,
      "text": "Slide content...",
      "audio_path": "uploads/audio/presentations/lesson_1_slide_1.mp3",
      "image_path": "uploads/slides/lesson_1/slide_1.png",
      "duration_estimate": 3.5
    }
  ]
}
```

## File Structure

```
uploads/
├── presentations/          # Original uploaded files
│   └── lesson_1_presentation.pptx
├── slides/                 # Generated slide images (NEW)
│   └── lesson_1/
│       ├── slide_1.png
│       ├── slide_2.png
│       └── slide_3.png
└── audio/
    └── presentations/      # Generated TTS audio
        ├── lesson_1_slide_1.mp3
        ├── lesson_1_slide_2.mp3
        └── lesson_1_slide_3.mp3
```

## Frontend Integration

```javascript
// Display slide image
function showSlide(slide) {
  const img = document.getElementById('slide-image');
  img.src = `http://localhost:8001/${slide.image_path}`;
  
  // Play audio narration
  const audio = new Audio(`http://localhost:8001/${slide.audio_path}`);
  audio.play();
  
  // Show transcript (optional)
  document.getElementById('transcript').textContent = slide.text;
}
```

## Troubleshooting

### "pdf2image not working"
- **Solution:** Install Poppler (see above)
- **Verify:** Run `pdftoppm -v` in terminal

### "PPTX conversion failed"
- **Solution:** Ensure Microsoft PowerPoint is installed (Windows only)
- **Alternative:** Convert PPTX to PDF first, then use PDF processing

### "Images not displaying in frontend"
- **Check:** File exists at `uploads/slides/lesson_{id}/slide_{n}.png`
- **Check:** CORS allows serving static files
- **Check:** Image path is correct in response JSON

### "Processing takes too long"
- **Normal:** 30-60 seconds per slide (image conversion + TTS)
- **Tip:** Process presentations before lesson starts
- **Tip:** Use pre-posting feature for scheduled lessons

## Performance Notes

- **PPTX → PNG:** Fast on Windows with PowerPoint (~2-5 sec/slide)
- **PDF → PNG:** Depends on page complexity (~3-10 sec/page with Poppler)
- **TTS Audio:** ~5-15 sec/slide depending on text length

## Security

- Only authenticated teachers can upload presentations
- Files are validated (PPTX/PDF only)
- Images stored in isolated lesson directories
- Static file serving configured with security headers

---

**Status:** ✅ Ready for Use  
**Updated:** October 30, 2025
