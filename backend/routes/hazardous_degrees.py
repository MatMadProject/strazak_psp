"""
Router dla stopni szkodliwości.
Endpointy:
  GET    /hazardous-degrees/              - lista z filtrami i paginacją
  GET    /hazardous-degrees/statistics    - statystyki
  GET    /hazardous-degrees/{id}          - pojedynczy rekord
  POST   /hazardous-degrees/              - utwórz
  PUT    /hazardous-degrees/{id}          - aktualizuj
  DELETE /hazardous-degrees/{id}          - usuń
  GET    /hazardous-degrees/template/download  - szablon xlsx
  POST   /hazardous-degrees/import        - import z xlsx
  GET    /hazardous-degrees/export/excel  - eksport do xlsx
  GET    /hazardous-degrees/export/csv    - eksport do csv
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import shutil
import uuid
import sys

sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from config import settings
from services.hazardous_degrees_service import HazardousDegreesService
from services.hazardous_degrees_excel_service import HazardousDegreesExcelService

router = APIRouter()
excel_service = HazardousDegreesExcelService()


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class HazardousDegreeCreate(BaseModel):
    stopien: int = Field(..., ge=1, description="Stopień (liczba arabska, min. 1)")
    punkt:   int = Field(..., ge=1, description="Punkt (liczba arabska, min. 1)")
    opis:    str = Field(..., min_length=1, description="Opis")
    uwagi:   Optional[str] = None


class HazardousDegreeUpdate(BaseModel):
    stopien: Optional[int] = Field(None, ge=1)
    punkt:   Optional[int] = Field(None, ge=1)
    opis:    Optional[str] = None
    uwagi:   Optional[str] = None


# ── Endpointy ────────────────────────────────────────────────────────────────

@router.get("/")
def get_hazardous_degrees(
    search:  Optional[str] = None,
    stopien: Optional[int] = None,
    skip:    int = Query(0,   ge=0),
    limit:   int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Pobierz listę stopni szkodliwości z opcjonalnym filtrowaniem.
    - search:  szukaj w opisie i uwagach
    - stopien: filtruj po stopniu (liczba arabska)
    - skip, limit: paginacja
    """
    if search:
        records = HazardousDegreesService.search(db, search, skip, limit)
        total   = HazardousDegreesService.get_total_count(db, search=search)
    elif stopien is not None:
        records = HazardousDegreesService.get_by_stopien(db, stopien, skip, limit)
        total   = HazardousDegreesService.get_total_count(db, stopien=stopien)
    else:
        records = HazardousDegreesService.get_all(db, skip, limit)
        total   = HazardousDegreesService.get_total_count(db)

    return {
        "records": [r.to_dict() for r in records],
        "total_count": total,
        "skip":  skip,
        "limit": limit,
        "count": len(records),
    }


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Pobierz statystyki stopni szkodliwości"""
    return HazardousDegreesService.get_statistics(db)


# WAŻNE: endpointy ze stałymi segmentami (/template/download, /import, /export/*)
# muszą być PRZED /{id} żeby FastAPI nie traktował ich jako parametru
@router.get("/template/download")
def download_template():
    """Pobierz pusty szablon Excel do importu"""
    try:
        file_content = excel_service.create_template_file()
        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=szablon_stopnie_szkodliwosci.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Importuj stopnie szkodliwości z pliku Excel (.xlsx)"""
    file_path = None
    try:
        print(f"[HAZARDOUS IMPORT] Otrzymano plik: {file.filename}")

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".xlsx"]:
            raise HTTPException(
                status_code=400,
                detail="Nieprawidłowe rozszerzenie pliku. Dozwolone: .xlsx"
            )

        # Zapisz plik tymczasowo
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = settings.UPLOAD_DIR / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"[HAZARDOUS IMPORT] Plik zapisany: {file_path}")

        # Przetwórz
        records_data = excel_service.process_excel_file(file_path)

        if not records_data:
            raise HTTPException(
                status_code=400,
                detail="Nie znaleziono prawidłowych danych w pliku"
            )

        # Zapisz do bazy
        created_count = 0
        skipped_count = 0
        errors = []

        for record_data in records_data:
            try:
                HazardousDegreesService.create(db, record_data)
                created_count += 1
            except Exception as e:
                skipped_count += 1
                errors.append(f"{record_data.get('stopien')}.{record_data.get('punkt')}: {str(e)}")

        return {
            "success": True,
            "message": f"Zaimportowano {created_count} rekordów",
            "created_count": created_count,
            "skipped_count": skipped_count,
            "errors": errors if errors else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[HAZARDOUS IMPORT] BŁĄD: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Zawsze usuń plik tymczasowy
        if file_path and Path(file_path).exists():
            Path(file_path).unlink()


@router.get("/export/excel")
def export_to_excel(
    search:  Optional[str] = None,
    stopien: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Eksportuj stopnie szkodliwości do pliku Excel (.xlsx)"""
    try:
        if search:
            records = HazardousDegreesService.search(db, search, skip=0, limit=10000)
        elif stopien is not None:
            records = HazardousDegreesService.get_by_stopien(db, stopien, skip=0, limit=10000)
        else:
            records = HazardousDegreesService.get_all(db, skip=0, limit=10000)

        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")

        records_data  = [r.to_dict() for r in records]
        file_content  = excel_service.export_to_excel(records_data)

        from datetime import datetime
        filename = f"stopnie_szkodliwosci_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[HAZARDOUS EXPORT EXCEL] BŁĄD: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
def export_to_csv(
    search:  Optional[str] = None,
    stopien: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Eksportuj stopnie szkodliwości do pliku CSV"""
    try:
        if search:
            records = HazardousDegreesService.search(db, search, skip=0, limit=10000)
        elif stopien is not None:
            records = HazardousDegreesService.get_by_stopien(db, stopien, skip=0, limit=10000)
        else:
            records = HazardousDegreesService.get_all(db, skip=0, limit=10000)

        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")

        records_data = [r.to_dict() for r in records]
        file_content = excel_service.export_to_csv(records_data)

        from datetime import datetime
        filename = f"stopnie_szkodliwosci_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return StreamingResponse(
            file_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[HAZARDOUS EXPORT CSV] BŁĄD: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{record_id}")
def get_hazardous_degree(record_id: int, db: Session = Depends(get_db)):
    """Pobierz pojedynczy rekord"""
    record = HazardousDegreesService.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    return record.to_dict()


@router.post("/")
def create_hazardous_degree(
    data: HazardousDegreeCreate,
    db: Session = Depends(get_db)
):
    """Utwórz nowy stopień szkodliwości"""
    try:
        record = HazardousDegreesService.create(db, data.dict())
        return {
            "success": True,
            "message": "Rekord został dodany",
            "record": record.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{record_id}")
def update_hazardous_degree(
    record_id: int,
    data: HazardousDegreeUpdate,
    db: Session = Depends(get_db)
):
    """Aktualizuj rekord"""
    update_dict = {k: v for k, v in data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="Brak danych do aktualizacji")

    record = HazardousDegreesService.update(db, record_id, update_dict)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")

    return {
        "success": True,
        "message": "Rekord zaktualizowany",
        "record": record.to_dict()
    }


@router.delete("/{record_id}")
def delete_hazardous_degree(record_id: int, db: Session = Depends(get_db)):
    """Usuń rekord"""
    success = HazardousDegreesService.delete(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")

    return {
        "success": True,
        "message": "Rekord został usunięty"
    }