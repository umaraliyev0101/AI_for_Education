#!/usr/bin/env python3
"""
Face Recognition Attendance System
==================================

Real-time attendance marking using face recognition at entrance camera.
"""

import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
from typing import List, Optional, Tuple, Dict
import logging
from datetime import datetime
import time

from .face_recognition_db import FaceRecognitionDB
from .face_enrollment import FaceEnrollmentSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognitionAttendance:
    """Real-time face recognition for automatic attendance"""

    def __init__(self, db_path: str = "attendance.db", device: str = "auto", threshold: float = 0.6):
        """
        Initialize face recognition attendance system
        
        Args:
            db_path: Path to SQLite database
            device: Device for inference ('cuda', 'cpu', or 'auto')
            threshold: Distance threshold for face matching (lower = stricter)
        """
        self.db = FaceRecognitionDB(db_path)
        self.threshold = threshold
        self.enrollment_system = FaceEnrollmentSystem(device)
        
        # Use same models from enrollment system
        self.mtcnn = self.enrollment_system.mtcnn
        self.resnet = self.enrollment_system.resnet
        
        # Load all student encodings into memory for fast comparison
        self.student_encodings = []
        self.student_ids = []
        self._load_database()
        
        # Track recent recognitions to avoid duplicate marking
        self.recent_recognitions = {}  # {student_id: timestamp}
        self.recognition_cooldown = 30  # seconds
        
        logger.info("✅ Face recognition attendance system ready")

    def _load_database(self):
        """Load all student encodings from database"""
        encodings, ids = self.db.get_all_encodings(active_only=True)
        self.student_encodings = encodings
        self.student_ids = ids
        logger.info(f"📚 Loaded {len(self.student_ids)} student profiles")

    def reload_database(self):
        """Reload student encodings (call after adding new students)"""
        self._load_database()

    def recognize_face(self, face_tensor: torch.Tensor) -> Tuple[Optional[str], float]:
        """
        Recognize a face by comparing against database
        
        Args:
            face_tensor: Aligned face tensor from MTCNN
            
        Returns:
            Tuple of (student_id, confidence) or (None, 0.0) if no match
        """
        if not self.student_encodings:
            return None, 0.0
        
        try:
            # Generate encoding for detected face
            encoding = self.enrollment_system.generate_encoding(face_tensor)
            
            if encoding is None:
                return None, 0.0
            
            # Calculate distances to all stored encodings
            distances = []
            for stored_encoding in self.student_encodings:
                # Euclidean distance
                distance = np.linalg.norm(encoding - stored_encoding)
                distances.append(distance)
            
            # Find minimum distance
            min_distance = min(distances)
            min_index = distances.index(min_distance)
            
            # Check if below threshold
            if min_distance < self.threshold:
                student_id = self.student_ids[min_index]
                # Convert distance to confidence (0-1 range)
                # Distance typically ranges from 0 (perfect match) to ~1.4 (different faces)
                # Use exponential decay for better confidence scores
                confidence = np.exp(-min_distance * 2.0)
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
                return student_id, confidence
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"❌ Recognition failed: {e}")
            return None, 0.0

    def process_frame(self, frame: np.ndarray, mark_attendance: bool = True) -> Tuple[np.ndarray, List[Dict]]:
        """
        Process a single frame for face recognition
        
        Args:
            frame: BGR image from camera
            mark_attendance: Whether to mark attendance in database
            
        Returns:
            Tuple of (annotated_frame, recognized_students)
        """
        recognized = []
        
        try:
            face_tensor = self._prepare_face_tensor(frame)
            if face_tensor is not None:
                recognized = self._handle_recognition(face_tensor, frame, mark_attendance)
            
            return frame, recognized
            
        except Exception as e:
            logger.error(f"❌ Frame processing failed: {e}")
            return frame, []

    def _prepare_face_tensor(self, frame: np.ndarray) -> Optional[torch.Tensor]:
        """Detect face and prepare tensor for recognition."""
        face = self.enrollment_system.detect_face(frame)
        if face is None:
            return None
        
        if isinstance(face, np.ndarray):
            # Convert BGR->RGB, HWC->CHW, scale to [0,1] and make float tensor
            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            return torch.from_numpy(face_rgb).permute(2, 0, 1).float() / 255.0
        else:
            # Assume it's already a torch.Tensor-like object
            return face

    def _handle_recognition(self, face_tensor: torch.Tensor, frame: np.ndarray, mark_attendance: bool) -> List[Dict]:
        """Handle face recognition, attendance marking, and annotation."""
        recognized = []
        student_id, confidence = self.recognize_face(face_tensor)
        
        if student_id is not None:
            student = self.db.get_student(student_id)
            if student and self._check_and_mark_attendance(student_id, confidence, mark_attendance):
                recognized.append({
                    'student_id': student_id,
                    'name': student['name'],
                    'class': student['class_name'],
                    'confidence': confidence
                })
            # Annotate frame regardless of cooldown
            frame = self._annotate_frame(frame, student['name'], confidence)
        
        return recognized

    def _check_and_mark_attendance(self, student_id: str, confidence: float, mark_attendance: bool) -> bool:
        """Check cooldown and mark attendance if allowed."""
        current_time = time.time()
        last_recognition = self.recent_recognitions.get(student_id, 0)
        
        if current_time - last_recognition <= self.recognition_cooldown:
            return False
        
        if mark_attendance:
            success = self.db.mark_attendance(student_id, confidence)
            if success:
                self.recent_recognitions[student_id] = current_time
                student = self.db.get_student(student_id)
                logger.info(f"✅ Attendance: {student['name']} ({confidence:.2f})")
        
        return True

    def _annotate_frame(self, frame: np.ndarray, name: str, confidence: float) -> np.ndarray:
        """Draw recognition result on frame"""
        # Draw rectangle around face area (approximate)
        height, width = frame.shape[:2]
        face_box = (
            int(width * 0.25),
            int(height * 0.15),
            int(width * 0.75),
            int(height * 0.85)
        )
        
        cv2.rectangle(frame, (face_box[0], face_box[1]), (face_box[2], face_box[3]), (0, 255, 0), 2)
        
        # Draw name and confidence
        label = f"{name} ({confidence:.2f})"
        cv2.putText(
            frame,
            label,
            (face_box[0], face_box[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )
        
        return frame

    def run_entrance_camera(self, camera_id: int = 0, display: bool = True):
        """
        Run attendance system with entrance camera
        
        Args:
            camera_id: Camera device ID
            display: Whether to display video feed
        """
        try:
            cap = cv2.VideoCapture(camera_id)
            
            if not cap.isOpened():
                logger.error("❌ Cannot open camera")
                return
            
            logger.info("📹 Entrance camera started")
            logger.info("Press 'q' to quit, 'r' to reload database")
            
            frame_count = 0
            process_every_n_frames = 5  # Process every 5th frame for performance
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.error("❌ Failed to read frame")
                    break
                
                # Process frame
                if frame_count % process_every_n_frames == 0:
                    frame, recognized = self.process_frame(frame, mark_attendance=True)
                
                frame_count += 1
                
                # Display
                if display:
                    # Add timestamp and count
                    cv2.putText(
                        frame,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    cv2.putText(
                        frame,
                        f"Students: {len(self.student_ids)}",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    cv2.imshow('Attendance System', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    logger.info("🛑 Stopping camera")
                    break
                elif key == ord('r'):
                    logger.info("🔄 Reloading database")
                    self.reload_database()
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            logger.error(f"❌ Camera operation failed: {e}")

    def process_video_file(self, video_path: str, output_path: Optional[str] = None):
        """
        Process a video file for attendance
        
        Args:
            video_path: Path to video file
            output_path: Optional path to save annotated video
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"❌ Cannot open video: {video_path}")
                return
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Video writer for output
            writer = None
            if output_path:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            logger.info(f"📹 Processing video: {video_path}")
            
            frame_count = 0
            all_recognized = []
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Process every 15 frames (for ~2 fps processing)
                if frame_count % 15 == 0:
                    frame, recognized = self.process_frame(frame, mark_attendance=True)
                    all_recognized.extend(recognized)
                
                if writer:
                    writer.write(frame)
                
                frame_count += 1
                
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count} frames...")
            
            cap.release()
            if writer:
                writer.release()
            
            # Summary
            unique_students = set(r['student_id'] for r in all_recognized)
            logger.info(f"✅ Video processing complete")
            logger.info(f"Recognized {len(unique_students)} unique students")
            
        except Exception as e:
            logger.error(f"❌ Video processing failed: {e}")

    def get_attendance_report(self, date: Optional[str] = None) -> Dict:
        """Generate attendance report for a date"""
        return self.db.get_attendance_summary(date)

    def close(self):
        """Clean up resources"""
        self.db.close()


def test_attendance_system():
    """Test attendance system"""
    print("🧪 Testing Face Recognition Attendance System...")
    
    attendance = FaceRecognitionAttendance()
    
    print(f"✅ System initialized with {len(attendance.student_ids)} students")
    
    # Get today's summary
    summary = attendance.get_attendance_report()
    print(f"Today's attendance: {summary.get('present', 0)}/{summary.get('total_students', 0)}")
    
    attendance.close()


if __name__ == "__main__":
    test_attendance_system()
