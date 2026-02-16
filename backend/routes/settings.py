from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import sys
import os

router = APIRouter()

class DatabaseSettings(BaseModel):
    type: str  # "local" or "network"
    path: str

class AppSettings(BaseModel):
    database: DatabaseSettings

def get_settings_path() -> Path:
    """Pobierz ścieżkę do pliku ustawień"""
    if getattr(sys, "frozen", False):
        # Desktop - obok exe
        return Path(sys.executable).parent / "settings.json"
    else:
        # Web/Development - w folderze data/
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)  # Utwórz jeśli nie istnieje
        return data_dir / "settings.json"

@router.get("/")
async def get_settings():
    """Pobierz aktualne ustawienia"""
    try:
        settings_path = get_settings_path()
        
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings
        else:
            # Domyślne ustawienia
            from config import settings as app_settings
            return {
                "database": {
                    "type": app_settings.DATABASE_TYPE,
                    "path": str(app_settings.DATABASE_PATH)
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def update_settings(settings: AppSettings):
    """Zaktualizuj ustawienia"""
    try:
        settings_path = get_settings_path()
        
        # Walidacja ścieżki
        db_path = Path(settings.database.path)
        
        if settings.database.type == "network":
            # Sprawdź czy ścieżka UNC
            if not str(db_path).startswith("\\\\"):
                raise HTTPException(
                    status_code=400, 
                    detail="Ścieżka sieciowa musi zaczynać się od \\\\"
                )
        
        # Sprawdź czy folder istnieje
        db_dir = db_path.parent
        if not db_dir.exists() and settings.database.type == "local":
            raise HTTPException(
                status_code=400,
                detail=f"Folder nie istnieje: {db_dir}"
            )
        
        # Zapisz ustawienia
        settings_dict = settings.dict()
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Ustawienia zapisane. Uruchom ponownie aplikację, aby zastosować zmiany.",
            "settings": settings_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-database")
async def get_current_database():
    """Pobierz aktualnie używaną bazę danych"""
    from config import settings as app_settings
    
    return {
        "type": app_settings.DATABASE_TYPE,
        "path": str(app_settings.DATABASE_PATH),
        "exists": app_settings.DATABASE_PATH.exists()
    }
@router.get("/browse-database")
@router.get("/browse-database/")
async def browse_database():
    """Otwórz dialog wyboru pliku bazy danych (tylko desktop)"""
    try:
        import webview
        
        # Otwórz dialog wyboru pliku
        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=('Baza danych SQLite (*.db)', 'Wszystkie pliki (*.*)')
        )
        
        if result and len(result) > 0:
            return {"path": result[0]}
        else:
            return {"path": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd dialogu: {str(e)}")

@router.get("/browse-folder")
@router.get("/browse-folder/")
async def browse_folder():
    """Otwórz dialog wyboru folderu (tylko desktop)"""
    try:
        import webview
        
        # Otwórz dialog wyboru folderu
        result = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG
        )
        
        if result and len(result) > 0:
            # Dodaj nazwę pliku app.db
            from pathlib import Path
            folder_path = Path(result[0])
            db_path = folder_path / "app.db"
            return {"path": str(db_path)}
        else:
            return {"path": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd dialogu: {str(e)}")