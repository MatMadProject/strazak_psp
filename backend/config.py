import sys
import os
from pathlib import Path

class Settings:
    # Podstawowa konfiguracja
    APP_NAME = "Strazak App"
    VERSION = "1.0.0"
    # Czy aplikacja działa jako exe (PyInstaller)
    IS_DESKTOP = getattr(sys, "frozen", False)
    
    # Ścieżki
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    
    # Baza danych
    # Desktop: SQLite (lokalny plik)
    # Web: Zmień na PostgreSQL connection string
    DATABASE_URL = f"sqlite:///{DATA_DIR / 'app.db'}"
    
    # CORS - dla developmentu
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Limity
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {".xlsx"}
    
    def __init__(self):
        # Utwórz niezbędne foldery
        self.DATA_DIR.mkdir(exist_ok=True)
        self.UPLOAD_DIR.mkdir(exist_ok=True)

settings = Settings()