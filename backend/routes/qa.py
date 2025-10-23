"""
Q&A Session Routes
Process questions and retrieve answers using NLP
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.qa_session import QASession
from backend.models.lesson import Lesson
from backend.models.user import User
from backend.schemas.qa_session import QASessionCreate, QASessionResponse
from backend.dependencies import get_current_user, require_teacher
from backend.config import settings
import os
import json

router = APIRouter()


@router.get("/", response_model=List[QASessionResponse])
async def list_qa_sessions(
    skip: int = 0,
    limit: int = 100,
    lesson_id: Optional[int] = None,
    found_answer: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List Q&A sessions with filtering
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        lesson_id: Filter by lesson ID
        found_answer: Filter by whether answer was found
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of Q&A sessions
    """
    query = db.query(QASession).order_by(QASession.timestamp.desc())
    
    if lesson_id:
        query = query.filter(QASession.lesson_id == lesson_id)
    
    if found_answer is not None:
        query = query.filter(QASession.found_answer == found_answer)
    
    qa_sessions = query.offset(skip).limit(limit).all()
    return qa_sessions


@router.get("/lesson/{lesson_id}", response_model=List[QASessionResponse])
async def get_lesson_qa_sessions(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all Q&A sessions for a specific lesson
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of Q&A sessions for the lesson
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    qa_sessions = db.query(QASession).filter(
        QASession.lesson_id == lesson_id
    ).order_by(QASession.timestamp).all()
    
    return qa_sessions


@router.get("/{qa_id}", response_model=QASessionResponse)
async def get_qa_session(
    qa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Q&A session by ID
    
    Args:
        qa_id: Q&A session ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Q&A session information
    """
    qa_session = db.query(QASession).filter(QASession.id == qa_id).first()
    
    if not qa_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Q&A session with ID {qa_id} not found"
        )
    
    return qa_session


@router.post("/", response_model=QASessionResponse, status_code=status.HTTP_201_CREATED)
async def create_qa_session(
    qa_data: QASessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Q&A session entry (text question)
    
    Args:
        qa_data: Q&A session data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created Q&A session with answer
        
    Note:
        This is a placeholder. Actual NLP processing will be integrated
        with the NLP/QA service.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == qa_data.lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {qa_data.lesson_id} not found"
        )
    
    # Create Q&A session
    new_qa = QASession(
        lesson_id=qa_data.lesson_id,
        question_text=qa_data.question_text,
        question_audio_path=qa_data.question_audio_path,
        transcription_confidence=qa_data.transcription_confidence
    )
    
    # TODO: Integrate NLP/QA service here to get answer
    # For now, mark as not found
    new_qa.found_answer = False
    new_qa.answer_text = "NLP service integration pending"
    
    db.add(new_qa)
    db.commit()
    db.refresh(new_qa)
    
    return new_qa


@router.post("/ask-audio", response_model=QASessionResponse)
async def ask_question_audio(
    lesson_id: int,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ask a question via audio (STT + NLP processing)
    
    Args:
        lesson_id: Lesson database ID
        audio_file: Audio recording of question
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Q&A session with transcribed question and answer
        
    Note:
        This is a placeholder. Actual STT + NLP integration pending.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Validate file type
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file"
        )
    
    # Save audio file
    audio_filename = f"question_{lesson_id}_{audio_file.filename}"
    audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
    
    with open(audio_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)
    
    # TODO: Integrate STT service to transcribe audio
    # TODO: Integrate NLP/QA service to get answer
    # TODO: Integrate TTS service to generate audio answer
    
    # Placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="STT + NLP service integration pending"
    )


@router.post("/process-lesson-materials/{lesson_id}")
async def process_lesson_materials(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Process lesson materials and create vector store for Q&A
    
    Args:
        lesson_id: Lesson database ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        Success message with vector store path
        
    Note:
        This is a placeholder. Actual materials processing and 
        vector store creation will be integrated.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    if not lesson.materials_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No materials uploaded for this lesson"
        )
    
    # TODO: Integrate materials processor and NLP service
    # to create vector store from lesson materials
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Materials processing service integration pending"
    )


@router.delete("/{qa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qa_session(
    qa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """
    Delete a Q&A session (Teacher or Admin)
    
    Args:
        qa_id: Q&A session ID
        db: Database session
        current_user: Authenticated teacher/admin
        
    Returns:
        No content
    """
    qa_session = db.query(QASession).filter(QASession.id == qa_id).first()
    
    if not qa_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Q&A session with ID {qa_id} not found"
        )
    
    db.delete(qa_session)
    db.commit()
    
    return None
