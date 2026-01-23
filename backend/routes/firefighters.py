from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from services.firefighter_service import FirefighterService

router = APIRouter(prefix="/api/firefighters", tags=["firefighters"])

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