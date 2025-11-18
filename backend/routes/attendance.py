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
    
    # Add student names to response
    response_data = []
    for record in attendance_records:
        record_dict = record.__dict__.copy()
        student = db.query(Student).filter(Student.id == record.student_id).first()
        record_dict['student_name'] = student.name if student else None
        response_data.append(record_dict)
    
    return response_data


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
    
    # Add student names to response
    response_data = []
    for record in attendance_records:
        record_dict = record.__dict__.copy()
        student = db.query(Student).filter(Student.id == record.student_id).first()
        record_dict['student_name'] = student.name if student else None
        response_data.append(record_dict)
    
    return response_data


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
    
    # Add student names to response (though all will be the same student)
    response_data = []
    for record in attendance_records:
        record_dict = record.__dict__.copy()
        record_dict['student_name'] = student.name
        response_data.append(record_dict)
    
    return response_data


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
    
    # Add student name to response
    response_data = new_attendance.__dict__.copy()
    response_data['student_name'] = student.name
    
    return response_data


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
        
        # Add student name to response
        response_data = new_attendance.__dict__.copy()
        response_data['student_name'] = student.name
        
        return response_data
        
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
    max_duration_minutes: int = Query(30, description="Maximum scan duration in minutes", ge=1, le=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Auto-scan attendance until lesson starts
    Scans continuously from now until lesson start time (or max duration)
    
    Args:
        lesson_id: Lesson database ID
        max_duration_minutes: Safety limit in minutes (1-120)
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        List of recognized students with photos
    """
    from datetime import datetime, timedelta
    from face_recognition.face_attendance import FaceRecognitionAttendance
    from backend.config import settings
    import os
    import cv2
    import base64
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Calculate scan duration based on lesson start time
    current_time = datetime.now()
    
    # Combine date and start_time for full datetime
    if lesson.start_time is not None:
        lesson_start = lesson.start_time
    else:
        # Fallback: assume lesson starts at the date specified
        lesson_start = lesson.date
    
    # Calculate time until lesson starts
    time_until_start = lesson_start - current_time
    time_until_start_seconds = max(0, int(time_until_start.total_seconds()))
    
    # If lesson already started, scan for 5 minutes or until max_duration
    if time_until_start_seconds <= 0:
        scan_duration_seconds = min(300, max_duration_minutes * 60)  # 5 min or max_duration
        scan_reason = "lesson_already_started"
    else:
        # Scan until lesson starts, but not longer than max_duration
        scan_duration_seconds = min(time_until_start_seconds, max_duration_minutes * 60)
        scan_reason = "until_lesson_start"
    
    logger.info(f"Auto-scan: {scan_duration_seconds}s ({scan_reason}), lesson starts at {lesson_start}")
    
    try:
        # Initialize face recognition
        face_recognition_system = FaceRecognitionAttendance(
            db_path=os.path.join(settings.UPLOAD_DIR, "attendance.db")
        )
        
        # Open camera
        cap = cv2.VideoCapture(1) # Uses camera index from settings
        if not cap.isOpened():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot access camera"
            )
        
        recognized_students = []
        max_attempts = scan_duration_seconds * 20  # Assuming 20 fps
        attempt = 0
        scan_start_time = datetime.now()
        
        logger.info(f"Starting auto-scan: {scan_duration_seconds}s duration, max {max_attempts} frames")
        
        while attempt < max_attempts:
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
                face_image_path = getattr(student, 'face_image_path', None)
                if face_image_path and os.path.exists(str(face_image_path)):
                    try:
                        with open(str(face_image_path), 'rb') as f:
                            photo_base64 = base64.b64encode(f.read()).decode('utf-8')
                    except Exception:
                        photo_base64 = None
                
                recognized_students.append({
                    'student_id': student.student_id,
                    'id': student.id,
                    'name': student.name,
                    'photo_base64': photo_base64,
                    'confidence': student_info['confidence']
                })
                
                logger.info(f"Recognized: {student.name} ({len(recognized_students)} total)")
            
            attempt += 1
            
            # Progress logging every 100 frames
            if attempt % 100 == 0:
                elapsed = (datetime.now() - scan_start_time).total_seconds()
                logger.info(f"Scan progress: {elapsed:.1f}s elapsed, {len(recognized_students)} students recognized")
        
        scan_end_time = datetime.now()
        total_scan_time = (scan_end_time - scan_start_time).total_seconds()
        
        cap.release()
        face_recognition_system.close()
        
        logger.info(f"Auto-scan completed: {total_scan_time:.1f}s, {len(recognized_students)} students")
        
        return {
            "lesson_id": lesson_id,
            "recognized_count": len(recognized_students),
            "students": recognized_students,
            "scan_duration_seconds": total_scan_time,
            "scan_reason": scan_reason,
            "lesson_start_time": lesson_start.isoformat() if lesson_start is not None else None
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
