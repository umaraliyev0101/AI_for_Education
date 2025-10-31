"""
Configuration Settings
Environment configuration using pydantic-settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Education Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./ai_education.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS - Allow all origins for development (update for production)
    CORS_ORIGINS: list = ["*"]  # Allow all origins for testing
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    FACE_IMAGES_DIR: str = "./uploads/faces"
    MATERIALS_DIR: str = "./uploads/materials"
    PRESENTATIONS_DIR: str = "./uploads/presentations"
    AUDIO_DIR: str = "./uploads/audio"
    VECTOR_STORES_DIR: str = "./vector_stores"
    
    # AI Models
    STT_MODEL: str = "lucio/xls-r-uzbek-cv8"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    TTS_VOICE: str = "uz-UZ-MadinaNeural"
    
    # Processing
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K_DOCUMENTS: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
