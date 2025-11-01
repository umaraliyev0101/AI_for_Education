"""
WebSocket Routes for Real-Time Lesson Management
=================================================

WebSocket endpoints for:
- Live attendance monitoring
- Presentation delivery with audio
- Real-time Q&A during lessons
- Lesson state updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime, date
from decimal import Decimal

from backend.database import get_db
from backend.models.lesson import Lesson
from backend.models.user import User, UserRole
from backend.dependencies import get_current_user_ws
from backend.services.lesson_session_service import get_lesson_session_service
from backend.services.presentation_service import get_presentation_service
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for lessons"""
    
    def __init__(self):
        # {lesson_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        self.connection_counter = 0
    
    def _serialize_data(self, data: Any) -> Any:
        """
        Recursively convert non-JSON-serializable objects to JSON-compatible types
        
        Handles:
        - datetime/date objects → ISO format strings
        - Decimal objects → float
        - SQLAlchemy models → dict (via __dict__)
        - bytes → decode to string
        """
        if isinstance(data, dict):
            return {key: self._serialize_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize_data(item) for item in data]
        elif isinstance(data, (datetime, date)):
            return data.isoformat()  # Convert datetime/date to ISO string
        elif isinstance(data, Decimal):
            return float(data)  # Convert Decimal to float
        elif isinstance(data, bytes):
            try:
                return data.decode('utf-8')  # Try to decode bytes
            except:
                return str(data)  # Fallback to string representation
        elif hasattr(data, '__dict__') and not isinstance(data, type):
            # Handle SQLAlchemy models and other objects with __dict__
            obj_dict = {}
            for key, value in data.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes like _sa_instance_state
                    obj_dict[key] = self._serialize_data(value)
            return obj_dict
        else:
            return data
    
    async def connect(self, websocket: WebSocket, lesson_id: int) -> str:
        """Connect a client to a lesson room"""
        await websocket.accept()
        
        if lesson_id not in self.active_connections:
            self.active_connections[lesson_id] = {}
        
        connection_id = f"conn_{self.connection_counter}"
        self.connection_counter += 1
        
        self.active_connections[lesson_id][connection_id] = websocket
        logger.info(f"✅ Client {connection_id} connected to lesson {lesson_id}")
        
        return connection_id
    
    def disconnect(self, lesson_id: int, connection_id: str):
        """Disconnect a client from a lesson room"""
        if lesson_id in self.active_connections:
            if connection_id in self.active_connections[lesson_id]:
                del self.active_connections[lesson_id][connection_id]
                logger.info(f"🔌 Client {connection_id} disconnected from lesson {lesson_id}")
            
            # Clean up empty rooms
            if not self.active_connections[lesson_id]:
                del self.active_connections[lesson_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            # Serialize the message before sending to handle datetime objects
            serialized_message = self._serialize_data(message)
            await websocket.send_json(serialized_message)
        except Exception as e:
            logger.error(f"❌ Failed to send personal message: {e}")
    
    async def broadcast_to_lesson(self, lesson_id: int, message: dict):
        """Broadcast a message to all connections in a lesson room"""
        if lesson_id in self.active_connections:
            # Serialize the message once before broadcasting
            serialized_message = self._serialize_data(message)
            
            disconnected = []
            for connection_id, websocket in self.active_connections[lesson_id].items():
                try:
                    await websocket.send_json(serialized_message)
                except Exception as e:
                    logger.error(f"❌ Failed to send to {connection_id}: {e}")
                    disconnected.append(connection_id)
            
            # Clean up disconnected clients
            for connection_id in disconnected:
                self.disconnect(lesson_id, connection_id)
    
    def get_connection_count(self, lesson_id: int) -> int:
        """Get number of active connections for a lesson"""
        return len(self.active_connections.get(lesson_id, {}))


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/lesson/{lesson_id}")
async def lesson_websocket(
    websocket: WebSocket,
    lesson_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time lesson management
    
    Message types from client:
    - {"type": "start_attendance"}
    - {"type": "end_attendance"}
    - {"type": "start_presentation"}
    - {"type": "next_slide"}
    - {"type": "previous_slide"}
    - {"type": "pause_presentation"}
    - {"type": "resume_presentation"}
    - {"type": "ask_question", "question": "text", "method": "text|audio"}
    - {"type": "start_qa"}
    - {"type": "end_lesson"}
    
    Message types to client:
    - {"type": "lesson_state", "data": {...}}
    - {"type": "attendance_update", "student": {...}}
    - {"type": "slide_data", "slide": {...}}
    - {"type": "presentation_paused"}
    - {"type": "presentation_resumed"}
    - {"type": "question_answered", "answer": {...}}
    - {"type": "qa_mode_started"}
    - {"type": "lesson_ended"}
    - {"type": "error", "message": "..."}
    """
    
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        await websocket.close(code=4004, reason="Lesson not found")
        return
    
    # Connect client
    connection_id = await manager.connect(websocket, lesson_id)
    
    # Get services
    session_service = get_lesson_session_service()
    presentation_service = get_presentation_service()
    
    try:
        # Send initial lesson state
        session_state = session_service.get_session_state(lesson_id)
        await manager.send_personal_message({
            "type": "lesson_state",
            "data": {
                "lesson_id": lesson_id,
                "status": lesson.status.value,
                "session": session_state,
                "connection_count": manager.get_connection_count(lesson_id)
            }
        }, websocket)
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "start_attendance":
                await handle_start_attendance(lesson_id, session_service, manager)
            
            elif message_type == "end_attendance":
                await handle_end_attendance(lesson_id, session_service, manager)
            
            elif message_type == "start_presentation":
                await handle_start_presentation(lesson_id, lesson, session_service, presentation_service, manager)
            
            elif message_type == "next_slide":
                await handle_next_slide(lesson_id, session_service, presentation_service, manager)
            
            elif message_type == "previous_slide":
                await handle_previous_slide(lesson_id, session_service, presentation_service, manager)
            
            elif message_type == "pause_presentation":
                await handle_pause_presentation(lesson_id, session_service, manager)
            
            elif message_type == "resume_presentation":
                await handle_resume_presentation(lesson_id, session_service, manager)
            
            elif message_type == "ask_question":
                await handle_ask_question(
                    lesson_id,
                    data.get("question"),
                    data.get("method", "text"),
                    session_service,
                    manager,
                    websocket
                )
            
            elif message_type == "start_qa":
                await handle_start_qa(lesson_id, session_service, manager)
            
            elif message_type == "end_lesson":
                await handle_end_lesson(lesson_id, session_service, manager, db)
                break
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(lesson_id, connection_id)
        logger.info(f"Client {connection_id} disconnected from lesson {lesson_id}")
    
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(lesson_id, connection_id)


async def handle_start_attendance(lesson_id: int, session_service, manager):
    """Handle attendance phase start"""
    await session_service.start_attendance_phase(lesson_id)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "attendance_started",
        "timestamp": datetime.now().isoformat()
    })


async def handle_end_attendance(lesson_id: int, session_service, manager):
    """Handle attendance phase end"""
    session_service.update_session_state(lesson_id, {'attendance_started': False})
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "attendance_ended",
        "timestamp": datetime.now().isoformat()
    })


async def handle_start_presentation(lesson_id: int, lesson, session_service, presentation_service, manager):
    """Handle presentation phase start"""
    await session_service.start_presentation_phase(lesson_id)
    
    # ✅ FIX: Load presentation data (should already be processed via API endpoint)
    presentation_data = presentation_service.load_presentation_metadata(lesson_id)
    
    if not presentation_data:
        # ❌ Presentation not processed yet - send error instead of auto-processing
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "error",
            "message": "Presentation not processed yet. Please upload and process the presentation first.",
            "timestamp": datetime.now().isoformat()
        })
        logger.warning(f"⚠️ Attempted to start unprocessed presentation for lesson {lesson_id}")
        return
    
    if presentation_data:
        # Send ALL presentation data including all slides
        session_service.update_session_state(lesson_id, {'current_slide': 1})
        
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "presentation_started",
            "lesson_id": lesson_id,
            "lesson_title": lesson.title,
            "total_slides": presentation_data['total_slides'],
            "slides": presentation_data['slides'],  # ← All slides with image_path, audio_path, text
            "current_slide_number": 1,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"📊 Presentation started for lesson {lesson_id} with {presentation_data['total_slides']} slides")
    else:
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "error",
            "message": "No presentation available"
        })


async def handle_next_slide(lesson_id: int, session_service, presentation_service, manager):
    """Handle next slide request"""
    session_state = session_service.get_session_state(lesson_id)
    if not session_state:
        return
    
    current_slide = session_state.get('current_slide', 0)
    presentation_data = presentation_service.load_presentation_metadata(lesson_id)
    
    if presentation_data and current_slide < presentation_data['total_slides']:
        next_slide_num = current_slide + 1
        slide_data = presentation_service.get_slide_data(lesson_id, next_slide_num)
        
        session_service.update_session_state(lesson_id, {'current_slide': next_slide_num})
        
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "slide_changed",
            "slide": slide_data,
            "timestamp": datetime.now().isoformat()
        })
    elif presentation_data and current_slide >= presentation_data['total_slides']:
        # Presentation completed, transition to Q&A
        await handle_presentation_completed(lesson_id, session_service, manager)


async def handle_previous_slide(lesson_id: int, session_service, presentation_service, manager):
    """Handle previous slide request"""
    session_state = session_service.get_session_state(lesson_id)
    if not session_state:
        return
    
    current_slide = session_state.get('current_slide', 1)
    
    if current_slide > 1:
        prev_slide_num = current_slide - 1
        slide_data = presentation_service.get_slide_data(lesson_id, prev_slide_num)
        
        session_service.update_session_state(lesson_id, {'current_slide': prev_slide_num})
        
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "slide_changed",
            "slide": slide_data,
            "timestamp": datetime.now().isoformat()
        })


async def handle_pause_presentation(lesson_id: int, session_service, manager):
    """Handle presentation pause (for questions)"""
    await session_service.pause_lesson(lesson_id)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "presentation_paused",
        "timestamp": datetime.now().isoformat()
    })


async def handle_resume_presentation(lesson_id: int, session_service, manager):
    """Handle presentation resume"""
    await session_service.resume_lesson(lesson_id)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "presentation_resumed",
        "timestamp": datetime.now().isoformat()
    })


async def handle_ask_question(lesson_id: int, question: str, method: str, session_service, manager, websocket):
    """Handle question during presentation"""
    # This will be processed by Q&A system
    # For now, just acknowledge
    await manager.send_personal_message({
        "type": "question_received",
        "question": question,
        "method": method,
        "timestamp": datetime.now().isoformat()
    }, websocket)


async def handle_start_qa(lesson_id: int, session_service, manager):
    """Handle Q&A phase start"""
    await session_service.start_qa_phase(lesson_id)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "qa_mode_started",
        "timestamp": datetime.now().isoformat()
    })


async def handle_presentation_completed(lesson_id: int, session_service, manager):
    """Handle presentation completion and auto-transition to Q&A"""
    await session_service.start_qa_phase(lesson_id)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "presentation_completed",
        "message": "Presentation finished. Starting Q&A session.",
        "timestamp": datetime.now().isoformat()
    })


async def handle_end_lesson(lesson_id: int, session_service, manager, db: Session):
    """Handle lesson end"""
    await session_service.end_lesson(lesson_id, db)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "lesson_ended",
        "timestamp": datetime.now().isoformat()
    })


@router.get("/lesson/{lesson_id}/connections")
async def get_lesson_connections(lesson_id: int):
    """Get number of active connections for a lesson"""
    return {
        "lesson_id": lesson_id,
        "active_connections": manager.get_connection_count(lesson_id)
    }
