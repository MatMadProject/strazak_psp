"""
backend/services/hazardous_records_service.py

Wzorowany na DataService — identyczny styl i struktura metod.
Różnice vs DataService:
  - Model: HazardousRecord zamiast SWDRecord
  - create_records: mapuje INNE pola z ModelZestawienieWiersz
    (te dotyczące szkodliwości, nie samych wyjazdów)
  - Nowe metody: assign_degree, assign_degree_bulk, count z filtrem only_unassigned
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from models.swd_data import HazardousRecord, ImportedFile

try:
    from zestawienie_swd import CollectionZestawienieWiersz
except ImportError:
    CollectionZestawienieWiersz = None


class HazardousRecordsService:
    """Serwis do zarządzania danymi Dodatku Szkodliwego"""

    # ── Pliki — identycznie jak DataService ──────────────────────────────────

    @staticmethod
    def get_all_files(db: Session) -> List[ImportedFile]:
        return db.query(ImportedFile).order_by(ImportedFile.imported_at.desc()).all()

    @staticmethod
    def get_file_by_id(db: Session, file_id: int) -> Optional[ImportedFile]:
        return db.query(ImportedFile).filter(ImportedFile.id == file_id).first()

    @staticmethod
    def create_file_record(
        db: Session,
        filename: str,
        original_filename: str,
        file_path: str,
        rows_count: int
    ) -> ImportedFile:
        file_record = ImportedFile(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            rows_count=rows_count,
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        return file_record

    @staticmethod
    def delete_file(db: Session, file_id: int) -> bool:
        file_record = db.query(ImportedFile).filter(ImportedFile.id == file_id).first()
        if file_record:
            db.delete(file_record)
            db.commit()
            return True
        return False

    # ── Rekordy — odczyt ─────────────────────────────────────────────────────

    @staticmethod
    def get_records_by_file(
        db: Session,
        file_id: int,
        skip: int = 0,
        limit: int = 100,
        firefighter: str = None,
        only_unassigned: bool = False,
        sort_by: str = None,
        sort_order: str = "asc",
    ) -> List[HazardousRecord]:
        query = db.query(HazardousRecord).filter(HazardousRecord.file_id == file_id)

        if firefighter:
            query = query.filter(HazardousRecord.nazwisko_imie == firefighter)

        if only_unassigned:
            query = query.filter(HazardousRecord.hazardous_degree_id == None)

        if sort_by:
            col = getattr(HazardousRecord, sort_by, None)
            if col is not None:
                query = query.order_by(col.desc() if sort_order == "desc" else col.asc())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_records_by_file(
        db: Session,
        file_id: int,
        firefighter: str = None,
        only_unassigned: bool = False,
    ) -> int:
        query = db.query(func.count(HazardousRecord.id)).filter(
            HazardousRecord.file_id == file_id
        )
        if firefighter:
            query = query.filter(HazardousRecord.nazwisko_imie == firefighter)
        if only_unassigned:
            query = query.filter(HazardousRecord.hazardous_degree_id == None)
        return query.scalar()

    @staticmethod
    def get_record_by_id(db: Session, record_id: int) -> Optional[HazardousRecord]:
        return db.query(HazardousRecord).filter(HazardousRecord.id == record_id).first()

    @staticmethod
    def get_unique_firefighters_in_file(db: Session, file_id: int) -> List[str]:
        """Identyczna metoda jak DataService.get_unique_firefighters_in_file"""
        result = (
            db.query(HazardousRecord.nazwisko_imie)
            .filter(HazardousRecord.file_id == file_id)
            .distinct()
            .order_by(HazardousRecord.nazwisko_imie)
            .all()
        )
        return [r[0] for r in result if r[0]]

    # ── Rekordy — zapis ──────────────────────────────────────────────────────

    @staticmethod
    def create_records(db: Session, file_id: int, records_data) -> int:
        """
        Tworzy rekordy z CollectionZestawienieWiersz.
        Wzorzec identyczny jak DataService.create_records —
        ale mapujemy INNE pola: te dotyczące szkodliwości.

        Pola z ModelZestawienieWiersz które używamy:
          jednostka, stopien, nazwisko_imie, data_przyjecia,
          p, mz, af, nr_meldunku, funkcja,
          czas_od, czas_do, czas_udzialu,
          dodatek_szkodliwy, stopien_szkodliwosci,
          aktualizowal_szkod, data_aktualizacji_szkod, opis_st_szkodliwosci
        """
        created_count = 0
        try:
            if hasattr(records_data, "items"):
                # CollectionZestawienieWiersz — identyczny pattern jak DataService
                print(f"[HAZARDOUS SERVICE] Tworzenie {len(records_data.items)} rekordów")

                for row in records_data.items:
                    record = HazardousRecord(
                        file_id=file_id,
                        jednostka               = str(row.jednostka)               if row.jednostka               else None,
                        nazwisko_imie           = str(row.nazwisko_imie)           if row.nazwisko_imie           else None,
                        stopien                 = str(row.stopien)                 if row.stopien                 else None,
                        data_przyjecia          = row.data_przyjecia               if row.data_przyjecia           else None,
                        p                       = str(row.p)                       if row.p                       else None,
                        mz                      = str(row.mz)                      if row.mz                      else None,
                        af                      = str(row.af)                      if row.af                      else None,
                        nr_meldunku             = str(row.nr_meldunku)             if row.nr_meldunku             else None,
                        funkcja                 = str(row.funkcja)                 if row.funkcja                 else None,
                        czas_od                 = row.czas_od                      if row.czas_od                 else None,
                        czas_do                 = row.czas_do                      if row.czas_do                 else None,
                        czas_udzialu            = str(row.czas_udzialu)            if row.czas_udzialu            else None,
                        dodatek_szkodliwy       = str(row.dodatek_szkodliwy)       if row.dodatek_szkodliwy       else None,
                        stopien_szkodliwosci    = str(row.stopien_szkodliwosci)    if row.stopien_szkodliwosci    else None,
                        aktualizowal_szkod      = str(row.aktualizowal_szkod)      if row.aktualizowal_szkod      else None,
                        data_aktualizacji_szkod = row.data_aktualizacji_szkod      if row.data_aktualizacji_szkod else None,
                        opis_st_szkodliwosci    = str(row.opis_st_szkodliwosci)    if row.opis_st_szkodliwosci    else None,
                        # hazardous_degree_id — None przy imporcie, przypisywane ręcznie
                        hazardous_degree_id     = None,
                    )
                    db.add(record)
                    created_count += 1
            else:
                # Fallback: lista słowników (jak DataService)
                for record_data in records_data:
                    db.add(HazardousRecord(file_id=file_id, **record_data))
                    created_count += 1

            db.commit()
            print(f"[HAZARDOUS SERVICE] Utworzono {created_count} rekordów")
            return created_count

        except Exception as e:
            print(f"[HAZARDOUS SERVICE] Błąd tworzenia rekordów: {e}")
            db.rollback()
            raise

    @staticmethod
    def update_record(db: Session, record_id: int, update_data: dict) -> Optional[HazardousRecord]:
        """Identyczna metoda jak DataService.update_record"""
        record = db.query(HazardousRecord).filter(HazardousRecord.id == record_id).first()
        if record:
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            db.commit()
            db.refresh(record)
        return record

    @staticmethod
    def delete_record(db: Session, record_id: int) -> bool:
        """Identyczna metoda jak DataService.delete_record"""
        record = db.query(HazardousRecord).filter(HazardousRecord.id == record_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False

    # ── Przypisanie stopnia — nowa logika biznesowa ──────────────────────────

    @staticmethod
    def assign_degree(
        db: Session,
        record_id: int,
        hazardous_degree_id: Optional[int]
    ) -> Optional[HazardousRecord]:
        """
        Przypisz (lub odepnij gdy None) stopień szkodliwości do rekordu.
        Główna operacja biznesowa — użytkownik wybiera z dropdownu.
        """
        record = db.query(HazardousRecord).filter(HazardousRecord.id == record_id).first()
        if record:
            record.hazardous_degree_id = hazardous_degree_id
            db.commit()
            db.refresh(record)
        return record

    @staticmethod
    def assign_degree_bulk(
        db: Session,
        record_ids: List[int],
        hazardous_degree_id: Optional[int]
    ) -> int:
        """Przypisz stopień szkodliwości do wielu rekordów naraz"""
        records = (
            db.query(HazardousRecord)
            .filter(HazardousRecord.id.in_(record_ids))
            .all()
        )
        for record in records:
            record.hazardous_degree_id = hazardous_degree_id
        db.commit()
        return len(records)

    # ── Statystyki ───────────────────────────────────────────────────────────

    @staticmethod
    def get_statistics(db: Session, file_id: int) -> dict:
        total = HazardousRecordsService.count_records_by_file(db, file_id)
        assigned = (
            db.query(func.count(HazardousRecord.id))
            .filter(
                HazardousRecord.file_id == file_id,
                HazardousRecord.hazardous_degree_id != None,
            )
            .scalar()
        )
        return {
            "total_records":    total,
            "assigned_count":   assigned,
            "unassigned_count": total - assigned,
        }