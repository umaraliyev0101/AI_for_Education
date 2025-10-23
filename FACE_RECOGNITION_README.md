# Face Recognition Attendance System

## Overview
Automatic attendance system using FaceNet face recognition at entrance camera.

## Features
- **Student Enrollment**: Register students with facial recognition
- **Real-time Attendance**: Automatic attendance marking at entrance
- **Database Management**: SQLite database for students and attendance
- **Reporting**: Daily/monthly attendance reports
- **CLI Interface**: Easy-to-use command-line interface

## Installation

```bash
# Install dependencies
pip install facenet-pytorch opencv-python Pillow numpy torch

# Or use requirements.txt
pip install -r requirements.txt
```

## Usage

### 1. Enroll Students
```bash
# Interactive enrollment with webcam
python main.py enroll

# You'll be prompted for:
# - Student ID
# - Student Name
# - Class/Grade
# - Face photos (5 photos via webcam)
```

### 2. Start Attendance Camera
```bash
# Start entrance camera
python main.py attendance

# Use specific camera
python main.py attendance 1

# Press 'q' to quit, 'r' to reload database
```

### 3. View Reports
```bash
# Today's attendance
python main.py report

# Specific date
python main.py report 2025-10-22
```

### 4. List Students
```bash
# View all enrolled students
python main.py students
```

## How It Works

### Face Recognition Pipeline
1. **Face Detection**: MTCNN detects faces in camera frames
2. **Face Encoding**: FaceNet generates 512-dimensional encodings
3. **Face Matching**: Compare against database using Euclidean distance
4. **Attendance Marking**: Log timestamp when match found

### Database Schema

**Students Table:**
- student_id (PRIMARY KEY)
- name
- class_name
- face_encoding (BLOB)
- enrolled_date
- photos_count
- active

**Attendance Table:**
- id (AUTO INCREMENT)
- student_id (FOREIGN KEY)
- date
- timestamp
- confidence
- status

### Recognition Parameters
- **Model**: FaceNet (InceptionResnetV1)
- **Threshold**: 0.6 (Euclidean distance)
- **Encoding Size**: 512 dimensions
- **Cooldown**: 30 seconds between recognitions

## Directory Structure
```
face_recognition_db.py       # SQLite database management
face_enrollment.py           # Student enrollment module
face_attendance.py           # Real-time attendance system
main.py                      # CLI interface
attendance.db               # SQLite database (created automatically)
```

## Tips for Best Results

### Enrollment
- Take 5 photos from different angles
- Good lighting is essential
- Face should be clearly visible
- No glasses or face coverings (or include them in enrollment)

### Camera Setup
- Place camera at entrance at eye level
- Ensure good lighting
- Camera should cover entrance area
- Distance: 1-2 meters optimal

### Accuracy
- Threshold 0.6: Balanced (recommended)
- Threshold 0.5: More strict (fewer false positives)
- Threshold 0.7: More lenient (may have false positives)

## Troubleshooting

### Camera not opening
```python
# Check available cameras
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i} available")
        cap.release()
```

### Face not detected
- Improve lighting
- Move closer to camera
- Face camera directly
- Remove obstructions

### Wrong person recognized
- Lower threshold for stricter matching
- Re-enroll student with more photos
- Check for duplicate enrollments

## Privacy & Security
- Face encodings are stored (not raw photos)
- Encodings are numerical vectors, not reversible to images
- Database should be encrypted in production
- Follow local data protection regulations

## Performance
- **Enrollment**: ~5 seconds per student
- **Recognition**: ~100ms per frame
- **Database Size**: ~5-10 KB per student
- **1000 Students**: ~5-10 MB database

## Future Enhancements
- [ ] Multi-face detection in single frame
- [ ] Cloud database support
- [ ] Mobile app integration
- [ ] Email/SMS notifications
- [ ] Anti-spoofing (liveness detection)
- [ ] Export to Excel/CSV
