from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from services.data_service import DataService

router = APIRouter(prefix="/api/data", tags=["data"])

# Pydantic models dla request/response
class RecordUpdate(BaseModel):
    nazwisko_imie: Optional[str] = None
    stopien: Optional[str] = None
    p: Optional[str] = None
    mz: Optional[str] = None
    af: Optional[str] = None
    zaliczono_do_emerytury: Optional[str] = None
    nr_meldunku: Optional[str] = None
    czas_rozp_zdarzenia: Optional[str] = None
    funkcja: Optional[str] = None

@router.get("/records")
def get_records(
    file_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Pobierz rekordy z opcjonalnym filtrowaniem
    - file_id: filtruj po pliku
    - search: wyszukaj w nazwach, kodach, kategoriach
    - skip, limit: paginacja
    """
    if search:
        records = DataService.search_records(db, search, skip, limit)
    elif file_id:
        records = DataService.get_records_by_file(db, file_id, skip, limit)
    else:
        records = DataService.get_all_records(db, skip, limit)
    
    return {
        "records": [record.to_dict() for record in records],
        "skip": skip,
        "limit": limit,
        "count": len(records)
    }

@router.get("/records/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):
    """Pobierz pojedynczy rekord"""
    record = DataService.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    
    return record.to_dict()

@router.put("/records/{record_id}")
def update_record(
    record_id: int,
    update_data: RecordUpdate,
    db: Session = Depends(get_db)
):
    """Aktualizuj rekord"""
    # Usuń None wartości
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Brak danych do aktualizacji")
    
    record = DataService.update_record(db, record_id, update_dict)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    
    return {
        "success": True,
        "message": "Rekord zaktualizowany",
        "record": record.to_dict()
    }

@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Usuń rekord"""
    success = DataService.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    
    return {"success": True, "message": "Rekord usunięty"}

@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Pobierz statystyki aplikacji"""
    stats = DataService.get_statistics(db)
    return stats

@router.get("/files/{file_id}/firefighters")
def get_firefighters_in_file(file_id: int, db: Session = Depends(get_db)):
    """Pobierz listę unikalnych strażaków z danego pliku"""
    firefighters = DataService.get_unique_firefighters_in_file(db, file_id)
    return {"firefighters": firefighters}

@router.get("/files/{file_id}/records")
def get_file_records(
    file_id: int,
    firefighter: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = 'asc',
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Pobierz rekordy z danego pliku
    - firefighter: filtruj po strażaku (nazwisko_imie)
    - sort_by: sortuj po kolumnie (nazwisko_imie, funkcja, nr_meldunku, czas_rozp_zdarzenia, etc.)
    - sort_order: kierunek sortowania (asc, desc)
    - skip, limit: paginacja
    """
    if firefighter:
        records = DataService.get_records_by_file_and_firefighter(
            db, file_id, firefighter, skip, limit, sort_by, sort_order
        )
    else:
        records = DataService.get_records_by_file(
            db, file_id, skip, limit, sort_by, sort_order
        )
    
    return {
        "records": [record.to_dict() for record in records],
        "file_id": file_id,
        "skip": skip,
        "limit": limit,
        "count": len(records)
    }

@router.post("/files/{file_id}/records")
def create_record(
    file_id: int,
    record_data: RecordUpdate,
    db: Session = Depends(get_db)
):
    """Utwórz nowy rekord w pliku"""
    # Sprawdź czy plik istnieje
    from services.data_service import DataService
    file_record = DataService.get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    
    # Przygotuj dane (usuń None wartości)
    create_dict = {k: v for k, v in record_data.dict().items() if v is not None}
    
    if not create_dict:
        raise HTTPException(status_code=400, detail="Brak danych do zapisania")
    
    # Sprawdź wymagane pola
    if not create_dict.get('nazwisko_imie'):
        raise HTTPException(status_code=400, detail="Pole 'Nazwisko i Imię' jest wymagane")
    
    if not create_dict.get('nr_meldunku'):
        raise HTTPException(status_code=400, detail="Pole 'Nr meldunku' jest wymagane")
    
    # Sprawdź duplikaty
    existing_record = DataService.check_duplicate_record(
        db, 
        file_id, 
        create_dict['nazwisko_imie'], 
        create_dict['nr_meldunku']
    )
    
    if existing_record:
        raise HTTPException(
            status_code=409,  # 409 Conflict
            detail=f"Rekord dla '{create_dict['nazwisko_imie']}' z meldunkiem '{create_dict['nr_meldunku']}' już istnieje w tym pliku"
        )
    
    # Dodaj file_id do danych
    create_dict['file_id'] = file_id
    
    # Utwórz rekord
    record = DataService.create_single_record(db, create_dict)
    
    return {
        "success": True,
        "message": "Rekord utworzony pomyślnie",
        "record": record.to_dict()
    }