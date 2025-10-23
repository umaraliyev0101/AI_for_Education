#!/usr/bin/env python3
"""
Face Recognition Enrollment System
==================================

Student enrollment with FaceNet face recognition.
"""

import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
from typing import List, Optional, Tuple
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceEnrollmentSystem:
    """Handles student enrollment with face recognition"""

    def __init__(self, device: str = "auto"):
        """Initialize face detection and recognition models"""
        
        # Set device
        if device == "auto":
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        logger.info(f"Using device: {self.device}")
        
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=self.device,
            keep_all=False  # Only detect one face
        )
        
        # Initialize FaceNet for face recognition
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        logger.info("✅ Face recognition models loaded")

    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect face in image
        
        Args:
            image: BGR image from OpenCV
            
        Returns:
            Cropped and aligned face image, or None if no face detected
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Detect and align face
            face = self.mtcnn(pil_image)
            
            if face is not None:
                return face
            
            logger.warning("⚠️ No face detected")
            return None
            
        except Exception as e:
            logger.error(f"❌ Face detection failed: {e}")
            return None

    def generate_encoding(self, face_tensor: torch.Tensor) -> np.ndarray:
        """
        Generate face encoding from face tensor
        
        Args:
            face_tensor: Aligned face tensor from MTCNN
            
        Returns:
            512-dimensional face encoding
        """
        try:
            with torch.no_grad():
                # Add batch dimension if needed
                if face_tensor.dim() == 3:
                    face_tensor = face_tensor.unsqueeze(0)
                
                # Move to device
                face_tensor = face_tensor.to(self.device)
                
                # Generate encoding
                encoding = self.resnet(face_tensor)
                
                # Convert to numpy and normalize
                encoding = encoding.cpu().numpy().flatten()
                encoding = encoding / np.linalg.norm(encoding)
                
                return encoding.astype(np.float32)
                
        except Exception as e:
            logger.error(f"❌ Encoding generation failed: {e}")
            return None

    def enroll_from_camera(self, num_photos: int = 5, camera_id: int = 0) -> List[np.ndarray]:
        """
        Enroll student using webcam
        
        Args:
            num_photos: Number of photos to capture
            camera_id: Camera device ID
            
        Returns:
            List of face encodings
        """
        encodings = []
        
        try:
            cap = cv2.VideoCapture(camera_id)
            
            if not cap.isOpened():
                logger.error("❌ Cannot open camera")
                return []
            
            logger.info(f"📸 Capturing {num_photos} photos for enrollment...")
            logger.info("Press SPACE to capture, ESC to cancel")
            
            captured = 0
            
            while captured < num_photos:
                ret, frame = cap.read()
                
                if not ret:
                    logger.error("❌ Failed to read frame")
                    break
                
                # Display frame
                display_frame = frame.copy()
                cv2.putText(
                    display_frame,
                    f"Captured: {captured}/{num_photos}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    display_frame,
                    "Press SPACE to capture",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                
                cv2.imshow('Enrollment', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC
                    logger.info("❌ Enrollment cancelled")
                    break
                elif key == 32:  # SPACE
                    # Detect face
                    face = self.detect_face(frame)
                    
                    if face is not None:
                        # Generate encoding
                        encoding = self.generate_encoding(face)
                        
                        if encoding is not None:
                            encodings.append(encoding)
                            captured += 1
                            logger.info(f"✅ Captured photo {captured}/{num_photos}")
                        else:
                            logger.warning("⚠️ Failed to generate encoding")
                    else:
                        logger.warning("⚠️ No face detected, try again")
            
            cap.release()
            cv2.destroyAllWindows()
            
            return encodings
            
        except Exception as e:
            logger.error(f"❌ Camera enrollment failed: {e}")
            return []

    def enroll_from_images(self, image_paths: List[str]) -> List[np.ndarray]:
        """
        Enroll student from image files
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            List of face encodings
        """
        encodings = []
        
        for image_path in image_paths:
            try:
                # Read image
                image = cv2.imread(image_path)
                
                if image is None:
                    logger.warning(f"⚠️ Cannot read image: {image_path}")
                    continue
                
                # Detect face
                face = self.detect_face(image)
                
                if face is not None:
                    # Generate encoding
                    encoding = self.generate_encoding(face)
                    
                    if encoding is not None:
                        encodings.append(encoding)
                        logger.info(f"✅ Processed: {image_path}")
                    else:
                        logger.warning(f"⚠️ Encoding failed: {image_path}")
                else:
                    logger.warning(f"⚠️ No face in: {image_path}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to process {image_path}: {e}")
        
        return encodings

    def average_encodings(self, encodings: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Average multiple face encodings for more robust recognition
        
        Args:
            encodings: List of face encodings
            
        Returns:
            Averaged encoding
        """
        if not encodings:
            return None
        
        try:
            # Stack and average
            stacked = np.vstack(encodings)
            averaged = np.mean(stacked, axis=0)
            
            # Normalize
            averaged = averaged / np.linalg.norm(averaged)
            
            return averaged.astype(np.float32)
            
        except Exception as e:
            logger.error(f"❌ Averaging failed: {e}")
            return None

    def enroll_student_interactive(self) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[np.ndarray]]:
        """
        Interactive enrollment process
        
        Returns:
            Tuple of (student_id, name, class_name, face_encoding)
        """
        print("\n" + "="*50)
        print("👤 STUDENT ENROLLMENT")
        print("="*50)
        
        # Get student information
        student_id = input("Enter Student ID: ").strip()
        if not student_id:
            print("❌ Invalid student ID")
            return None, None, None, None
        
        name = input("Enter Student Name: ").strip()
        if not name:
            print("❌ Invalid name")
            return None, None, None, None
        
        class_name = input("Enter Class/Grade: ").strip()
        if not class_name:
            print("❌ Invalid class name")
            return None, None, None, None
        
        # Choose enrollment method
        print("\nEnrollment method:")
        print("1. Webcam (recommended)")
        print("2. Image files")
        
        choice = input("Choose method (1 or 2): ").strip()
        
        encodings = []
        
        if choice == "1":
            # Webcam enrollment
            num_photos = 5
            encodings = self.enroll_from_camera(num_photos)
        elif choice == "2":
            # Image file enrollment
            print("\nEnter image file paths (one per line, empty line to finish):")
            image_paths = []
            while True:
                path = input("Image path: ").strip()
                if not path:
                    break
                if Path(path).exists():
                    image_paths.append(path)
                else:
                    print(f"⚠️ File not found: {path}")
            
            if image_paths:
                encodings = self.enroll_from_images(image_paths)
        else:
            print("❌ Invalid choice")
            return None, None, None, None
        
        # Check if we got any encodings
        if not encodings:
            print("❌ No valid face encodings captured")
            return None, None, None, None
        
        # Average encodings
        final_encoding = self.average_encodings(encodings)
        
        if final_encoding is None:
            print("❌ Failed to create final encoding")
            return None, None, None, None
        
        print(f"✅ Enrollment successful! Captured {len(encodings)} face samples")
        
        return student_id, name, class_name, final_encoding


def test_enrollment():
    """Test enrollment system"""
    print("🧪 Testing Face Enrollment System...")
    
    enrollment = FaceEnrollmentSystem()
    
    # Test with dummy data
    print("✅ Enrollment system initialized")
    
    # In real usage, you would call:
    # student_id, name, class_name, encoding = enrollment.enroll_student_interactive()


if __name__ == "__main__":
    test_enrollment()
