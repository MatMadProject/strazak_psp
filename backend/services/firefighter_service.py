from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from models.swd_data import Firefighter

class FirefighterService:
    """Serwis do zarządzania danymi strażaków"""
    
    @staticmethod
    def get_all_firefighters(db: Session, skip: int = 0, limit: int = 100) -> List[Firefighter]:
        """Pobierz wszystkich strażaków z paginacją"""
        return db.query(Firefighter)\
            .order_by(Firefighter.nazwisko_imie)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_firefighter_by_id(db: Session, firefighter_id: int) -> Optional[Firefighter]:
        """Pobierz strażaka po ID"""
        return db.query(Firefighter).filter(Firefighter.id == firefighter_id).first()
    
    @staticmethod
    def create_firefighter(db: Session, firefighter_data: dict) -> Firefighter:
        """Utwórz nowego strażaka"""
        firefighter = Firefighter(**firefighter_data)
        db.add(firefighter)
        db.commit()
        db.refresh(firefighter)
        return firefighter
    
    @staticmethod
    def update_firefighter(db: Session, firefighter_id: int, update_data: dict) -> Optional[Firefighter]:
        """Aktualizuj dane strażaka"""
        firefighter = db.query(Firefighter).filter(Firefighter.id == firefighter_id).first()
        if firefighter:
            for key, value in update_data.items():
                if hasattr(firefighter, key) and value is not None:
                    setattr(firefighter, key, value)
            db.commit()
            db.refresh(firefighter)
        return firefighter
    
    @staticmethod
    def delete_firefighter(db: Session, firefighter_id: int) -> bool:
        """Usuń strażaka"""
        firefighter = db.query(Firefighter).filter(Firefighter.id == firefighter_id).first()
        if firefighter:
            db.delete(firefighter)
            db.commit()
            return True
        return False
    
    @staticmethod
    def search_firefighters(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Firefighter]:
        """Wyszukaj strażaków"""
        return db.query(Firefighter)\
            .filter(
                (Firefighter.nazwisko_imie.contains(query)) |
                (Firefighter.stopien.contains(query)) |
                (Firefighter.stanowisko.contains(query)) |
                (Firefighter.jednostka.contains(query))
            )\
            .order_by(Firefighter.nazwisko_imie)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """Pobierz statystyki strażaków"""
        total_firefighters = db.query(Firefighter).count()
        
        # Statystyki według stopni
        by_rank = db.query(
            Firefighter.stopien,
            func.count(Firefighter.id).label('count')
        ).group_by(Firefighter.stopien).all()
        
        # Statystyki według jednostek
        by_unit = db.query(
            Firefighter.jednostka,
            func.count(Firefighter.id).label('count')
        ).group_by(Firefighter.jednostka).all()
        
        return {
            "total_firefighters": total_firefighters,
            "by_rank": [{"rank": rank, "count": count} for rank, count in by_rank],
            "by_unit": [{"unit": unit, "count": count} for unit, count in by_unit]
        }
    
    @staticmethod
    def get_firefighters_by_unit(db: Session, jednostka: str, skip: int = 0, limit: int = 100) -> List[Firefighter]:
        """Pobierz strażaków z danej jednostki"""
        return db.query(Firefighter)\
            .filter(Firefighter.jednostka == jednostka)\
            .order_by(Firefighter.nazwisko_imie)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_firefighters_by_rank(db: Session, stopien: str, skip: int = 0, limit: int = 100) -> List[Firefighter]:
        """Pobierz strażaków z danym stopniem"""
        return db.query(Firefighter)\
            .filter(Firefighter.stopien == stopien)\
            .order_by(Firefighter.nazwisko_imie)\
            .offset(skip)\
            .limit(limit)\
            .all()