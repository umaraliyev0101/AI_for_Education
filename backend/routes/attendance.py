"""
Attendance Management Routes
Face recognition attendance tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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
    lesson_id: int,
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Scan face for attendance (Face Recognition)
    
    Args:
        lesson_id: Lesson database ID
        face_image: Face image from camera
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Created attendance record
        
    Note:
        This is a placeholder. Actual face recognition will be integrated
        with the face_recognition service.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Validate file type
    if not face_image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # TODO: Integrate face recognition service here
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Face recognition service integration pending"
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
