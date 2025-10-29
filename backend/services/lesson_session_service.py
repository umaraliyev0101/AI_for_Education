"""
Lesson Session Management Service
==================================

Manages lesson lifecycle, automatic start at scheduled time (8AM),
attendance automation, and real-time session state.
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models.lesson import Lesson, LessonStatus
from backend.models.attendance import Attendance
from backend.database import SessionLocal

logger = logging.getLogger(__name__)


class LessonSessionService:
    """Service to manage lesson sessions and automatic scheduling"""
    
    def __init__(self):
        self.active_sessions: Dict[int, Dict[str, Any]] = {}  # {lesson_id: session_data}
        self.scheduler_task: Optional[asyncio.Task] = None
        self.lesson_start_time = time(8, 0)  # 8:00 AM
        
    async def start_scheduler(self):
        """Start the lesson scheduler background task"""
        if self.scheduler_task is None or self.scheduler_task.done():
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("✅ Lesson scheduler started")
    
    async def stop_scheduler(self):
        """Stop the lesson scheduler"""
        if self.scheduler_task and not self.scheduler_task.done():
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Lesson scheduler stopped")
    
    async def _scheduler_loop(self):
        """Background loop to check and auto-start lessons"""
        while True:
            try:
                await self._check_and_start_lessons()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_start_lessons(self):
        """Check if any lessons should be auto-started"""
        db = SessionLocal()
        try:
            now = datetime.now()
            current_time = now.time()
            today = now.date()
            
            # Find lessons scheduled for today at 8AM that haven't started
            lessons = db.query(Lesson).filter(
                and_(
                    Lesson.status == LessonStatus.SCHEDULED,
                    Lesson.date >= datetime.combine(today, time(0, 0)),
                    Lesson.date < datetime.combine(today + timedelta(days=1), time(0, 0))
                )
            ).all()
            
            for lesson in lessons:
                # Check if it's time to start (within 5 minutes of scheduled time)
                lesson_time = lesson.date.time()
                if self._should_start_lesson(current_time, lesson_time):
                    await self._auto_start_lesson(lesson.id, db)
                    
        except Exception as e:
            logger.error(f"❌ Error checking lessons: {e}")
        finally:
            db.close()
    
    def _should_start_lesson(self, current_time: time, lesson_time: time) -> bool:
        """Check if lesson should be started based on time"""
        # Convert to minutes for comparison
        current_minutes = current_time.hour * 60 + current_time.minute
        lesson_minutes = lesson_time.hour * 60 + lesson_time.minute
        
        # Start lesson if within 5 minutes of scheduled time
        diff = current_minutes - lesson_minutes
        return 0 <= diff <= 5
    
    async def _auto_start_lesson(self, lesson_id: int, db: Session):
        """Automatically start a lesson"""
        try:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not lesson or lesson.status != LessonStatus.SCHEDULED:
                return
            
            lesson.status = LessonStatus.IN_PROGRESS
            lesson.start_time = datetime.now()
            db.commit()
            
            # Initialize session data
            self.active_sessions[lesson_id] = {
                'lesson_id': lesson_id,
                'started_at': lesson.start_time,
                'attendance_started': False,
                'presentation_started': False,
                'qa_mode': False,
                'paused': False,
                'current_slide': 0
            }
            
            logger.info(f"✅ Auto-started lesson {lesson_id}: {lesson.title}")
            
        except Exception as e:
            logger.error(f"❌ Failed to auto-start lesson {lesson_id}: {e}")
            db.rollback()
    
    async def start_lesson_manually(self, lesson_id: int, db: Session) -> bool:
        """Manually start a lesson (when teacher logs in)"""
        try:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not lesson:
                return False
            
            if lesson.status == LessonStatus.SCHEDULED:
                lesson.status = LessonStatus.IN_PROGRESS
                lesson.start_time = datetime.now()
                db.commit()
                
                # Initialize session
                self.active_sessions[lesson_id] = {
                    'lesson_id': lesson_id,
                    'started_at': lesson.start_time,
                    'attendance_started': False,
                    'presentation_started': False,
                    'qa_mode': False,
                    'paused': False,
                    'current_slide': 0
                }
                
                logger.info(f"✅ Manually started lesson {lesson_id}: {lesson.title}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start lesson {lesson_id}: {e}")
            db.rollback()
            return False
    
    async def end_lesson(self, lesson_id: int, db: Session) -> bool:
        """End a lesson"""
        try:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not lesson or lesson.status != LessonStatus.IN_PROGRESS:
                return False
            
            lesson.status = LessonStatus.COMPLETED
            lesson.end_time = datetime.now()
            db.commit()
            
            # Clean up session data
            if lesson_id in self.active_sessions:
                del self.active_sessions[lesson_id]
            
            logger.info(f"✅ Ended lesson {lesson_id}: {lesson.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to end lesson {lesson_id}: {e}")
            db.rollback()
            return False
    
    def get_session_state(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Get current session state for a lesson"""
        return self.active_sessions.get(lesson_id)
    
    def update_session_state(self, lesson_id: int, updates: Dict[str, Any]):
        """Update session state"""
        if lesson_id in self.active_sessions:
            self.active_sessions[lesson_id].update(updates)
    
    def is_lesson_active(self, lesson_id: int) -> bool:
        """Check if lesson is currently active"""
        return lesson_id in self.active_sessions
    
    async def start_attendance_phase(self, lesson_id: int) -> bool:
        """Mark that attendance phase has started"""
        if lesson_id in self.active_sessions:
            self.active_sessions[lesson_id]['attendance_started'] = True
            logger.info(f"✅ Started attendance for lesson {lesson_id}")
            return True
        return False
    
    async def start_presentation_phase(self, lesson_id: int) -> bool:
        """Mark that presentation phase has started"""
        if lesson_id in self.active_sessions:
            self.active_sessions[lesson_id]['presentation_started'] = True
            self.active_sessions[lesson_id]['attendance_started'] = False
            logger.info(f"✅ Started presentation for lesson {lesson_id}")
            return True
        return False
    
    async def start_qa_phase(self, lesson_id: int) -> bool:
        """Mark that Q&A phase has started"""
        if lesson_id in self.active_sessions:
            self.active_sessions[lesson_id]['qa_mode'] = True
            self.active_sessions[lesson_id]['presentation_started'] = False
            logger.info(f"✅ Started Q&A for lesson {lesson_id}")
            return True
        return False
    
    async def pause_lesson(self, lesson_id: int) -> bool:
        """Pause the lesson (for questions during presentation)"""
        if lesson_id in self.active_sessions:
            self.active_sessions[lesson_id]['paused'] = True
            logger.info(f"⏸️ Paused lesson {lesson_id}")
            return True
        return False
    
    async def resume_lesson(self, lesson_id: int) -> bool:
        """Resume the lesson after question"""
        if lesson_id in self.active_sessions:
            self.active_sessions[lesson_id]['paused'] = False
            logger.info(f"▶️ Resumed lesson {lesson_id}")
            return True
        return False
    
    def get_active_lessons(self) -> List[int]:
        """Get list of active lesson IDs"""
        return list(self.active_sessions.keys())


# Global service instance
_lesson_session_service: Optional[LessonSessionService] = None


def get_lesson_session_service() -> LessonSessionService:
    """Get or create the lesson session service singleton"""
    global _lesson_session_service
    if _lesson_session_service is None:
        _lesson_session_service = LessonSessionService()
    return _lesson_session_service
