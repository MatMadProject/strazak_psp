from sqlalchemy.orm import Session
from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from models.swd_data import SWDRecord, ImportedFile

class DataService:
    """Serwis do zarządzania danymi SWD"""
    
    @staticmethod
    def get_all_files(db: Session) -> List[ImportedFile]:
        """Pobierz wszystkie zaimportowane pliki"""
        return db.query(ImportedFile).order_by(ImportedFile.imported_at.desc()).all()
    
    @staticmethod
    def get_file_by_id(db: Session, file_id: int) -> Optional[ImportedFile]:
        """Pobierz plik po ID"""
        return db.query(ImportedFile).filter(ImportedFile.id == file_id).first()
    
    @staticmethod
    def create_file_record(db: Session, filename: str, original_filename: str, 
                          file_path: str, rows_count: int) -> ImportedFile:
        """Utwórz rekord zaimportowanego pliku"""
        file_record = ImportedFile(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            rows_count=rows_count
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        return file_record
    
    @staticmethod
    def delete_file(db: Session, file_id: int) -> bool:
        """Usuń plik i wszystkie powiązane rekordy"""
        file_record = db.query(ImportedFile).filter(ImportedFile.id == file_id).first()
        if file_record:
            db.delete(file_record)
            db.commit()
            return True
        return False
    
    # --- Operacje na rekordach SWD ---
    
    @staticmethod
    def get_records_by_file(db: Session, file_id: int, 
                           skip: int = 0, limit: int = 100) -> List[SWDRecord]:
        """Pobierz rekordy dla danego pliku z paginacją"""
        return db.query(SWDRecord)\
            .filter(SWDRecord.file_id == file_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_all_records(db: Session, skip: int = 0, limit: int = 100) -> List[SWDRecord]:
        """Pobierz wszystkie rekordy z paginacją"""
        return db.query(SWDRecord)\
            .order_by(SWDRecord.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_record_by_id(db: Session, record_id: int) -> Optional[SWDRecord]:
        """Pobierz pojedynczy rekord"""
        return db.query(SWDRecord).filter(SWDRecord.id == record_id).first()
    
    @staticmethod
    def create_records(db: Session, file_id: int, records_data: List[dict]) -> int:
        """Utwórz wiele rekordów na raz"""
        created_count = 0
        for record_data in records_data:
            record = SWDRecord(
                file_id=file_id,
                **record_data
            )
            db.add(record)
            created_count += 1
        
        db.commit()
        return created_count
    
    @staticmethod
    def update_record(db: Session, record_id: int, update_data: dict) -> Optional[SWDRecord]:
        """Aktualizuj rekord"""
        record = db.query(SWDRecord).filter(SWDRecord.id == record_id).first()
        if record:
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete_record(db: Session, record_id: int) -> bool:
        """Usuń rekord"""
        record = db.query(SWDRecord).filter(SWDRecord.id == record_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False
    
    @staticmethod
    def search_records(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[SWDRecord]:
        """Wyszukaj rekordy"""
        return db.query(SWDRecord)\
            .filter(
                (SWDRecord.nazwa_swd.contains(query)) |
                (SWDRecord.kod_swd.contains(query)) |
                (SWDRecord.kategoria.contains(query))
            )\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_statistics(db: Session) -> dict:
        """Pobierz statystyki"""
        total_files = db.query(ImportedFile).count()
        total_records = db.query(SWDRecord).count()
        
        return {
            "total_files": total_files,
            "total_records": total_records,
            "avg_records_per_file": total_records / total_files if total_files > 0 else 0
        }