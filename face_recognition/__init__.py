"""
Face Recognition System for Automatic Attendance

This package contains the face recognition system components:
- face_recognition_db: SQLite database management
- face_enrollment: Student enrollment with FaceNet
- face_attendance: Real-time attendance tracking
"""

from .face_recognition_db import FaceRecognitionDB
from .face_enrollment import FaceEnrollmentSystem
from .face_attendance import FaceRecognitionAttendance

__all__ = ['FaceRecognitionDB', 'FaceEnrollmentSystem', 'FaceRecognitionAttendance']
