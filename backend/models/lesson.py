"""
Lesson Model
Represents a lesson/class session with materials and presentation
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum


class LessonStatus(str, enum.Enum):
    """Lesson status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Schedule
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Materials
    presentation_path = Column(String(500), nullable=True)
    materials_path = Column(String(500), nullable=True)
    vector_store_path = Column(String(500), nullable=True)  # Path to FAISS vector store
    
    # Status
    status = Column(SQLEnum(LessonStatus), default=LessonStatus.SCHEDULED)
    
    # Metadata
    subject = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attendance_records = relationship("Attendance", back_populates="lesson", cascade="all, delete-orphan")
    qa_sessions = relationship("QASession", back_populates="lesson", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, title='{self.title}', status='{self.status}')>"
