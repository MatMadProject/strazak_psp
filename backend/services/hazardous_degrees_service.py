"""
backend/services/hazardous_degrees_service.py

Serwis do zarządzania stopniami szkodliwości.
Wzorowany na FirefighterService - zachowuje identyczny styl.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from models.swd_data import HazardousDegree


class HazardousDegreesService:
    """Serwis do zarządzania danymi stopni szkodliwości"""

    # ── Odczyt ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[HazardousDegree]:
        """Pobierz wszystkie stopnie z paginacją, posortowane stopień → punkt"""
        return (
            db.query(HazardousDegree)
            .order_by(HazardousDegree.stopien, HazardousDegree.punkt)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, record_id: int) -> Optional[HazardousDegree]:
        return db.query(HazardousDegree).filter(HazardousDegree.id == record_id).first()

    @staticmethod
    def search(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[HazardousDegree]:
        """Wyszukaj w opisie i uwagach"""
        return (
            db.query(HazardousDegree)
            .filter(
                or_(
                    HazardousDegree.opis.contains(query),
                    HazardousDegree.uwagi.contains(query),
                )
            )
            .order_by(HazardousDegree.stopien, HazardousDegree.punkt)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_stopien(
        db: Session,
        stopien: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[HazardousDegree]:
        """Pobierz wszystkie punkty danego stopnia"""
        return (
            db.query(HazardousDegree)
            .filter(HazardousDegree.stopien == stopien)
            .order_by(HazardousDegree.punkt)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_total_count(db: Session, search: str = None, stopien: int = None) -> int:
        """Łączna liczba rekordów (do paginacji)"""
        q = db.query(func.count(HazardousDegree.id))
        if search:
            q = q.filter(
                or_(
                    HazardousDegree.opis.contains(search),
                    HazardousDegree.uwagi.contains(search),
                )
            )
        if stopien is not None:
            q = q.filter(HazardousDegree.stopien == stopien)
        return q.scalar()

    # ── Zapis ───────────────────────────────────────────────────────────────

    @staticmethod
    def create(db: Session, data: dict) -> HazardousDegree:
        """Utwórz nowy stopień szkodliwości"""
        record = HazardousDegree(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update(db: Session, record_id: int, data: dict) -> Optional[HazardousDegree]:
        """Aktualizuj istniejący rekord"""
        record = db.query(HazardousDegree).filter(HazardousDegree.id == record_id).first()
        if record:
            for key, value in data.items():
                if hasattr(record, key) and value is not None:
                    setattr(record, key, value)
            db.commit()
            db.refresh(record)
        return record

    @staticmethod
    def delete(db: Session, record_id: int) -> bool:
        """Usuń rekord"""
        record = db.query(HazardousDegree).filter(HazardousDegree.id == record_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False

    # ── Statystyki ──────────────────────────────────────────────────────────

    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """Statystyki - łączna liczba, rozkład po stopniach"""
        total = db.query(HazardousDegree).count()

        by_degree = (
            db.query(
                HazardousDegree.stopien,
                func.count(HazardousDegree.id).label("count")
            )
            .group_by(HazardousDegree.stopien)
            .order_by(HazardousDegree.stopien)
            .all()
        )

        return {
            "total_records": total,
            "by_degree": [
                {"stopien": stopien, "count": count}
                for stopien, count in by_degree
            ],
        }