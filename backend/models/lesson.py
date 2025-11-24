"""
Lesson Model
Represents a lesson/class session with materials and presentation
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum
from datetime import datetime


class LessonStatus(str, enum.Enum):
    """Lesson status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Association table for many-to-many relationship between lessons and groups
lesson_groups = Table(
    'lesson_groups',
    Base.metadata,
    Column('lesson_id', Integer, ForeignKey('lessons.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)


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
    groups = relationship("Group", secondary=lesson_groups, backref="lessons")
    
    def calculate_status(self) -> LessonStatus:
        """
        Calculate lesson status based on current time and lesson schedule
        
        Returns:
            LessonStatus: The appropriate status based on timing
        """
        now = datetime.now(self.date.tzinfo) if hasattr(self.date, 'tzinfo') and self.date.tzinfo else datetime.now()
        
        # If manually cancelled, keep cancelled
        current_status = getattr(self, 'status', None)
        if current_status and str(current_status) == str(LessonStatus.CANCELLED):
            return LessonStatus.CANCELLED
        
        # Use the scheduled date as the reference point
        scheduled_time = getattr(self, 'date', None)
        
        if not scheduled_time:
            return LessonStatus.SCHEDULED
        
        # Calculate end time if duration is specified
        duration = getattr(self, 'duration_minutes', None)
        end_time = None
        if duration:
            from datetime import timedelta
            end_time = scheduled_time + timedelta(minutes=duration)
        
        # Status logic based purely on scheduled time
        if now < scheduled_time:
            return LessonStatus.SCHEDULED
        elif end_time and now >= end_time:
            return LessonStatus.COMPLETED
        else:
            return LessonStatus.IN_PROGRESS
    
    def update_status(self):
        """
        Update the lesson status based on current time
        """
        self.status = self.calculate_status()
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, title='{self.title}', status='{self.status}')>"
