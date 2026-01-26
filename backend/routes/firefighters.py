from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import shutil
import uuid
import sys

sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from config import settings
from services.firefighter_service import FirefighterService
from services.firefighter_excel_service import FirefighterExcelService

router = APIRouter(prefix="/api/firefighters", tags=["firefighters"])

# Inicjalizacja serwisu Excel
excel_service = FirefighterExcelService()

# Pydantic models
class FirefighterCreate(BaseModel):
    nazwisko_imie: str
    stopien: str
    stanowisko: str
    jednostka: str

class FirefighterUpdate(BaseModel):
    nazwisko_imie: Optional[str] = None
    stopien: Optional[str] = None
    stanowisko: Optional[str] = None
    jednostka: Optional[str] = None

@router.get("/")
def get_firefighters(
    search: Optional[str] = None,
    jednostka: Optional[str] = None,
    stopien: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Pobierz listę strażaków z opcjonalnym filtrowaniem
    - search: wyszukaj w nazwiskach, stopniach, stanowiskach, jednostkach
    - jednostka: filtruj po jednostce
    - stopien: filtruj po stopniu
    - skip, limit: paginacja
    """
    if search:
        firefighters = FirefighterService.search_firefighters(db, search, skip, limit)
    elif jednostka:
        firefighters = FirefighterService.get_firefighters_by_unit(db, jednostka, skip, limit)
    elif stopien:
        firefighters = FirefighterService.get_firefighters_by_rank(db, stopien, skip, limit)
    else:
        firefighters = FirefighterService.get_all_firefighters(db, skip, limit)
    
    return {
        "firefighters": [ff.to_dict() for ff in firefighters],
        "skip": skip,
        "limit": limit,
        "count": len(firefighters)
    }

@router.get("/statistics")
def get_firefighter_statistics(db: Session = Depends(get_db)):
    """Pobierz statystyki strażaków"""
    stats = FirefighterService.get_statistics(db)
    return stats

@router.get("/{firefighter_id}")
def get_firefighter(firefighter_id: int, db: Session = Depends(get_db)):
    """Pobierz pojedynczego strażaka"""
    firefighter = FirefighterService.get_firefighter_by_id(db, firefighter_id)
    if not firefighter:
        raise HTTPException(status_code=404, detail="Strażak nie znaleziony")
    
    return firefighter.to_dict()

@router.post("/")
def create_firefighter(
    firefighter_data: FirefighterCreate,
    db: Session = Depends(get_db)
):
    """Utwórz nowego strażaka"""
    try:
        firefighter = FirefighterService.create_firefighter(
            db, 
            firefighter_data.dict()
        )
        return {
            "success": True,
            "message": "Strażak został dodany",
            "firefighter": firefighter.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{firefighter_id}")
def update_firefighter(
    firefighter_id: int,
    update_data: FirefighterUpdate,
    db: Session = Depends(get_db)
):
    """Aktualizuj dane strażaka"""
    # Usuń None wartości
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Brak danych do aktualizacji")
    
    firefighter = FirefighterService.update_firefighter(db, firefighter_id, update_dict)
    if not firefighter:
        raise HTTPException(status_code=404, detail="Strażak nie znaleziony")
    
    return {
        "success": True,
        "message": "Dane strażaka zaktualizowane",
        "firefighter": firefighter.to_dict()
    }

@router.delete("/{firefighter_id}")
def delete_firefighter(firefighter_id: int, db: Session = Depends(get_db)):
    """Usuń strażaka"""
    success = FirefighterService.delete_firefighter(db, firefighter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strażak nie znaleziony")
    
    return {
        "success": True,
        "message": "Strażak został usunięty"
    }

@router.get("/template/download")
def download_template():
    """Pobierz pusty szablon Excel do importu strażaków"""
    try:
        file_content = excel_service.create_template_file()
        
        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=szablon_strazacy.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importuj strażaków z pliku Excel
    """
    try:
        print(f"📁 Otrzymano plik: {file.filename}")
        
        # Walidacja rozszerzenia
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.xlsx', '.xls']:
            raise HTTPException(
                status_code=400,
                detail="Nieprawidłowe rozszerzenie pliku. Dozwolone: .xlsx, .xls"
            )
        
        # Generuj unikalną nazwę pliku
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = settings.UPLOAD_DIR / unique_filename
        
        # Zapisz plik
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Plik zapisany: {file_path}")
        
        # Przetwórz plik
        firefighters_data = excel_service.process_excel_file(file_path)
        
        if not firefighters_data:
            raise HTTPException(
                status_code=400,
                detail="Nie znaleziono prawidłowych danych w pliku"
            )
        
        # Zapisz strażaków do bazy
        created_count = 0
        skipped_count = 0
        errors = []
        
        for firefighter_data in firefighters_data:
            try:
                FirefighterService.create_firefighter(db, firefighter_data)
                created_count += 1
            except Exception as e:
                skipped_count += 1
                errors.append(f"{firefighter_data.get('nazwisko_imie', 'Unknown')}: {str(e)}")
        
        # Usuń plik po przetworzeniu
        if file_path.exists():
            file_path.unlink()
        
        return {
            "success": True,
            "message": f"Zaimportowano {created_count} strażaków",
            "created_count": created_count,
            "skipped_count": skipped_count,
            "errors": errors if errors else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # W przypadku błędu, usuń plik
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        
        print(f"❌ BŁĄD: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/excel")
def export_to_excel(
    search: Optional[str] = None,
    jednostka: Optional[str] = None,
    stopien: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Eksportuj strażaków do pliku Excel
    Obsługuje te same filtry co endpoint listowania
    """
    try:
        # Pobierz strażaków z filtrami (bez limitów paginacji)
        if search:
            firefighters = FirefighterService.search_firefighters(db, search, skip=0, limit=10000)
        elif jednostka:
            firefighters = FirefighterService.get_firefighters_by_unit(db, jednostka, skip=0, limit=10000)
        elif stopien:
            firefighters = FirefighterService.get_firefighters_by_rank(db, stopien, skip=0, limit=10000)
        else:
            firefighters = FirefighterService.get_all_firefighters(db, skip=0, limit=10000)
        
        if not firefighters:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")
        
        # Konwertuj do słowników
        firefighters_data = [ff.to_dict() for ff in firefighters]
        
        # Generuj plik Excel
        file_content = excel_service.export_to_excel(firefighters_data)
        
        from datetime import datetime
        filename = f"strazacy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ BŁĄD EKSPORTU EXCEL: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
def export_to_csv(
    search: Optional[str] = None,
    jednostka: Optional[str] = None,
    stopien: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Eksportuj strażaków do pliku CSV
    Obsługuje te same filtry co endpoint listowania
    """
    try:
        # Pobierz strażaków z filtrami (bez limitów paginacji)
        if search:
            firefighters = FirefighterService.search_firefighters(db, search, skip=0, limit=10000)
        elif jednostka:
            firefighters = FirefighterService.get_firefighters_by_unit(db, jednostka, skip=0, limit=10000)
        elif stopien:
            firefighters = FirefighterService.get_firefighters_by_rank(db, stopien, skip=0, limit=10000)
        else:
            firefighters = FirefighterService.get_all_firefighters(db, skip=0, limit=10000)
        
        if not firefighters:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")
        
        # Konwertuj do słowników
        firefighters_data = [ff.to_dict() for ff in firefighters]
        
        # Generuj plik CSV
        file_content = excel_service.export_to_csv(firefighters_data)
        
        from datetime import datetime
        filename = f"strazacy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            file_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ BŁĄD EKSPORTU CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))