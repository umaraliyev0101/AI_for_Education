"""
Attendance Model
Tracks student attendance for lessons with face recognition
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    # Attendance details
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    recognition_confidence = Column(Float, nullable=True)  # Face recognition confidence score
    entry_method = Column(String(50), default="face_recognition")  # face_recognition, manual, etc.
    
    # Notes
    notes = Column(String(500), nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    lesson = relationship("Lesson", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, student_id={self.student_id}, lesson_id={self.lesson_id})>"
