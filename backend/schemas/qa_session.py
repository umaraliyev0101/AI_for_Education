"""
QA Session Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class QASessionBase(BaseModel):
    lesson_id: int
    question_text: str = Field(..., min_length=1)


class QASessionCreate(QASessionBase):
    """Schema for creating a Q&A session entry"""
    transcription_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    question_audio_path: Optional[str] = None


class QASessionResponse(QASessionBase):
    """Schema for Q&A session response"""
    id: int
    question_audio_path: Optional[str] = None
    transcription_confidence: Optional[float] = None
    answer_text: Optional[str] = None
    answer_audio_path: Optional[str] = None
    found_answer: bool
    relevance_score: Optional[float] = None
    source_documents: Optional[str] = None
    processing_time_ms: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
