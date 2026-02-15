import sys
import os
from pathlib import Path
import configparser

class Settings:
    # Podstawowa konfiguracja
    APP_NAME = "Strazak App"
    VERSION = "0.1.0"
    
    # Czy aplikacja działa jako exe (PyInstaller)
    IS_DESKTOP = getattr(sys, "frozen", False)
    
    def __init__(self):
        # Ścieżki bazowe
        self.BASE_DIR = self._get_base_dir()
        self.DATA_DIR = self.BASE_DIR / "data"
        
        # Załaduj konfigurację bazy danych
        self._load_database_config()
        
        # Upload dir - zawsze obok bazy danych
        self.UPLOAD_DIR = self.DATABASE_PATH.parent / "uploads"
        
        # Utwórz niezbędne foldery
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Debug info
        print(f"[CONFIG] Mode: {'Desktop (PyInstaller)' if self.IS_DESKTOP else 'Web/Development'}")
        print(f"[CONFIG] Base dir: {self.BASE_DIR}")
        print(f"[CONFIG] Database: {self.DATABASE_PATH}")
        print(f"[CONFIG] Upload dir: {self.UPLOAD_DIR}")
    
    def _get_base_dir(self) -> Path:
        """Pobierz katalog bazowy aplikacji"""
        if self.IS_DESKTOP:
            # PyInstaller - katalog z exe
            return Path(sys.executable).parent
        else:
            # Development/Web - backend/
            return Path(__file__).parent.parent
    
    def _load_database_config(self):
        """
        Wczytaj konfigurację bazy danych.
        Priorytet:
        1. config.ini (desktop z instalatora)
        2. Domyślna persistent location (desktop bez instalatora)
        3. Backend/data/app.db (web/development)
        """
        # Desktop - sprawdź config.ini
        if self.IS_DESKTOP:
            config_path = Path(sys.executable).parent / "config.ini"
            
            if config_path.exists():
                # Odczytaj config.ini (utworzony przez installer)
                try:
                    config = configparser.ConfigParser()
                    config.read(config_path, encoding='utf-8')
                    
                    db_type = config.get('Database', 'Type', fallback='local')
                    db_path_str = config.get('Database', 'Path', fallback=None)
                    
                    if db_path_str:
                        self.DATABASE_PATH = Path(db_path_str)
                        self.DATABASE_TYPE = db_type
                        self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
                        
                        print(f"[CONFIG] Using database from config.ini: {self.DATABASE_PATH}")
                        return
                except Exception as e:
                    print(f"[CONFIG] Error reading config.ini: {e}, using default")
            
            # Desktop BEZ config.ini (testowanie przed instalacją)
            # Użyj AppData, NIE dist/data
            if sys.platform == "win32":
                import os
                appdata = Path(os.environ.get('APPDATA', Path.home()))
                db_dir = appdata / 'StrazakDesktopApp' / 'data'
            else:
                db_dir = Path.home() / '.strazak'
            
            db_dir.mkdir(parents=True, exist_ok=True)
            self.DATABASE_PATH = db_dir / "app.db"
            
            # Jeśli baza nie istnieje, skopiuj z bundle (_MEIPASS)
            if not self.DATABASE_PATH.exists():
                try:
                    if hasattr(sys, '_MEIPASS'):
                        source_db = Path(sys._MEIPASS) / "data" / "app.db"
                        if source_db.exists():
                            import shutil
                            shutil.copy2(source_db, self.DATABASE_PATH)
                            print(f"[CONFIG] Database copied from bundle to: {self.DATABASE_PATH}")
                except Exception as e:
                    print(f"[CONFIG] Error copying database: {e}")
            
            self.DATABASE_TYPE = 'local'
            self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
            print(f"[CONFIG] Desktop test mode - using: {self.DATABASE_PATH}")
            return
        
        # Web/Development - domyślna lokalizacja
        self.DATABASE_PATH = self.DATA_DIR / "app.db"
        self.DATABASE_TYPE = 'local'
        self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
        print(f"[CONFIG] Web/Dev mode - using: {self.DATABASE_PATH}")
    
    # CORS - dla developmentu
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Limity
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {".xlsx"}

settings = Settings()