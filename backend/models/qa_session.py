"""
QA Session Model
Tracks questions and answers during lesson Q&A sessions
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class QASession(Base):
    __tablename__ = "qa_sessions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    # Question details
    question_text = Column(Text, nullable=False)
    question_audio_path = Column(String(500), nullable=True)  # Path to recorded audio
    transcription_confidence = Column(Float, nullable=True)  # STT confidence score
    
    # Answer details
    answer_text = Column(Text, nullable=True)
    answer_audio_path = Column(String(500), nullable=True)  # Path to TTS audio
    found_answer = Column(Boolean, default=False)
    relevance_score = Column(Float, nullable=True)  # LLM relevance score
    
    # Source documents (JSON string of document IDs)
    source_documents = Column(Text, nullable=True)
    
    # Processing metadata
    processing_time_ms = Column(Integer, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="qa_sessions")
    
    def __repr__(self):
        return f"<QASession(id={self.id}, lesson_id={self.lesson_id}, found_answer={self.found_answer})>"
