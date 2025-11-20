"""
Attendance Management Routes
Face recognition attendance tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime
from backend.database import get_db
from backend.models.attendance import Attendance
from backend.models.student import Student
from backend.models.lesson import Lesson
from backend.models.user import User
from backend.schemas.attendance import AttendanceCreate, AttendanceResponse
from backend.dependencies import require_teacher, get_current_user

router = APIRouter()


def get_student_photo_base64(student: Student) -> Optional[str]:
    """
    Get student's photo as base64 string for display in frontend
    
    Args:
        student: Student model instance
        
    Returns:
        Base64 encoded image string or None if no image available
    """
    import os
    import base64
    
    if not student:
        return None
    
    face_image_path = getattr(student, 'face_image_path', None)
    if not face_image_path:
        return None
    
    try:
        face_image_path_str = str(face_image_path)
        if os.path.exists(face_image_path_str):
            with open(face_image_path_str, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        pass
    
    return None


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
    
    # Add student names and photos to response
    response_data = []
    for record in attendance_records:
        record_dict = record.__dict__.copy()
        student = db.query(Student).filter(Student.id == record.student_id).first()
        record_dict['student_name'] = student.name if student else None
        record_dict['student_photo_base64'] = get_student_photo_base64(student)
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
    
    # Add student names and photos to response
    response_data = []
    for record in attendance_records:
        record_dict = record.__dict__.copy()
        student = db.query(Student).filter(Student.id == record.student_id).first()
        record_dict['student_name'] = student.name if student else None
        record_dict['student_photo_base64'] = get_student_photo_base64(student)
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
    
    # Add student names and photos to response (though all will be the same student)
    response_data = []
    for record in attendance_records:
        record_dict = record.__dict__.copy()
        record_dict['student_name'] = student.name
        record_dict['student_photo_base64'] = get_student_photo_base64(student)
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
    
    # Add student name and photo to response
    response_data = new_attendance.__dict__.copy()
    response_data['student_name'] = student.name
    response_data['student_photo_base64'] = get_student_photo_base64(student)
    
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
        
        # Add student name and photo to response
        response_data = new_attendance.__dict__.copy()
        response_data['student_name'] = student.name
        response_data['student_photo_base64'] = get_student_photo_base64(student)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Face recognition failed: {str(e)}"
        )


async def run_auto_scan_background(lesson_id: int, scan_duration_seconds: int, lesson_start: Any):
    """
    Background task for auto-scanning attendance
    """
    import asyncio
    from datetime import datetime, timedelta
    from face_recognition.face_attendance import FaceRecognitionAttendance
    from backend.config import settings
    from backend.database import get_db
    import os
    import cv2
    import base64
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Create our own database session for this background task
    db = next(get_db())
    
    try:
        # Initialize face recognition
        face_recognition_system = FaceRecognitionAttendance(
            db_path=os.path.join(settings.UPLOAD_DIR, "attendance.db")
        )
        
        # Open camera
        camera_index = 0  # Default camera index
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            logger.error(f"Cannot access camera for auto-scan of lesson {lesson_id}")
            return
        
        # Get camera information
        camera_name = f"Camera {camera_index}"
        try:
            # Try to get camera backend information
            backend = cap.get(cv2.CAP_PROP_BACKEND)
            if backend:
                backend_name = {
                    cv2.CAP_DSHOW: "DirectShow",
                    cv2.CAP_MSMF: "Media Foundation",
                    cv2.CAP_V4L2: "V4L2",
                    cv2.CAP_AVFOUNDATION: "AVFoundation",
                    cv2.CAP_GSTREAMER: "GStreamer",
                    cv2.CAP_FFMPEG: "FFMPEG",
                    cv2.CAP_IMAGES: "Images",
                    cv2.CAP_OPENCV_MJPEG: "OpenCV MJPEG"
                }.get(int(backend), f"Unknown ({backend})")
                camera_name = f"Camera {camera_index} ({backend_name})"
            
            # Try to get camera resolution
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if width > 0 and height > 0:
                camera_name += f" - {width}x{height}"
                
        except Exception:
            # If we can't get camera info, just use the index
            pass
        
        logger.info(f"Using camera: {camera_name} for auto-scan of lesson {lesson_id}")
        
        recognized_students = []
        scan_start_time = datetime.now()
        scan_end_time_target = scan_start_time + timedelta(seconds=scan_duration_seconds)
        
        logger.info(f"Starting background auto-scan: {scan_duration_seconds}s duration until {scan_end_time_target}, using {camera_name}")
        
        while datetime.now() < scan_end_time_target:
            # Check if lesson has started (stop 1 second before)
            current_time_check = datetime.now()
            time_until_start_check = lesson_start - current_time_check
            if time_until_start_check.total_seconds() <= 1:
                logger.info("Lesson starting within 1 second, stopping auto-scan")
                break
            
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)  # Wait a bit before retrying
                continue
            
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
            
            # Yield control to event loop every frame
            await asyncio.sleep(0.05)  # ~20 fps target
            
            # Progress logging every 2 seconds
            elapsed = (datetime.now() - scan_start_time).total_seconds()
            if int(elapsed) % 2 == 0 and int(elapsed) > 0:
                remaining = max(0, scan_duration_seconds - elapsed)
                logger.info(f"Scan progress: {elapsed:.1f}s elapsed, {remaining:.1f}s remaining, {len(recognized_students)} students recognized")
        
        scan_end_time = datetime.now()
        total_scan_time = (scan_end_time - scan_start_time).total_seconds()
        
        cap.release()
        face_recognition_system.close()
        
        logger.info(f"Auto-scan completed: {total_scan_time:.1f}s, {len(recognized_students)} students using {camera_name}")
        
    except Exception as e:
        logger.error(f"Auto-scan background task failed for lesson {lesson_id}: {str(e)}")
    finally:
        # Always close the database session
        try:
            db.close()
        except Exception:
            pass


@router.post("/auto-scan/{lesson_id}")
async def auto_scan_attendance(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Auto-scan attendance until 1 second before lesson starts
    Scans continuously from now until 1 second before lesson start time
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Confirmation that scan has started
    """
    import asyncio
    from datetime import datetime
    
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Calculate scan duration based on lesson scheduled time
    current_time = datetime.now()
    
    # Use the scheduled date as the lesson start time for autoscan
    # (not the manual start_time which is only set when lesson is actually started)
    lesson_start = lesson.date
    
    # Calculate time until lesson starts
    time_until_start = lesson_start - current_time
    time_until_start_seconds = max(0, int(time_until_start.total_seconds()))
    
    # If lesson already started (based on scheduled time), don't scan
    if time_until_start_seconds <= 1:
        return {
            "lesson_id": lesson_id,
            "recognized_count": 0,
            "students": [],
            "scan_duration_seconds": 0,
            "scan_reason": "lesson_already_started",
            "lesson_start_time": lesson_start.isoformat() if lesson_start is not None else None
        }
    
    # Scan until 1 second before lesson starts
    scan_duration_seconds = time_until_start_seconds - 1
    scan_reason = "until_1_second_before_lesson_start"
    
    # Start background scanning task
    asyncio.create_task(run_auto_scan_background(
        lesson_id, scan_duration_seconds, lesson.date
    ))
    
    # Return immediately with scan started confirmation
    return {
        "lesson_id": lesson_id,
        "status": "scan_started",
        "scan_duration_seconds": scan_duration_seconds,
        "scan_reason": scan_reason,
        "lesson_start_time": lesson_start.isoformat() if lesson_start is not None else None,
        "message": f"Auto-scan started and will run for {scan_duration_seconds} seconds until 1 second before lesson starts"
    }


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
