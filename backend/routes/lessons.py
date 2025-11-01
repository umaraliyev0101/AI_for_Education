"""
Lesson Management Routes
CRUD operations for lessons
"""
import os
import shutil
import glob
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
    Delete a lesson and all associated files (Teacher or Admin)
    
    This will delete:
    - Presentation files (PPTX/PDF)
    - Slide images
    - Audio files (TTS for slides and Q&A recordings)
    - Materials files
    - Vector stores
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        No content
    """
    from backend.models.qa_session import QASession
    
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Delete all associated files before deleting the lesson record
    files_deleted = []
    errors = []
    
    try:
        # 1. Delete presentation files (PPTX/PDF)
        presentations_dir = os.path.abspath(settings.PRESENTATIONS_DIR)
        presentation_patterns = [
            os.path.join(presentations_dir, f"lesson_{lesson_id}_presentation.*")
        ]
        for pattern in presentation_patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        files_deleted.append(file_path)
                except Exception as e:
                    errors.append(f"Failed to delete {file_path}: {str(e)}")
        
        # 2. Delete slide images directory
        slides_dir = os.path.join(os.path.abspath(settings.UPLOAD_DIR), "slides", f"lesson_{lesson_id}")
        if os.path.exists(slides_dir):
            try:
                shutil.rmtree(slides_dir)
                files_deleted.append(f"{slides_dir}/ (directory)")
            except Exception as e:
                errors.append(f"Failed to delete slides directory {slides_dir}: {str(e)}")
        
        # 3. Delete audio files directory (TTS for slides)
        audio_presentations_dir = os.path.join(os.path.abspath(settings.AUDIO_DIR), "presentations", f"lesson_{lesson_id}")
        if os.path.exists(audio_presentations_dir):
            try:
                shutil.rmtree(audio_presentations_dir)
                files_deleted.append(f"{audio_presentations_dir}/ (directory)")
            except Exception as e:
                errors.append(f"Failed to delete audio directory {audio_presentations_dir}: {str(e)}")
        
        # 4. Delete materials files
        materials_dir = os.path.abspath(settings.MATERIALS_DIR)
        materials_patterns = [
            os.path.join(materials_dir, f"lesson_{lesson_id}_materials.*")
        ]
        for pattern in materials_patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        files_deleted.append(file_path)
                except Exception as e:
                    errors.append(f"Failed to delete {file_path}: {str(e)}")
        
        # 5. Delete vector stores
        vector_stores_dir = os.path.abspath(settings.VECTOR_STORES_DIR)
        lesson_vector_store = os.path.join(vector_stores_dir, "lesson_materials", str(lesson_id))
        if os.path.exists(lesson_vector_store):
            try:
                shutil.rmtree(lesson_vector_store)
                files_deleted.append(f"{lesson_vector_store}/ (directory)")
            except Exception as e:
                errors.append(f"Failed to delete vector store {lesson_vector_store}: {str(e)}")
        
        # 6. Delete Q&A audio recordings associated with this lesson
        qa_sessions = db.query(QASession).filter(QASession.lesson_id == lesson_id).all()
        audio_dir = os.path.abspath(settings.AUDIO_DIR)
        for qa in qa_sessions:
            # Delete question audio
            question_audio_pattern = os.path.join(audio_dir, f"question_{qa.id}_question.*")
            for file_path in glob.glob(question_audio_pattern):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        files_deleted.append(file_path)
                except Exception as e:
                    errors.append(f"Failed to delete {file_path}: {str(e)}")
            
            # Delete answer audio if exists
            answer_audio_pattern = os.path.join(audio_dir, f"question_{qa.id}_answer.*")
            for file_path in glob.glob(answer_audio_pattern):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        files_deleted.append(file_path)
                except Exception as e:
                    errors.append(f"Failed to delete {file_path}: {str(e)}")
        
    except Exception as e:
        # Log the error but continue with database deletion
        errors.append(f"Unexpected error during file cleanup: {str(e)}")
    
    # Delete the lesson from database (cascade will delete related records)
    db.delete(lesson)
    db.commit()
    
    # Log the cleanup results
    if files_deleted:
        print(f"✅ Deleted {len(files_deleted)} files/directories for lesson {lesson_id}")
    if errors:
        print(f"⚠️  Encountered {len(errors)} errors during cleanup:")
        for error in errors:
            print(f"   - {error}")
    
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


@router.post("/{lesson_id}/presentation")
async def upload_presentation(
    lesson_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Upload lesson presentation (PPTX, PDF) - Main endpoint
    
    Args:
        lesson_id: Lesson database ID
        file: Presentation file (PPTX or PDF)
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Success message with filename
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Validate file type
    if not file.filename.endswith(('.pptx', '.pdf')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PPTX and PDF files are supported"
        )
    
    # ✅ FIX: Use absolute path with os.path.join properly
    presentations_dir = os.path.abspath(settings.PRESENTATIONS_DIR)
    os.makedirs(presentations_dir, exist_ok=True)
    
    # Save presentation file
    file_ext = os.path.splitext(file.filename)[1].lower()
    filename = f"lesson_{lesson_id}_presentation{file_ext}"
    file_path = os.path.join(presentations_dir, filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Store absolute path in database
    lesson.presentation_path = os.path.abspath(file_path)
    
    db.commit()
    
    return {
        "message": "Presentation uploaded successfully",
        "filename": filename,
        "lesson_id": lesson_id,
        "file_path": lesson.presentation_path
    }


@router.post("/{lesson_id}/upload-presentation")
async def upload_lesson_presentation(
    lesson_id: int,
    presentation_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Upload lesson presentation (PPTX, PDF) - Legacy endpoint (alias)
    
    Args:
        lesson_id: Lesson database ID
        presentation_file: Presentation file
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Success message with file path
    """
    # Call the main endpoint
    return await upload_presentation(lesson_id, presentation_file, db, current_user)


