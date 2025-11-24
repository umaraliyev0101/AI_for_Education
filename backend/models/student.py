"""
Student Model
Represents a student with face encoding for recognition
"""
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    
    # Group assignment
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    
    # Face recognition data (stored as binary pickle)
    face_encoding = Column(LargeBinary, nullable=True)
    face_image_path = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    group = relationship("Group", back_populates="students")
    
    def __repr__(self):
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.name}')>"
