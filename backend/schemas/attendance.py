"""
Attendance Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AttendanceBase(BaseModel):
    student_id: int
    lesson_id: int
    entry_method: str = "face_recognition"
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    """Schema for recording attendance"""
    recognition_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response"""
    id: int
    timestamp: datetime
    recognition_confidence: Optional[float] = None
    
    class Config:
        from_attributes = True
