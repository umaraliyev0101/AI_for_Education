"""
Student Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class StudentBase(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    group_id: int = Field(..., description="ID of the group this student belongs to")
    is_active: bool = True


class StudentCreate(StudentBase):
    """Schema for creating a new student"""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating student information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    group_id: Optional[int] = Field(None, description="ID of the group this student belongs to")
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int
    face_image_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
