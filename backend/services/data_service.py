from sqlalchemy.orm import Session
from typing import List, Optional, Union
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from models.swd_data import SWDRecord, ImportedFile

# Import dla type hinting
try:
    from zestawienie_swd import CollectionZestawienieWiersz
except ImportError:
    CollectionZestawienieWiersz = None

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
                           skip: int = 0, limit: int = 100,
                           sort_by: str = None, sort_order: str = 'asc') -> List[SWDRecord]:
        """Pobierz rekordy dla danego pliku z paginacją i sortowaniem"""
        query = db.query(SWDRecord).filter(SWDRecord.file_id == file_id)
        
        # Sortowanie
        if sort_by:
            column = getattr(SWDRecord, sort_by, None)
            if column is not None:
                if sort_order == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_records_by_file_and_firefighter(db: Session, file_id: int, 
                                            nazwisko_imie: str,
                                            skip: int = 0, limit: int = 100,
                                            sort_by: str = None, sort_order: str = 'asc') -> List[SWDRecord]:
        """Pobierz rekordy dla danego pliku i strażaka z sortowaniem"""
        query = db.query(SWDRecord).filter(
            SWDRecord.file_id == file_id,
            SWDRecord.nazwisko_imie == nazwisko_imie
        )
        
        # Sortowanie
        if sort_by:
            column = getattr(SWDRecord, sort_by, None)
            if column is not None:
                if sort_order == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_unique_firefighters_in_file(db: Session, file_id: int) -> List[str]:
        """Pobierz unikalne nazwiska strażaków z danego pliku"""
        result = db.query(SWDRecord.nazwisko_imie)\
            .filter(SWDRecord.file_id == file_id)\
            .distinct()\
            .order_by(SWDRecord.nazwisko_imie)\
            .all()
        return [r[0] for r in result if r[0]]
    
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
    def create_records(db: Session, file_id: int, records_data) -> int:
        """
        Utwórz wiele rekordów na raz
        Akceptuje zarówno CollectionZestawienieWiersz jak i listę słowników
        """
        created_count = 0
        
        try:
            # Sprawdź czy to CollectionZestawienieWiersz z biblioteki
            if hasattr(records_data, 'items'):
                # To jest CollectionZestawienieWiersz
                print(f"📝 [DATA SERVICE] Tworzenie {len(records_data.items)} rekordów z CollectionZestawienieWiersz")
                
                for record_data in records_data.items:
                    record = SWDRecord(
                        file_id=file_id,
                        nazwisko_imie=str(record_data.nazwisko_imie) if record_data.nazwisko_imie else None,
                        stopien=str(record_data.stopien) if record_data.stopien else None,
                        p=str(record_data.p) if record_data.p else None,
                        mz=str(record_data.mz) if record_data.mz else None,
                        af=str(record_data.af) if record_data.af else None,
                        zaliczono_do_emerytury=str(record_data.zaliczono_do_emerytury) if record_data.zaliczono_do_emerytury else None,
                        nr_meldunku=str(record_data.nr_meldunku) if record_data.nr_meldunku else None,
                        czas_rozp_zdarzenia=str(record_data.czas_rozp_zdarzenia) if record_data.czas_rozp_zdarzenia else None,
                        funkcja=str(record_data.funkcja) if record_data.funkcja else None
                    )
                    db.add(record)
                    created_count += 1
            else:
                # To jest lista słowników (fallback dla starszego kodu)
                print(f"📝 [DATA SERVICE] Tworzenie {len(records_data)} rekordów ze słowników")
                
                for record_data in records_data:
                    record = SWDRecord(
                        file_id=file_id,
                        **record_data
                    )
                    db.add(record)
                    created_count += 1
            
            db.commit()
            print(f"✅ [DATA SERVICE] Utworzono {created_count} rekordów")
            return created_count
            
        except Exception as e:
            print(f"❌ [DATA SERVICE] Błąd tworzenia rekordów: {e}")
            db.rollback()
            raise
    
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
                (SWDRecord.nazwisko_imie.contains(query)) |
                (SWDRecord.nr_meldunku.contains(query)) |
                (SWDRecord.funkcja.contains(query))
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