"""
Q&A Session Routes
Process questions and retrieve answers using LLM (FLAN-T5 for lightweight testing)
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
import logging

_llm_service = None

# Import LLM QA Service
try:
    from utils.uzbek_llm_qa_service import create_uzbek_llm_qa_service
    LLM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LLM service not available: {e}")
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter()


def get_llm_service():
    """Get or initialize the LLM service."""
    global _llm_service
    if _llm_service is None and LLM_AVAILABLE:
        try:
            _llm_service = create_uzbek_llm_qa_service()
            logger.info("✅ LLM service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM service: {e}")
            _llm_service = None
    return _llm_service

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
    generate_audio: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Q&A session entry (text question)
    
    Args:
        qa_data: Q&A session data
        generate_audio: Whether to generate TTS audio for the answer
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created Q&A session with answer and optional audio
        
    Note:
        Uses FLAN-T5 (lightweight model) for answer generation with RAG
    """
    from backend.config import settings
    import os
    
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
    
    # Try to get answer using LLM
    llm_service = get_llm_service()
    if llm_service and lesson.materials_path:
        try:
            # Prepare lesson materials if not already done
            materials_dir = lesson.materials_path
            if os.path.exists(materials_dir):
                file_paths = []
                for root, dirs, files in os.walk(materials_dir):
                    for file in files:
                        if file.endswith(('.pdf', '.pptx', '.docx', '.txt', '.md')):
                            file_paths.append(os.path.join(root, file))
                
                if file_paths:
                    lesson_id_str = f"lesson_{qa_data.lesson_id}"
                    success = llm_service.prepare_lesson_materials(file_paths, lesson_id_str)
                    
                    if success:
                        # Generate answer
                        answer, found, docs = llm_service.answer_question(
                            qa_data.question_text, 
                            lesson_id_str, 
                            use_llm=True
                        )
                        new_qa.found_answer = found
                        new_qa.answer_text = answer
                        new_qa.retrieved_docs_count = len(docs)
                        
                        # Generate TTS audio for answer if requested
                        if generate_audio and answer:
                            try:
                                from stt_pipelines.uzbek_tts_pipeline import create_uzbek_tts
                                tts = create_uzbek_tts(voice="male_clear")
                                
                                audio_filename = f"qa_{new_qa.lesson_id}_answer_{hash(answer[:50])}.mp3"
                                audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
                                
                                tts.speak_text(answer, save_to_file=audio_path)
                                new_qa.answer_audio_path = audio_path
                                
                            except Exception as e:
                                logger.error(f"TTS generation failed: {e}")
                    else:
                        new_qa.found_answer = False
                        new_qa.answer_text = "Dars materiallarini qayta ishlashda xatolik yuz berdi."
                else:
                    new_qa.found_answer = False
                    new_qa.answer_text = "Dars uchun materiallar topilmadi."
            else:
                new_qa.found_answer = False
                new_qa.answer_text = "Dars materiallarining yo'li mavjud emas."
        except Exception as e:
            logger.error(f"LLM processing error: {e}")
            new_qa.found_answer = False
            new_qa.answer_text = f"LLM xatolik: {str(e)}"
    else:
        new_qa.found_answer = False
        new_qa.answer_text = "LLM service mavjud emas yoki dars materiallari yo'q."
    
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
    Ask a question via audio (STT + LLM processing)
    
    Args:
        lesson_id: Lesson database ID
        audio_file: Audio recording of question
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Q&A session with transcribed question and answer
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
    
    # Transcribe audio using STT
    question_text = None
    transcription_confidence = 0.0
    
    try:
        # Import STT service
        from stt_pipelines.uzbek_hf_pipeline import UzbekHFSTTPipeline
        stt = UzbekHFSTTPipeline()
        
        # Transcribe
        result = stt.transcribe_file(audio_path)
        question_text = result.get('text', '').strip()
        transcription_confidence = result.get('confidence', 0.0)
        
        if not question_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not transcribe audio - no speech detected"
            )
            
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="STT service not available"
        )
    except Exception as e:
        logger.error(f"STT transcription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription failed: {str(e)}"
        )
    
    # Create Q&A session with transcribed question
    new_qa = QASession(
        lesson_id=lesson_id,
        question_text=question_text,
        question_audio_path=audio_path,
        transcription_confidence=transcription_confidence
    )
    
    # Generate answer using LLM
    llm_service = get_llm_service()
    if llm_service and lesson.materials_path:
        try:
            # Prepare lesson materials if needed
            materials_dir = lesson.materials_path
            if os.path.exists(materials_dir):
                file_paths = []
                for root, dirs, files in os.walk(materials_dir):
                    for file in files:
                        if file.endswith(('.pdf', '.pptx', '.docx', '.txt', '.md')):
                            file_paths.append(os.path.join(root, file))
                
                if file_paths:
                    lesson_id_str = f"lesson_{lesson_id}"
                    success = llm_service.prepare_lesson_materials(file_paths, lesson_id_str)
                    
                    if success:
                        # Generate answer
                        answer, found, docs = llm_service.answer_question(
                            question_text, 
                            lesson_id_str, 
                            use_llm=True
                        )
                        new_qa.found_answer = found
                        new_qa.answer_text = answer
                        new_qa.retrieved_docs_count = len(docs)
                    else:
                        new_qa.found_answer = False
                        new_qa.answer_text = "Dars materiallarini qayta ishlashda xatolik yuz berdi."
                else:
                    new_qa.found_answer = False
                    new_qa.answer_text = "Dars uchun materiallar topilmadi."
            else:
                new_qa.found_answer = False
                new_qa.answer_text = "Dars materiallarining yo'li mavjud emas."
        except Exception as e:
            logger.error(f"LLM processing error: {e}")
            new_qa.found_answer = False
            new_qa.answer_text = f"LLM xatolik: {str(e)}"
    else:
        new_qa.found_answer = False
        new_qa.answer_text = "LLM service mavjud emas yoki dars materiallari yo'q."
    
    db.add(new_qa)
    db.commit()
    db.refresh(new_qa)
    
    return new_qa


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
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    if not lesson.materials_path or not os.path.exists(lesson.materials_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No materials uploaded for this lesson or materials path does not exist"
        )
    
    # Get LLM service
    llm_service = get_llm_service()
    if not llm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available"
        )
    
    try:
        # Find all supported files in materials directory
        file_paths = []
        for root, dirs, files in os.walk(lesson.materials_path):
            for file in files:
                if file.endswith(('.pdf', '.pptx', '.docx', '.txt', '.md')):
                    file_paths.append(os.path.join(root, file))
        
        if not file_paths:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No supported files found in materials directory"
            )
        
        # Process materials and create vector store
        lesson_id_str = f"lesson_{lesson_id}"
        success = llm_service.prepare_lesson_materials(file_paths, lesson_id_str, force_recreate=True)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process lesson materials"
            )
        
        # Get statistics
        stats = llm_service.get_lesson_statistics(lesson_id_str)
        
        # Optionally save vector store to disk
        vector_store_path = os.path.join(settings.VECTOR_STORES_DIR, f"lesson_{lesson_id}")
        os.makedirs(vector_store_path, exist_ok=True)
        llm_service.save_vector_store(lesson_id_str, vector_store_path)
        
        return {
            "message": "Lesson materials processed successfully",
            "lesson_id": lesson_id,
            "vector_store_path": vector_store_path,
            "statistics": stats,
            "files_processed": len(file_paths)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Materials processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Materials processing failed: {str(e)}"
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
