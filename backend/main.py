"""
FastAPI Main Application
AI Education Backend Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db
import os

# Create upload directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FACE_IMAGES_DIR, exist_ok=True)
os.makedirs(settings.MATERIALS_DIR, exist_ok=True)
os.makedirs(settings.PRESENTATIONS_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORES_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for AI-powered education system with face recognition, attendance, and Q&A",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on startup"""
    init_db()
    
    # Start lesson scheduler
    from backend.services.lesson_session_service import get_lesson_session_service
    lesson_service = get_lesson_session_service()
    await lesson_service.start_scheduler()
    
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    print(f"📅 Lesson scheduler: Active")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    from backend.services.lesson_session_service import get_lesson_session_service
    lesson_service = get_lesson_session_service()
    await lesson_service.stop_scheduler()
    print("🛑 Lesson scheduler stopped")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import and include routers
from backend.routes import auth, students, lessons, attendance, qa, websocket

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(qa.router, prefix="/api/qa", tags=["Q&A"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
