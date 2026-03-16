"""
backend/routes/hazardous_records.py
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
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
    hazardous_degree_id: Optional[int] = None

class AssignDegreeBulkRequest(BaseModel):
    record_ids: List[int]
    hazardous_degree_id: Optional[int] = None

class RecordCreate(BaseModel):
    file_id:                 int
    jednostka:               Optional[str] = None
    nazwisko_imie:           Optional[str] = None
    stopien:                 Optional[str] = None
    p:                       Optional[str] = None
    mz:                      Optional[str] = None
    af:                      Optional[str] = None
    nr_meldunku:             Optional[str] = None
    funkcja:                 Optional[str] = None
    czas_od:                 Optional[str] = None
    czas_do:                 Optional[str] = None
    czas_udzialu:            Optional[str] = None
    dodatek_szkodliwy:       Optional[str] = None
    stopien_szkodliwosci:    Optional[str] = None
    opis_st_szkodliwosci:    Optional[str] = None
    hazardous_degree_id:     Optional[int] = None

class RecordUpdate(BaseModel):
    jednostka:               Optional[str] = None
    nazwisko_imie:           Optional[str] = None
    stopien:                 Optional[str] = None
    p:                       Optional[str] = None
    mz:                      Optional[str] = None
    af:                      Optional[str] = None
    nr_meldunku:             Optional[str] = None
    funkcja:                 Optional[str] = None
    czas_od:                 Optional[str] = None
    czas_do:                 Optional[str] = None
    czas_udzialu:            Optional[str] = None
    dodatek_szkodliwy:       Optional[str] = None
    stopien_szkodliwosci:    Optional[str] = None
    opis_st_szkodliwosci:    Optional[str] = None
    hazardous_degree_id:     Optional[int] = None


# ── Helper ───────────────────────────────────────────────────────────────────

def _encode_filename(filename: str) -> str:
    return f"attachment; filename*=UTF-8''{quote(filename)}"

def _build_filename(prefix: str, firefighter: str, date_from: str, date_to: str,
                    only_unassigned: bool, only_eligible: bool, ext: str) -> str:
    """Buduje nazwę pliku uwzględniając aktywne filtry"""
    parts = [prefix]
    if firefighter:
        parts.append(firefighter.replace(" ", "_"))
    if date_from and date_to:
        parts.append(f"{date_from}_do_{date_to}")
    elif date_from:
        parts.append(f"od_{date_from}")
    elif date_to:
        parts.append(f"do_{date_to}")
    if only_unassigned:
        parts.append("bez_stopnia")
    if only_eligible:
        parts.append("zaliczone")
    parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))
    return "_".join(parts) + ext


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
    file_path = None
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".xlsx", ".xls"]:
            raise HTTPException(status_code=400, detail="Dozwolone: .xlsx, .xls")

        unique_filename = f"hazardous_{uuid.uuid4()}{file_ext}"
        file_path = Path(settings.UPLOAD_DIR) / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        records_data = excel_processor.process_excel_file(file_path)

        if not records_data or not hasattr(records_data, "items") or len(records_data.items) == 0:
            raise HTTPException(status_code=400, detail="Nie znaleziono danych w pliku")

        file_record = HazardousRecordsService.create_file_record(
            db,
            filename=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            rows_count=len(records_data.items),
        )

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
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path and Path(file_path).exists():
            Path(file_path).unlink()


# ── REKORDY ──────────────────────────────────────────────────────────────────

@router.get("/files/{file_id}/records")
def get_records(
    file_id: int,
    firefighter: Optional[str] = None,
    only_unassigned: bool = False,
    only_eligible: bool = False,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
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
        only_eligible=only_eligible,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by, sort_order=sort_order,
    )
    total = HazardousRecordsService.count_records_by_file(
        db, file_id,
        firefighter=firefighter,
        only_unassigned=only_unassigned,
        only_eligible=only_eligible,
        date_from=date_from,
        date_to=date_to,
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
    names = HazardousRecordsService.get_unique_firefighters_in_file(db, file_id)
    return {"firefighters": names}


@router.post("/records/")
def create_record(data: RecordCreate, db: Session = Depends(get_db)):
    from models.swd_data import HazardousRecord
    record = HazardousRecord(**data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"success": True, "record": record.to_dict()}


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
def assign_degree(record_id: int, data: AssignDegreeRequest, db: Session = Depends(get_db)):
    record = HazardousRecordsService.assign_degree(db, record_id, data.hazardous_degree_id)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    return {"success": True, "record": record.to_dict()}


@router.post("/records/assign-degree-bulk")
def assign_degree_bulk(data: AssignDegreeBulkRequest, db: Session = Depends(get_db)):
    updated = HazardousRecordsService.assign_degree_bulk(
        db, data.record_ids, data.hazardous_degree_id
    )
    return {"success": True, "updated_count": updated}


# ── EKSPORT ───────────────────────────────────────────────────────────────────

@router.get("/files/{file_id}/export/excel")
def export_to_excel(
    file_id: int,
    firefighter:     Optional[str] = None,
    only_unassigned: bool = False,
    only_eligible:   bool = False,
    date_from:       Optional[str] = None,
    date_to:         Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        from services.hazardous_excel_service import HazardousExcelService
        records = HazardousRecordsService.get_records_by_file(
            db, file_id, skip=0, limit=100000,
            firefighter=firefighter,
            only_unassigned=only_unassigned,
            only_eligible=only_eligible,
            date_from=date_from,
            date_to=date_to,
        )
        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")

        filename = _build_filename(
            "dodatek_szkodliwy", firefighter, date_from, date_to,
            only_unassigned, only_eligible, ".xlsx"
        )
        file_content = HazardousExcelService().export_to_excel([r.to_dict() for r in records])

        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": _encode_filename(filename),
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/export/csv")
def export_to_csv(
    file_id: int,
    firefighter:     Optional[str] = None,
    only_unassigned: bool = False,
    only_eligible:   bool = False,
    date_from:       Optional[str] = None,
    date_to:         Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        from services.hazardous_excel_service import HazardousExcelService
        records = HazardousRecordsService.get_records_by_file(
            db, file_id, skip=0, limit=100000,
            firefighter=firefighter,
            only_unassigned=only_unassigned,
            only_eligible=only_eligible,
            date_from=date_from,
            date_to=date_to,
        )
        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")

        filename = _build_filename(
            "dodatek_szkodliwy", firefighter, date_from, date_to,
            only_unassigned, only_eligible, ".csv"
        )
        file_content = HazardousExcelService().export_to_csv([r.to_dict() for r in records])

        return StreamingResponse(
            file_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": _encode_filename(filename),
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/generate-document")
def generate_document(
    file_id: int,
    firefighter:     Optional[str] = None,
    only_unassigned: bool = False,
    only_eligible:   bool = False,
    date_from:       Optional[str] = None,
    date_to:         Optional[str] = None,
    polrocze:        Optional[str] = None,
    jednostka:       Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Generuje zestawienie czynności w warunkach szkodliwych w formacie HTML.
    Stosuje te same filtry co eksport Excel/CSV.
    """
    try:
        from services.hazardous_document_service import HazardousDocumentService

        if not firefighter:
            raise HTTPException(status_code=400, detail="Musisz wybrać strażaka")

        if not date_from or not date_to:
            raise HTTPException(
                status_code=400,
                detail="Musisz wybrać zakres dat (od - do) aby wygenerować dokument"
            )

        # Oblicz półrocze na podstawie daty
        if not polrocze:
            try:
                from datetime import date as date_type
                d = date_type.fromisoformat(date_from[:10])
                polrocze = f"{'I' if d.month <= 6 else 'II'} półrocze {d.year}"
            except Exception:
                polrocze = '.....................'

        records = HazardousRecordsService.get_records_by_file(
            db, file_id, skip=0, limit=100000,
            firefighter=firefighter,
            only_unassigned=only_unassigned,
            only_eligible=only_eligible,
            date_from=date_from,
            date_to=date_to,
        )
        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do wygenerowania dokumentu")

        records_data = [r.to_dict() for r in records]

        # Dane strażaka — pobierz z tabeli firefighters (stopien, stanowisko, jednostka)
        firefighter_data = None
        jednostka_val = jednostka  # opcjonalny override z query param
        try:
            from services.firefighter_service import FirefighterService
            ffs = FirefighterService.search_firefighters(db, firefighter, skip=0, limit=1)
            if ffs:
                ff = ffs[0]
                firefighter_data = {
                    'stopien':       ff.stopien       or '.....................',
                    'nazwisko_imie': ff.nazwisko_imie or firefighter,
                    'stanowisko':    ff.stanowisko    or '.....................',
                }
                # jednostka z tabeli firefighters jeśli nie podana w query
                if not jednostka_val:
                    jednostka_val = getattr(ff, 'jednostka', None) or ''
        except Exception as e:
            print(f"[WARN] Nie znaleziono strażaka w firefighters: {e}")

        # Fallback — dane z pierwszego rekordu SWD
        if not firefighter_data and records:
            r = records[0]
            firefighter_data = {
                'stopien':       r.stopien       or '.....................',
                'nazwisko_imie': r.nazwisko_imie or firefighter,
                'stanowisko':    '.....................',
            }

        # jednostka — fallback z rekordu SWD
        if not jednostka_val and records:
            jednostka_val = records[0].jednostka or '.....................'

        doc_service = HazardousDocumentService()
        html_content = doc_service.generate_html(
            firefighter_name=firefighter,
            records=records_data,
            firefighter_data=firefighter_data,
            polrocze=polrocze,
            jednostka=jednostka_val,
            filters={
                'only_eligible':   only_eligible,
                'only_unassigned': only_unassigned,
            },
        )

        return StreamingResponse(
            iter([html_content.encode('utf-8')]),
            media_type="text/html",
            headers={"Content-Type": "text/html; charset=utf-8"},
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))