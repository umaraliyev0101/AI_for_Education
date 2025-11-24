"""
WebSocket Routes for Real-Time Lesson Management
=================================================

WebSocket endpoints for:
- Live attendance monitoring
- Real-time Q&A during lessons
- Lesson state updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime, date
from decimal import Decimal
import asyncio
import cv2
import os

from backend.database import get_db
from backend.models.lesson import Lesson
from backend.models.user import User, UserRole
from backend.dependencies import get_current_user_ws
from backend.services.lesson_session_service import get_lesson_session_service
from face_recognition.face_attendance import FaceRecognitionAttendance
from backend.models.student import Student
from backend.models.attendance import Attendance
from backend.routes.attendance import get_student_photo_base64
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for lessons"""
    
    def __init__(self):
        # {lesson_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        self.connection_counter = 0
        
        # Attendance monitoring
        self.attendance_monitors: Dict[int, Dict[str, Any]] = {}  # {lesson_id: monitor_data}
        self.monitoring_tasks: Dict[int, asyncio.Task] = {}  # {lesson_id: task}
        self.stop_flags: Dict[int, bool] = {}  # {lesson_id: stop_flag}
    
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
    
    async def start_attendance_monitoring(self, lesson_id: int):
        """Start automatic attendance monitoring for a lesson"""
        if lesson_id in self.monitoring_tasks:
            return  # Already monitoring
        
        # Initialize attendance monitor
        self.attendance_monitors[lesson_id] = {
            'face_recognition': None,
            'present_students': set(),
            'last_update': datetime.now(),
            'camera_id': 0  # Default camera
        }
        
        # Initialize stop flag
        self.stop_flags[lesson_id] = False
        
        # Initialize face recognition system
        try:
            attendance_db_path = os.path.join("uploads", "attendance.db")
            self.attendance_monitors[lesson_id]['face_recognition'] = FaceRecognitionAttendance(
                db_path=attendance_db_path,
                threshold=0.6
            )
            logger.info(f"✅ Started face recognition for lesson {lesson_id}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize face recognition: {e}")
            return
        
        # Start monitoring task
        task = asyncio.create_task(self._attendance_monitoring_loop(lesson_id))
        self.monitoring_tasks[lesson_id] = task
        
        logger.info(f"✅ Started attendance monitoring for lesson {lesson_id}")
    
    async def stop_attendance_monitoring(self, lesson_id: int):
        """Stop attendance monitoring for a lesson"""
        # Set stop flag first
        self.stop_flags[lesson_id] = True
        
        if lesson_id in self.monitoring_tasks:
            self.monitoring_tasks[lesson_id].cancel()
            try:
                await self.monitoring_tasks[lesson_id]
            except asyncio.CancelledError:
                pass
            del self.monitoring_tasks[lesson_id]
        
        if lesson_id in self.attendance_monitors:
            monitor = self.attendance_monitors[lesson_id]
            if monitor['face_recognition']:
                monitor['face_recognition'].close()
            del self.attendance_monitors[lesson_id]
        
        # Clean up stop flag
        if lesson_id in self.stop_flags:
            del self.stop_flags[lesson_id]
        
        logger.info(f"🛑 Stopped attendance monitoring for lesson {lesson_id}")
    
    async def _attendance_monitoring_loop(self, lesson_id: int):
        """Background loop for attendance monitoring"""
        monitor = self.attendance_monitors.get(lesson_id)
        if not monitor or not monitor['face_recognition']:
            return
        
        face_recognition = monitor['face_recognition']
        
        # Create our own database session for this background task
        db = next(get_db())
        
        # Try to open camera
        cap = cv2.VideoCapture(monitor['camera_id'])
        if not cap.isOpened():
            logger.error(f"❌ Cannot open camera for lesson {lesson_id}")
            db.close()
            return
        
        try:
            while not self.stop_flags.get(lesson_id, False) and lesson_id in self.attendance_monitors:
                ret, frame = cap.read()
                if not ret:
                    await asyncio.sleep(1)
                    continue
                
                # Process frame for face recognition
                _, recognized = face_recognition.process_frame(frame, mark_attendance=True)
                
                # Process recognized students
                for student_info in recognized:
                    student_id = student_info['student_id']
                    
                    # Check if this is a new detection
                    if student_id not in monitor['present_students']:
                        monitor['present_students'].add(student_id)
                        
                        # Get student details from database
                        student = db.query(Student).filter(Student.student_id == student_id).first()
                        if student:
                            # Mark attendance in main database
                            attendance_record = Attendance(
                                student_id=student.id,
                                lesson_id=lesson_id,
                                recognition_confidence=student_info['confidence'],
                                entry_method="auto_face_recognition"
                            )
                            db.add(attendance_record)
                            db.commit()
                            
                            # Send real-time update to clients
                            student_data = {
                                'student_id': student.student_id,
                                'name': student.name,
                                'email': student.email,
                                'confidence': student_info['confidence'],
                                'face_image_path': student.face_image_path,
                                'photo_base64': get_student_photo_base64(student),
                                'detected_at': datetime.now().isoformat()
                            }
                            
                            await self.broadcast_to_lesson(lesson_id, {
                                "type": "student_detected",
                                "student": student_data,
                                "timestamp": datetime.now().isoformat()
                            })
                
                # Send attendance count update every second
                current_time = datetime.now()
                if (current_time - monitor['last_update']).seconds >= 1:
                    monitor['last_update'] = current_time
                    
                    await self.broadcast_to_lesson(lesson_id, {
                        "type": "attendance_count_update",
                        "present_count": len(monitor['present_students']),
                        "timestamp": current_time.isoformat()
                    })
                
                await asyncio.sleep(0.5)  # Check every 0.5 seconds
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"❌ Attendance monitoring error for lesson {lesson_id}: {e}")
        finally:
            cap.release()
            # Always close the database session
            try:
                db.close()
            except Exception:
                pass
    
    async def get_attendance_report(self, lesson_id: int, db: Session) -> Dict[str, Any]:
        """Generate comprehensive attendance report for a lesson"""
        monitor = self.attendance_monitors.get(lesson_id, {})
        present_students = monitor.get('present_students', set())
        
        # Get all students (assuming all enrolled students are potential attendees)
        all_students = db.query(Student).filter(Student.is_active == True).all()
        
        # Get present students details
        present_students_data = []
        for student in all_students:
            if student.student_id in present_students:
                # Get attendance record
                attendance_record = db.query(Attendance).filter(
                    Attendance.student_id == student.id,
                    Attendance.lesson_id == lesson_id
                ).first()
                
                present_students_data.append({
                    'student_id': student.student_id,
                    'name': student.name,
                    'email': student.email,
                    'face_image_path': student.face_image_path,
                    'photo_base64': get_student_photo_base64(student),
                    'detected_at': attendance_record.timestamp.isoformat() if attendance_record else None,
                    'confidence': attendance_record.recognition_confidence if attendance_record else None
                })
        
        # Get absent students
        absent_students_data = []
        for student in all_students:
            if student.student_id not in present_students:
                absent_students_data.append({
                    'student_id': student.student_id,
                    'name': student.name,
                    'email': student.email,
                    'face_image_path': student.face_image_path,
                    'photo_base64': get_student_photo_base64(student)
                })
        
        return {
            'total_students': len(all_students),
            'present_count': len(present_students_data),
            'absent_count': len(absent_students_data),
            'present_students': present_students_data,
            'absent_students': absent_students_data,
            'attendance_rate': (len(present_students_data) / len(all_students) * 100) if all_students else 0
        }


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
    - {"type": "stop_auto_attendance"}
    - {"type": "ask_question", "question": "text", "method": "text|audio"}
    - {"type": "start_qa"}
    - {"type": "end_lesson"}
    
    Message types to client:
    - {"type": "lesson_state", "data": {...}}
    - {"type": "attendance_started", "auto_monitoring": true}
    - {"type": "attendance_ended", "report": {...}}
    - {"type": "auto_attendance_stopped", "message": "..."}
    - {"type": "student_detected", "student": {...}}
    - {"type": "attendance_count_update", "present_count": 5}
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
            
            elif message_type == "stop_auto_attendance":
                await handle_stop_auto_attendance(lesson_id, manager)
            
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
    
    # Start automatic attendance monitoring
    await manager.start_attendance_monitoring(lesson_id)
    
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "attendance_started",
        "auto_monitoring": True,
        "timestamp": datetime.now().isoformat()
    })


