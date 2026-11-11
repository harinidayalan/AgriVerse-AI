import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of AgriVerse AI
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

class Config:
    """Application configuration for AgriVerse AI."""
    
    # Flask Security & Environment
    SECRET_KEY = os.getenv("SECRET_KEY", "agriverse-smart-farming-secret-key-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    
    # Google Gemini API Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    
    # Upload Settings
    UPLOAD_FOLDER = BASE_DIR / os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    ALLOWED_DOC_EXTENSIONS = {"pdf"}
    
    # Vector Storage & RAG Settings
    VECTOR_STORE_DIR = BASE_DIR / os.getenv("VECTOR_STORE_DIR", "vector_store")
    CHUNK_SIZE = 600       # tokens / chars per chunk
    CHUNK_OVERLAP = 100    # chunk overlap for context retention
    TOP_K_RESULTS = 4      # similarity search neighbors
    
    # SQLite Database Settings
    DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "database/agriverse.db")
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required runtime directories exist."""
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Ensure folders on import
Config.ensure_directories()
