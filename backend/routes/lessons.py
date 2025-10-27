"""
Lesson Management Routes
CRUD operations for lessons
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models.lesson import Lesson, LessonStatus
from backend.models.user import User
from backend.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse
from backend.dependencies import require_teacher, get_current_user
from backend.config import settings
import os

router = APIRouter()


@router.get("/", response_model=List[LessonResponse])
async def list_lessons(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[LessonStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all lessons with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by lesson status
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of lessons
    """
    query = db.query(Lesson).order_by(Lesson.date.desc())
    
    if status_filter:
        query = query.filter(Lesson.status == status_filter)
    
    lessons = query.offset(skip).limit(limit).all()
    return lessons


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get lesson by ID
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Lesson information
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    return lesson


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Create a new lesson (Teacher or Admin)
    
    Args:
        lesson_data: Lesson creation data
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Created lesson information
    """
    
    new_lesson = Lesson(
        title=lesson_data.title,
        description=lesson_data.description,
        date=lesson_data.date,
        duration_minutes=lesson_data.duration_minutes,
        subject=lesson_data.subject,
        notes=lesson_data.notes,
        status=LessonStatus.SCHEDULED
    )
    
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    
    return new_lesson


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Update lesson information (Teacher or Admin)
    
    Args:
        lesson_id: Lesson database ID
        lesson_data: Updated lesson data
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Updated lesson information
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Update fields if provided
    update_data = lesson_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(lesson, field, value)
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Delete a lesson (Teacher or Admin)
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        No content
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    db.delete(lesson)
    db.commit()
    
    return None


@router.post("/{lesson_id}/start", response_model=LessonResponse)
async def start_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Start a lesson (Teacher or Admin)
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Updated lesson with IN_PROGRESS status
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    if lesson.status != LessonStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start lesson with status: {lesson.status}"
        )
    
    lesson.status = LessonStatus.IN_PROGRESS
    lesson.start_time = datetime.now()
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.post("/{lesson_id}/end", response_model=LessonResponse)
async def end_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    End a lesson (Teacher or Admin)
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Updated lesson with COMPLETED status
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    if lesson.status != LessonStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot end lesson with status: {lesson.status}"
        )
    
    lesson.status = LessonStatus.COMPLETED
    lesson.end_time = datetime.now()
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.post("/{lesson_id}/upload-materials")
async def upload_lesson_materials(
    lesson_id: int,
    materials_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Upload lesson materials (PDF, PPTX, DOCX, TXT)
    
    Args:
        lesson_id: Lesson database ID
        materials_file: Materials file
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Success message with file path
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Validate file type
    allowed_extensions = [".pdf", ".pptx", ".docx", ".txt"]
    file_ext = os.path.splitext(materials_file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save materials file
    filename = f"lesson_{lesson_id}_materials{file_ext}"
    file_path = os.path.join(settings.MATERIALS_DIR, filename)
    
    with open(file_path, "wb") as f:
        content = await materials_file.read()
        f.write(content)
    
    lesson.materials_path = file_path
    
    db.commit()
    
    return {
        "message": "Materials uploaded successfully",
        "file_path": file_path,
        "lesson_id": lesson_id
    }


@router.post("/{lesson_id}/upload-presentation")
async def upload_lesson_presentation(
    lesson_id: int,
    presentation_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Upload lesson presentation (PPTX, PDF)
    
    Args:
        lesson_id: Lesson database ID
        presentation_file: Presentation file
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Success message with file path
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Validate file type
    allowed_extensions = [".pptx", ".pdf"]
    file_ext = os.path.splitext(presentation_file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save presentation file
    filename = f"lesson_{lesson_id}_presentation{file_ext}"
    file_path = os.path.join(settings.PRESENTATIONS_DIR, filename)
    
    with open(file_path, "wb") as f:
        content = await presentation_file.read()
        f.write(content)
    
    lesson.presentation_path = file_path
    
    db.commit()
    
    return {
        "message": "Presentation uploaded successfully",
        "file_path": file_path,
        "lesson_id": lesson_id
    }