@router.post("/{lesson_id}/presentation/process")
async def process_presentation_endpoint(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Process presentation and generate slide images + audio
    Sends real-time progress updates via WebSocket
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Processing status and presentation data
    """
    from backend.services.presentation_service import PresentationService
    from backend.routes.websocket import manager
    
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # ✅ FIX: Get absolute path and check existence properly
    presentation_path = lesson.presentation_path
    if not presentation_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No presentation uploaded for this lesson"
        )
    
    # Convert to absolute path if relative
    if not os.path.isabs(presentation_path):
        presentation_path = os.path.abspath(presentation_path)
    
    if not os.path.exists(presentation_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Presentation file not found: {presentation_path}"
        )
    
    # ✅ NEW: Send processing started message via WebSocket
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "presentation_processing_started",
        "lesson_id": lesson_id,
        "message": "Processing presentation...",
        "timestamp": datetime.now().isoformat()
    })
    
    presentation_service = PresentationService()
    
    try:
        # Process with progress callback
        presentation_data = await presentation_service.process_presentation_with_progress(
            presentation_path,
            lesson_id,
            progress_callback=lambda current, total, slide_text: 
                manager.broadcast_to_lesson(lesson_id, {
                    "type": "presentation_processing_progress",
                    "lesson_id": lesson_id,
                    "current_slide": current,
                    "total_slides": total,
                    "slide_text": slide_text[:50] + "..." if len(slide_text) > 50 else slide_text,
                    "progress_percent": int((current / total) * 100),
                    "timestamp": datetime.now().isoformat()
                })
        )
        
        if not presentation_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process presentation"
            )
        
        # ✅ NEW: Send processing completed message
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "presentation_processing_completed",
            "lesson_id": lesson_id,
            "total_slides": presentation_data['total_slides'],
            "message": "Presentation ready!",
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "message": "Presentation processed successfully",
            "lesson_id": lesson_id,
            "total_slides": presentation_data['total_slides'],
            "slides": presentation_data['slides']
        }
        
    except Exception as e:
        # ✅ NEW: Send error message via WebSocket
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "presentation_processing_error",
            "lesson_id": lesson_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Presentation processing failed: {str(e)}"
        )


@router.post("/{lesson_id}/process-presentation")
async def process_presentation_legacy(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Process presentation - Legacy endpoint (alias)
    """
    return await process_presentation_endpoint(lesson_id, db, current_user)


@router.get("/{lesson_id}/presentation")
async def get_presentation_data(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get processed presentation data for a lesson
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Presentation data with slides, images, and audio
    """
    from backend.services.presentation_service import PresentationService
    
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    presentation_service = PresentationService()
    presentation_data = presentation_service.load_presentation_metadata(lesson_id)
    
    if not presentation_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not processed yet. Please upload and process first."
        )
    
    return presentation_data
