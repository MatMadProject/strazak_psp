import sys
import os
from pathlib import Path
import configparser
import json

class Settings:
    # Podstawowa konfiguracja
    APP_NAME = "Strazak App"
    VERSION = "0.3.2"
    COMPANY = "MatMad Software"
    
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
        
        # Utwórz niezbędne foldery (tylko dla web/dev)
        if not self.IS_DESKTOP:
            self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Debug info
        print(f"[CONFIG] Mode: {'Desktop (PyInstaller)' if self.IS_DESKTOP else 'Web/Development'}")
        print(f"[CONFIG] Base dir: {self.BASE_DIR}")
        print(f"[CONFIG] Database: {self.DATABASE_PATH}")
        print(f"[CONFIG] Database type: {self.DATABASE_TYPE}")
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
        1. settings.json (zakładka Ustawienia - NAJWYŻSZY)
        2. config.ini (installer - custom instalacja)
        3. Domyślna lokalizacja (AppData dla desktop, data/ dla web)
        """
        
        # === DESKTOP ===
        if self.IS_DESKTOP:
            # PRIORYTET 1: settings.json w AppData (zakładka Ustawienia)
            if sys.platform == "win32":
                appdata = Path(os.environ.get('APPDATA', Path.home()))
                settings_json_path = appdata / 'StrazakDesktopApp' / 'settings.json'
            else:
                settings_json_path = Path.home() / '.strazak' / 'settings.json'
            
            if settings_json_path.exists():
                try:
                    with open(settings_json_path, 'r', encoding='utf-8') as f:
                        settings_data = json.load(f)
                    
                    db_config = settings_data.get('database', {})
                    db_type = db_config.get('type', 'local')
                    db_path = db_config.get('path')
                    
                    if db_path:
                        self.DATABASE_PATH = Path(db_path)
                        self.DATABASE_TYPE = db_type
                        self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
                        
                        print(f"[CONFIG] ✓ Using database from settings.json ({db_type})")
                        return
                except Exception as e:
                    print(f"[CONFIG] ⚠️ Error reading settings.json: {e}")
            
            # PRIORYTET 2: config.ini (installer - custom instalacja)
            config_ini_path = self.BASE_DIR / "config.ini"
            
            if config_ini_path.exists():
                try:
                    config = configparser.ConfigParser()
                    config.read(config_ini_path, encoding='utf-8')
                    
                    db_type = config.get('Database', 'Type', fallback='local')
                    db_path_str = config.get('Database', 'Path', fallback=None)
                    
                    if db_path_str:
                        self.DATABASE_PATH = Path(db_path_str)
                        self.DATABASE_TYPE = db_type
                        self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
                        
                        print(f"[CONFIG] ✓ Using database from config.ini ({db_type})")
                        return
                except Exception as e:
                    print(f"[CONFIG] ⚠️ Error reading config.ini: {e}")
            
            # PRIORYTET 3: Domyślna lokalizacja - ZAWSZE AppData!
            if sys.platform == "win32":
                appdata = Path(os.environ.get('APPDATA', Path.home()))
                db_dir = appdata / 'StrazakDesktopApp' / 'data'
            else:
                db_dir = Path.home() / '.strazak'
            
            db_dir.mkdir(parents=True, exist_ok=True)
            self.DATABASE_PATH = db_dir / "app.db"
            
            self.DATABASE_TYPE = 'local'
            self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
            print(f"[CONFIG] ✓ Using default location (AppData)")
            return
        
        # === WEB/DEVELOPMENT ===
        # PRIORYTET 1: settings.json w data/
        settings_json_path = self.DATA_DIR / "settings.json"
        
        if settings_json_path.exists():
            try:
                with open(settings_json_path, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                db_config = settings_data.get('database', {})
                db_path = db_config.get('path')
                
                if db_path:
                    self.DATABASE_PATH = Path(db_path)
                    self.DATABASE_TYPE = db_config.get('type', 'local')
                    self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
                    
                    print(f"[CONFIG] ✓ Using database from settings.json")
                    return
            except Exception as e:
                print(f"[CONFIG] ⚠️ Error reading settings.json: {e}")
        
        # PRIORYTET 2: Domyślna - data/app.db (OK dla development)
        self.DATABASE_PATH = self.DATA_DIR / "app.db"
        self.DATABASE_TYPE = 'local'
        self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"
        print(f"[CONFIG] ✓ Using default location (data/)")
    
    # CORS - dla developmentu
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Limity
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {".xlsx"}

settings = Settings()