from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import sys

sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from config import settings
from services.excel_processor import ExcelProcessor
from services.data_service import DataService

router = APIRouter(prefix="/api/files", tags=["files"])
processor = ExcelProcessor()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload i przetwarzanie pliku Excel
    """
    try:
        # Walidacja rozszerzenia
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Nieprawidłowe rozszerzenie pliku. Dozwolone: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Generuj unikalną nazwę pliku
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = settings.UPLOAD_DIR / unique_filename
        
        # Zapisz plik
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Przetwórz plik
        records_data = processor.process_excel_file(file_path)
        
        # Utwórz rekord pliku w bazie
        file_record = DataService.create_file_record(
            db=db,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            rows_count=records_data.count
        )
        
        # Zapisz rekordy do bazy
        created_count = DataService.create_records(
            db=db,
            file_id=file_record.id,
            records_data=records_data
        )
        
        return {
            "success": True,
            "message": f"Plik przetworzony pomyślnie",
            "file_id": file_record.id,
            "filename": file.filename,
            "records_imported": created_count
        }
        
    except Exception as e:
        # W przypadku błędu, usuń plik
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_all_files(db: Session = Depends(get_db)):
    """Pobierz listę wszystkich zaimportowanych plików"""
    files = DataService.get_all_files(db)
    return {
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "imported_at": f.imported_at.isoformat() if f.imported_at else None,
                "rows_count": f.rows_count,
                "status": f.status
            }
            for f in files
        ]
    }

@router.get("/{file_id}")
def get_file_details(file_id: int, db: Session = Depends(get_db)):
    """Pobierz szczegóły pliku"""
    file_record = DataService.get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    
    return {
        "id": file_record.id,
        "filename": file_record.original_filename,
        "imported_at": file_record.imported_at.isoformat() if file_record.imported_at else None,
        "rows_count": file_record.rows_count,
        "status": file_record.status,
        "notes": file_record.notes
    }

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Usuń plik i wszystkie powiązane dane"""
    success = DataService.delete_file(db, file_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    
    return {"success": True, "message": "Plik usunięty pomyślnie"}

@router.get("/{file_id}/preview")
def get_file_preview(file_id: int, db: Session = Depends(get_db)):
    """Podgląd pierwszych rekordów z pliku"""
    file_record = DataService.get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    
    records = DataService.get_records_by_file(db, file_id, skip=0, limit=10)
    
    return {
        "file_id": file_id,
        "filename": file_record.original_filename,
        "preview": [record.to_dict() for record in records]
    }