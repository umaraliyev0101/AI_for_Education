"""
Lesson Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from backend.models.lesson import LessonStatus


class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    date: datetime
    duration_minutes: Optional[int] = Field(None, gt=0)
    subject: Optional[str] = None
    notes: Optional[str] = None


class LessonCreate(LessonBase):
    """Schema for creating a new lesson"""
    pass


class LessonUpdate(BaseModel):
    """Schema for updating lesson information"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    subject: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[LessonStatus] = None


class LessonResponse(LessonBase):
    """Schema for lesson response"""
    id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    presentation_path: Optional[str] = None
    materials_path: Optional[str] = None
    vector_store_path: Optional[str] = None
    status: LessonStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
