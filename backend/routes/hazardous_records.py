"""
backend/routes/hazardous_records.py

Wzorowany na routes/files.py — identyczny styl uploadowania pliku.
Kluczowa różnica: używa ExcelProcessor.process_excel_file() →
get_zestawienie_szkodliwosci() (ten sam co Departures).

Zarejestruj w main.py:
  from routes.hazardous_records import router as hazardous_records_router
  app.include_router(hazardous_records_router, prefix="/api/hazardous-records", tags=["Hazardous Records"])
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import shutil
import uuid
import sys

sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from config import settings
from services.hazardous_records_service import HazardousRecordsService
from services.excel_processor import ExcelProcessor

router = APIRouter()
excel_processor = ExcelProcessor()


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class AssignDegreeRequest(BaseModel):
    hazardous_degree_id: Optional[int] = None  # None = odepnij

class AssignDegreeBulkRequest(BaseModel):
    record_ids: List[int]
    hazardous_degree_id: Optional[int] = None

class RecordUpdate(BaseModel):
    jednostka:               Optional[str] = None
    nazwisko_imie:           Optional[str] = None
    stopien:                 Optional[str] = None
    p:                       Optional[str] = None
    mz:                      Optional[str] = None
    af:                      Optional[str] = None
    nr_meldunku:             Optional[str] = None
    funkcja:                 Optional[str] = None
    czas_udzialu:            Optional[str] = None
    dodatek_szkodliwy:       Optional[str] = None
    stopien_szkodliwosci:    Optional[str] = None
    opis_st_szkodliwosci:    Optional[str] = None
    hazardous_degree_id:     Optional[int] = None


# ── PLIKI ────────────────────────────────────────────────────────────────────

@router.get("/files/")
def get_all_files(db: Session = Depends(get_db)):
    files = HazardousRecordsService.get_all_files(db)
    return {
        "files": [
            {
                "id":                f.id,
                "filename":          f.filename,
                "original_filename": f.original_filename,
                "imported_at":       f.imported_at.isoformat() if f.imported_at else None,
                "rows_count":        f.rows_count,
                "status":            getattr(f, "status", "completed"),
                "notes":             getattr(f, "notes", None),
            }
            for f in files
        ]
    }


@router.get("/files/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db)):
    file = HazardousRecordsService.get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    return {
        "id":                file.id,
        "filename":          file.filename,
        "original_filename": file.original_filename,
        "imported_at":       file.imported_at.isoformat() if file.imported_at else None,
        "rows_count":        file.rows_count,
        "status":            getattr(file, "status", "completed"),
    }


@router.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    success = HazardousRecordsService.delete_file(db, file_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    return {"success": True, "message": "Plik usunięty pomyślnie"}


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import pliku xlsx — identyczny flow jak routes/files.py:
      1. Zapisz plik tymczasowo
      2. ExcelProcessor.process_excel_file() → get_zestawienie_szkodliwosci()
      3. Utwórz ImportedFile
      4. HazardousRecordsService.create_records() z innymi polami niż DataService
      5. Usuń plik tymczasowy
    """
    file_path = None
    try:
        print(f"[HAZARDOUS UPLOAD] Plik: {file.filename}")

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".xlsx", ".xls"]:
            raise HTTPException(
                status_code=400,
                detail="Nieprawidłowe rozszerzenie. Dozwolone: .xlsx, .xls"
            )

        # Zapisz tymczasowo — identycznie jak routes/files.py
        unique_filename = f"hazardous_{uuid.uuid4()}{file_ext}"
        file_path = Path(settings.UPLOAD_DIR) / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Przetwórz — ten sam ExcelProcessor co Departures
        records_data = excel_processor.process_excel_file(file_path)

        if not records_data or not hasattr(records_data, "items") or len(records_data.items) == 0:
            raise HTTPException(status_code=400, detail="Nie znaleziono danych w pliku")

        records_count = len(records_data.items)

        # Utwórz rekord pliku
        file_record = HazardousRecordsService.create_file_record(
            db,
            filename=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            rows_count=records_count,
        )

        # Zapisz rekordy z mapowaniem pól szkodliwości
        created = HazardousRecordsService.create_records(db, file_record.id, records_data)

        return {
            "success":          True,
            "message":          f"Zaimportowano {created} rekordów",
            "file_id":          file_record.id,
            "filename":         file.filename,
            "records_imported": created,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[HAZARDOUS UPLOAD] BŁĄD: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Zawsze usuń plik tymczasowy — identycznie jak routes/files.py
        if file_path and Path(file_path).exists():
            Path(file_path).unlink()


# ── REKORDY ──────────────────────────────────────────────────────────────────

@router.get("/files/{file_id}/records")
def get_records(
    file_id: int,
    firefighter: Optional[str] = None,
    only_unassigned: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    records = HazardousRecordsService.get_records_by_file(
        db, file_id,
        skip=skip, limit=limit,
        firefighter=firefighter,
        only_unassigned=only_unassigned,
        sort_by=sort_by, sort_order=sort_order,
    )
    total = HazardousRecordsService.count_records_by_file(
        db, file_id,
        firefighter=firefighter,
        only_unassigned=only_unassigned,
    )
    return {
        "records":     [r.to_dict() for r in records],
        "total_count": total,
        "skip":        skip,
        "limit":       limit,
        "count":       len(records),
    }


@router.get("/files/{file_id}/statistics")
def get_statistics(file_id: int, db: Session = Depends(get_db)):
    return HazardousRecordsService.get_statistics(db, file_id)


@router.get("/files/{file_id}/firefighters")
def get_firefighters(file_id: int, db: Session = Depends(get_db)):
    """Unikalne nazwiska w pliku — do filtra dropdownu w HazardousList"""
    names = HazardousRecordsService.get_unique_firefighters_in_file(db, file_id)
    return {"firefighters": names}


@router.get("/records/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = HazardousRecordsService.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    return record.to_dict()


@router.put("/records/{record_id}")
def update_record(record_id: int, data: RecordUpdate, db: Session = Depends(get_db)):
    update_dict = {k: v for k, v in data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="Brak danych do aktualizacji")
    record = HazardousRecordsService.update_record(db, record_id, update_dict)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    return {"success": True, "record": record.to_dict()}


@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    success = HazardousRecordsService.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    return {"success": True, "message": "Rekord usunięty"}


@router.patch("/records/{record_id}/assign-degree")
def assign_degree(
    record_id: int,
    data: AssignDegreeRequest,
    db: Session = Depends(get_db)
):
    """
    Przypisz stopień szkodliwości do rekordu.
    hazardous_degree_id=null → odepnij stopień.
    """
    record = HazardousRecordsService.assign_degree(db, record_id, data.hazardous_degree_id)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    return {"success": True, "record": record.to_dict()}


@router.post("/records/assign-degree-bulk")
def assign_degree_bulk(data: AssignDegreeBulkRequest, db: Session = Depends(get_db)):
    """Przypisz stopień szkodliwości do wielu rekordów naraz"""
    updated = HazardousRecordsService.assign_degree_bulk(
        db, data.record_ids, data.hazardous_degree_id
    )
    return {"success": True, "updated_count": updated}