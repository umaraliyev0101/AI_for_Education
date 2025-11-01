"""
Face Recognition Integration Service
=====================================

Bridges the gap between the backend SQLAlchemy database and the face recognition system.
Handles enrollment, recognition, and attendance marking with proper synchronization.
"""

import os
import logging
import numpy as np
import pickle
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session

from backend.models.student import Student
from backend.config import settings
from face_recognition.face_enrollment import FaceEnrollmentSystem
from face_recognition.face_attendance import FaceRecognitionAttendance
from face_recognition.face_recognition_db import FaceRecognitionDB

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """
    Service for integrating face recognition with the backend database.
    
    This service manages:
    - Student face enrollment from uploaded images
    - Face encoding storage in the main database
    - Synchronization between SQLAlchemy and face recognition databases
    - Face recognition for attendance marking
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the face recognition service
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.enrollment_system = FaceEnrollmentSystem()
        self.face_db_path = os.path.join(settings.UPLOAD_DIR, "attendance.db")
        logger.info("✅ Face Recognition Service initialized")
    
    def enroll_student_from_image(
        self,
        student_id: int,
        image_path: str
    ) -> Tuple[bool, str]:
        """
        Enroll a student using a single face image
        
        Args:
            student_id: Student database ID (primary key)
            image_path: Path to the face image file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get student from database
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, f"Student with ID {student_id} not found"
            
            if not os.path.exists(image_path):
                return False, f"Image file not found: {image_path}"
            
            # Process image with enrollment system
            import cv2
            image = cv2.imread(image_path)
            if image is None:
                return False, "Failed to read image file"
            
            # Detect face
            face_tensor = self.enrollment_system.detect_face(image)
            if face_tensor is None:
                return False, "No face detected in image"
            
            # Generate face encoding
            encoding = self.enrollment_system.generate_encoding(face_tensor)
            if encoding is None:
                return False, "Failed to generate face encoding"
            
            # Save encoding to database as pickle (for SQLAlchemy LargeBinary)
            encoding_bytes = pickle.dumps(encoding)
            student.face_encoding = encoding_bytes
            student.face_image_path = image_path
            
            # Commit to database
            self.db.commit()
            
            # Also sync to face recognition database
            self._sync_to_face_db(student, encoding)
            
            logger.info(f"✅ Enrolled student {student.student_id} ({student.name})")
            return True, f"Successfully enrolled {student.name}"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Enrollment failed: {e}")
            return False, f"Enrollment error: {str(e)}"
    
    def enroll_student_from_multiple_images(
        self,
        student_id: int,
        image_paths: List[str]
    ) -> Tuple[bool, str]:
        """
        Enroll a student using multiple face images for better accuracy
        
        Args:
            student_id: Student database ID (primary key)
            image_paths: List of paths to face image files
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get student from database
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, f"Student with ID {student_id} not found"
            
            # Process all images
            encodings = []
            for image_path in image_paths:
                if not os.path.exists(image_path):
                    logger.warning(f"⚠️ Image not found: {image_path}")
                    continue
                
                import cv2
                image = cv2.imread(image_path)
                if image is None:
                    logger.warning(f"⚠️ Cannot read image: {image_path}")
                    continue
                
                # Detect face
                face_tensor = self.enrollment_system.detect_face(image)
                if face_tensor is None:
                    logger.warning(f"⚠️ No face in image: {image_path}")
                    continue
                
                # Generate encoding
                encoding = self.enrollment_system.generate_encoding(face_tensor)
                if encoding is not None:
                    encodings.append(encoding)
            
            if not encodings:
                return False, "No valid face encodings generated from provided images"
            
            # Average encodings for robustness
            final_encoding = self.enrollment_system.average_encodings(encodings)
            if final_encoding is None:
                return False, "Failed to average face encodings"
            
            # Save encoding to database
            encoding_bytes = pickle.dumps(final_encoding)
            student.face_encoding = encoding_bytes
            student.face_image_path = image_paths[0]  # Use first image as reference
            
            # Commit to database
            self.db.commit()
            
            # Sync to face recognition database
            self._sync_to_face_db(student, final_encoding)
            
            logger.info(f"✅ Enrolled student {student.student_id} with {len(encodings)} photos")
            return True, f"Successfully enrolled {student.name} using {len(encodings)} photos"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Multi-image enrollment failed: {e}")
            return False, f"Enrollment error: {str(e)}"
    
    def recognize_face_from_image(
        self,
        image_path: str
    ) -> Tuple[Optional[Student], float]:
        """
        Recognize a student from a face image
        
        Args:
            image_path: Path to the face image
            
        Returns:
            Tuple of (student: Student or None, confidence: float)
        """
        try:
            import cv2
            image = cv2.imread(image_path)
            if image is None:
                return None, 0.0
            
            # Use face recognition system
            recognition_system = FaceRecognitionAttendance(
                db_path=self.face_db_path,
                threshold=0.6
            )
            
            # Process frame
            _, recognized = recognition_system.process_frame(image, mark_attendance=False)
            
            if not recognized:
                return None, 0.0
            
            # Get first recognized student
            student_info = recognized[0]
            student_id_str = student_info['student_id']
            confidence = student_info['confidence']
            
            # Find student in database
            student = self.db.query(Student).filter(
                Student.student_id == student_id_str
            ).first()
            
            return student, confidence
            
        except Exception as e:
            logger.error(f"❌ Face recognition failed: {e}")
            return None, 0.0
    
    def get_all_enrolled_students(self) -> List[Dict]:
        """
        Get all students with face encodings enrolled
        
        Returns:
            List of student dictionaries with enrollment info
        """
        try:
            students = self.db.query(Student).filter(
                Student.face_encoding.isnot(None),
                Student.is_active == True
            ).all()
            
            return [
                {
                    'id': s.id,
                    'student_id': s.student_id,
                    'name': s.name,
                    'email': s.email,
                    'face_image_path': s.face_image_path,
                    'enrolled': True
                }
                for s in students
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to get enrolled students: {e}")
            return []
    
    def delete_student_enrollment(self, student_id: int) -> Tuple[bool, str]:
        """
        Delete a student's face enrollment
        
        Args:
            student_id: Student database ID (primary key)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, f"Student with ID {student_id} not found"
            
            # Remove encoding from main database
            student.face_encoding = None
            student.face_image_path = None
            self.db.commit()
            
            # Remove from face recognition database
            face_db = FaceRecognitionDB(self.face_db_path)
            face_db.delete_student(student.student_id, soft_delete=False)
            face_db.close()
            
            logger.info(f"✅ Deleted enrollment for {student.student_id}")
            return True, f"Enrollment deleted for {student.name}"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to delete enrollment: {e}")
            return False, f"Deletion error: {str(e)}"
    
    def _sync_to_face_db(self, student: Student, encoding: np.ndarray):
        """
        Synchronize student enrollment to the face recognition database
        
        Args:
            student: Student model instance
            encoding: Face encoding array
        """
        try:
            face_db = FaceRecognitionDB(self.face_db_path)
            
            # Check if student already exists
            existing = face_db.get_student(student.student_id)
            
            if existing:
                # Update existing student
                face_db.update_student(
                    student.student_id,
                    name=student.name,
                    face_encoding=encoding,
                    active=student.is_active
                )
                logger.info(f"✅ Updated face DB for {student.student_id}")
            else:
                # Add new student
                face_db.add_student(
                    student_id=student.student_id,
                    name=student.name,
                    class_name=student.email or "N/A",  # Use email as class placeholder
                    face_encoding=encoding,
                    photos_count=1
                )
                logger.info(f"✅ Added to face DB: {student.student_id}")
            
            face_db.close()
            
        except Exception as e:
            logger.error(f"❌ Face DB sync failed: {e}")
    
    def validate_face_encoding(self, student_id: int) -> Tuple[bool, str]:
        """
        Validate that a student's face encoding is properly stored
        
        Args:
            student_id: Student database ID (primary key)
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, "Student not found"
            
            if not student.face_encoding:
                return False, "No face encoding found"
            
            # Try to load encoding
            encoding = pickle.loads(student.face_encoding)
            
            if not isinstance(encoding, np.ndarray):
                return False, "Invalid encoding format"
            
            if encoding.shape != (512,):
                return False, f"Invalid encoding shape: {encoding.shape}, expected (512,)"
            
            if encoding.dtype != np.float32:
                return False, f"Invalid encoding dtype: {encoding.dtype}, expected float32"
            
            return True, "Face encoding is valid"
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False, f"Validation error: {str(e)}"
    
    def close(self):
        """Clean up resources"""
        # Enrollment system handles its own cleanup
        logger.info("✅ Face Recognition Service closed")


# Factory function for dependency injection
def get_face_recognition_service(db: Session) -> FaceRecognitionService:
    """
    Get a face recognition service instance
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        FaceRecognitionService instance
    """
    return FaceRecognitionService(db)
