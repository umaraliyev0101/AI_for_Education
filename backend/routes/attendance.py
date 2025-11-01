"""
Attendance Management Routes
Face recognition attendance tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models.attendance import Attendance
from backend.models.student import Student
from backend.models.lesson import Lesson
from backend.models.user import User
from backend.schemas.attendance import AttendanceCreate, AttendanceResponse
from backend.dependencies import require_teacher, get_current_user

router = APIRouter()


@router.get("/", response_model=List[AttendanceResponse])
async def list_attendance(
    skip: int = 0,
    limit: int = 100,
    lesson_id: Optional[int] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List attendance records with filtering
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        lesson_id: Filter by lesson ID
        student_id: Filter by student ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of attendance records
    """
    query = db.query(Attendance).order_by(Attendance.timestamp.desc())
    
    if lesson_id:
        query = query.filter(Attendance.lesson_id == lesson_id)
    
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    
    attendance_records = query.offset(skip).limit(limit).all()
    return attendance_records


@router.get("/lesson/{lesson_id}", response_model=List[AttendanceResponse])
async def get_lesson_attendance(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all attendance records for a specific lesson
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of attendance records for the lesson
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    attendance_records = db.query(Attendance).filter(
        Attendance.lesson_id == lesson_id
    ).order_by(Attendance.timestamp).all()
    
    return attendance_records


@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
async def get_student_attendance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all attendance records for a specific student
    
    Args:
        student_id: Student database ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of attendance records for the student
    """
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    attendance_records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(Attendance.timestamp.desc()).all()
    
    return attendance_records


@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Mark attendance manually (Teacher or Admin)
    
    Args:
        attendance_data: Attendance data
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Created attendance record
    """
    # Verify student exists
    student = db.query(Student).filter(Student.id == attendance_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {attendance_data.student_id} not found"
        )
    
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == attendance_data.lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {attendance_data.lesson_id} not found"
        )
    
    # Check if attendance already marked
    existing_attendance = db.query(Attendance).filter(
        Attendance.student_id == attendance_data.student_id,
        Attendance.lesson_id == attendance_data.lesson_id
    ).first()
    
    if existing_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance already marked for this student in this lesson"
        )
    
    # Create attendance record
    new_attendance = Attendance(
        student_id=attendance_data.student_id,
        lesson_id=attendance_data.lesson_id,
        recognition_confidence=attendance_data.recognition_confidence,
        entry_method=attendance_data.entry_method,
        notes=attendance_data.notes
    )
    
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    
    return new_attendance


@router.post("/scan", response_model=AttendanceResponse)
async def scan_face_attendance(
    lesson_id: int = Query(..., description="Lesson ID for attendance"),
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Scan face for attendance (Face Recognition)
    
    Args:
        lesson_id: Lesson database ID (query parameter)
        face_image: Face image from camera
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Created attendance record with student info
    """
    import cv2
    import numpy as np
    from face_recognition.face_attendance import FaceRecognitionAttendance
    from backend.config import settings
    import os
    
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Validate file type - add null check
    if not face_image.content_type or not face_image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # Read image file
        image_bytes = await face_image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        # Initialize face recognition system
        face_recognition_system = FaceRecognitionAttendance(
            db_path=os.path.join(settings.UPLOAD_DIR, "attendance.db")
        )
        
        # Process frame for face recognition
        annotated_frame, recognized = face_recognition_system.process_frame(
            frame,
            mark_attendance=False  # We'll mark manually
        )
        
        if not recognized:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No face recognized or student not enrolled"
            )
        
        # Get first recognized student
        student_info = recognized[0]
        student_id_str = student_info['student_id']
        confidence = student_info['confidence']
        
        # Find student in database by student_id (assuming it's stored as a string)
        student = db.query(Student).filter(Student.student_id == student_id_str).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id_str} not found in database"
            )
        
        # Check if attendance already marked
        existing_attendance = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.lesson_id == lesson_id
        ).first()
        
        if existing_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance already marked for this student in this lesson"
            )
        
        # Create attendance record
        new_attendance = Attendance(
            student_id=student.id,
            lesson_id=lesson_id,
            recognition_confidence=confidence,
            entry_method="face_recognition",
            notes=f"Recognized with {confidence:.2%} confidence"
        )
        
        db.add(new_attendance)
        db.commit()
        db.refresh(new_attendance)
        
        # Clean up
        face_recognition_system.close()
        
        return new_attendance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Face recognition failed: {str(e)}"
        )


@router.post("/auto-scan/{lesson_id}")
async def auto_scan_attendance(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Auto-scan attendance when teacher logs in using webcam
    This endpoint triggers automatic attendance taking
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        List of recognized students with photos
    """
    from face_recognition.face_attendance import FaceRecognitionAttendance
    from backend.config import settings
    import os
    import cv2
    import base64
    
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    try:
        # Initialize face recognition
        face_recognition_system = FaceRecognitionAttendance(
            db_path=os.path.join(settings.UPLOAD_DIR, "attendance.db")
        )
        
        # Open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot access camera"
            )
        
        recognized_students = []
        max_attempts = 100  # Try for ~5 seconds (at 20 fps)
        attempt = 0
        
        while attempt < max_attempts and len(recognized_students) < 10:  # Scan up to 10 students
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            _, recognized = face_recognition_system.process_frame(frame, mark_attendance=False)
            
            for student_info in recognized:
                student_id_str = student_info['student_id']
                
                # Check if already recognized
                if any(s['student_id'] == student_id_str for s in recognized_students):
                    continue
                
                # Find student in database
                student = db.query(Student).filter(Student.student_id == student_id_str).first()
                if not student:
                    continue
                
                # Check if attendance already marked
                existing = db.query(Attendance).filter(
                    Attendance.student_id == student.id,
                    Attendance.lesson_id == lesson_id
                ).first()
                
                if not existing:
                    # Mark attendance
                    new_attendance = Attendance(
                        student_id=student.id,
                        lesson_id=lesson_id,
                        recognition_confidence=student_info['confidence'],
                        entry_method="face_recognition_auto",
                        notes=f"Auto-recognized with {student_info['confidence']:.2%} confidence"
                    )
                    db.add(new_attendance)
                    db.commit()
                
                # Encode student photo (use face_image_path from Student model)
                photo_base64 = None
                if hasattr(student, 'face_image_path'):
                    img_path = student.face_image_path
                    if img_path is not None and os.path.exists(str(img_path)):
                        with open(str(img_path), 'rb') as f:
                            photo_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                recognized_students.append({
                    'student_id': student.student_id,
                    'id': student.id,
                    'name': student.name,
                    'photo_base64': photo_base64,
                    'confidence': student_info['confidence']
                })
            
            attempt += 1
        
        cap.release()
        face_recognition_system.close()
        
        return {
            "lesson_id": lesson_id,
            "recognized_count": len(recognized_students),
            "students": recognized_students
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-scan failed: {str(e)}"
        )


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Delete an attendance record (Teacher or Admin)
    
    Args:
        attendance_id: Attendance record ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        No content
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )
    
    db.delete(attendance)
    db.commit()
    
    return None