async def handle_end_attendance(lesson_id: int, session_service, manager):
    """Handle attendance phase end"""
    session_service.update_session_state(lesson_id, {'attendance_started': False})
    
    # Stop automatic attendance monitoring
    await manager.stop_attendance_monitoring(lesson_id)
    
    # Generate and send final attendance report
    db = next(get_db())
    try:
        report = await manager.get_attendance_report(lesson_id, db)
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "attendance_ended",
            "report": report,
            "timestamp": datetime.now().isoformat()
        })
    finally:
        db.close()


async def handle_ask_question(lesson_id: int, question: str, method: str, session_service, manager, websocket):
    """Handle question during presentation with LLM processing and audio response"""
    try:
        # Acknowledge question receipt
        await manager.send_personal_message({
            "type": "question_received",
            "question": question,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Get LLM service
        from backend.routes.qa import get_llm_service
        llm_service = get_llm_service()
        
        if not llm_service:
            await manager.send_personal_message({
                "type": "question_answered",
                "question": question,
                "answer": {
                    "text": "LLM service mavjud emas.",
                    "audio_path": None,
                    "found_answer": False
                },
                "timestamp": datetime.now().isoformat()
            }, websocket)
            return
        
        # Process question using LLM
        lesson_id_str = f"lesson_{lesson_id}"
        
        # Prepare lesson materials if available
        from backend.models.lesson import Lesson
        from backend.database import get_db
        from sqlalchemy.orm import Session
        import os
        
        db: Session = next(get_db())
        try:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            materials_path = getattr(lesson, 'materials_path', None)
            if lesson and materials_path and os.path.exists(str(materials_path)):
                file_paths = []
                for root, dirs, files in os.walk(str(materials_path)):
                    for file in files:
                        if file.endswith(('.pdf', '.pptx', '.docx', '.txt', '.md')):
                            file_paths.append(os.path.join(root, file))
                
                if file_paths:
                    success = llm_service.prepare_lesson_materials(file_paths, lesson_id_str)
                    if not success:
                        logger.warning(f"Failed to prepare materials for lesson {lesson_id}")
        finally:
            db.close()
        
        # Generate answer
        answer, found, docs = llm_service.answer_question(
            question, 
            lesson_id_str, 
            use_llm=True
        )
        
        # Generate TTS audio for answer
        audio_path = None
        if answer:
            try:
                from stt_pipelines.uzbek_tts_pipeline import create_uzbek_tts
                from backend.config import settings
                import os
                
                tts = create_uzbek_tts(voice="male_clear")
                
                audio_filename = f"qa_{lesson_id}_ws_answer_{hash(answer[:50])}.mp3"
                audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
                
                tts.speak_text(answer, save_to_file=audio_path)
                
                # Convert to relative path for frontend
                if os.path.exists(audio_path):
                    audio_path = f"/uploads/audio/{audio_filename}"
                else:
                    audio_path = None
                    
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")
                audio_path = None
        
        # Send answer back
        await manager.send_personal_message({
            "type": "question_answered",
            "question": question,
            "answer": {
                "text": answer,
                "audio_path": audio_path,
                "found_answer": found,
                "retrieved_docs_count": len(docs)
            },
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        await manager.send_personal_message({
            "type": "question_answered",
            "question": question,
            "answer": {
                "text": f"Xatolik yuz berdi: {str(e)}",
                "audio_path": None,
                "found_answer": False
            },
            "timestamp": datetime.now().isoformat()
        }, websocket)


async def handle_start_qa(lesson_id: int, session_service, manager):
    """Handle Q&A phase start"""
    await session_service.start_qa_phase(lesson_id)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "qa_mode_started",
        "timestamp": datetime.now().isoformat()
    })


async def handle_stop_auto_attendance(lesson_id: int, manager):
    """Handle stopping auto attendance monitoring"""
    # Check if auto attendance is currently running
    is_monitoring = lesson_id in manager.monitoring_tasks and not manager.monitoring_tasks[lesson_id].done()
    
    if is_monitoring:
        # Stop the monitoring
        await manager.stop_attendance_monitoring(lesson_id)
        
        # Update session state to mark attendance as stopped
        session_service = get_lesson_session_service()
        session_service.update_session_state(lesson_id, {'attendance_started': False})
        
        # Send confirmation to all clients
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "auto_attendance_stopped",
            "message": "Auto attendance monitoring has been stopped",
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"🛑 Auto attendance stopped for lesson {lesson_id}")
    else:
        # Send error if not currently monitoring
        await manager.broadcast_to_lesson(lesson_id, {
            "type": "error",
            "message": "Auto attendance is not currently running",
            "timestamp": datetime.now().isoformat()
        })


async def handle_end_lesson(lesson_id: int, session_service, manager, db: Session):
    """Handle lesson end"""
    # Stop attendance monitoring if still running
    await manager.stop_attendance_monitoring(lesson_id)
    
    # Generate final attendance report
    report = await manager.get_attendance_report(lesson_id, db)
    
    await session_service.end_lesson(lesson_id, db)
    await manager.broadcast_to_lesson(lesson_id, {
        "type": "lesson_ended",
        "final_attendance_report": report,
        "timestamp": datetime.now().isoformat()
    })


@router.get("/lesson/{lesson_id}/connections")
async def get_lesson_connections(lesson_id: int):
    """Get number of active connections for a lesson"""
    return {
        "lesson_id": lesson_id,
        "active_connections": manager.get_connection_count(lesson_id)
    }
