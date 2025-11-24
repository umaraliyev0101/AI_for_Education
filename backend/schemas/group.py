"""
Group Schemas
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class StudentInfo(BaseModel):
    """Simplified student info for group responses"""
    id: int
    student_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Group name (e.g., 'Year 1 - Group A')")
    year_level: int = Field(..., ge=1, le=4, description="Academic year level (1-4)")


class GroupCreate(GroupBase):
    """Schema for creating a new group"""
    pass


class GroupUpdate(BaseModel):
    """Schema for updating group information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    year_level: Optional[int] = Field(None, ge=1, le=4)


class GroupResponse(GroupBase):
    """Schema for group response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    students: List[StudentInfo] = Field(default_factory=list, description="List of students in this group")

    class Config:
        from_attributes = True
