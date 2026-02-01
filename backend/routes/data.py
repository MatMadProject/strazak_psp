from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path
import unicodedata
import re
from urllib.parse import quote

sys.path.append(str(Path(__file__).parent.parent))
from database import get_db
from services.data_service import DataService
from services.departures_excel_service import DeparturesExcelService
from services.document_generator_service import DocumentGeneratorService

router = APIRouter(prefix="/api/data", tags=["data"])

# Pydantic models dla request/response
class RecordUpdate(BaseModel):
    nazwisko_imie: Optional[str] = None
    stopien: Optional[str] = None
    p: Optional[str] = None
    mz: Optional[str] = None
    af: Optional[str] = None
    zaliczono_do_emerytury: Optional[str] = None
    nr_meldunku: Optional[str] = None
    czas_rozp_zdarzenia: Optional[str] = None
    funkcja: Optional[str] = None

def normalize_filename(text: str) -> str:
    """
    Normalizuje tekst do bezpiecznej nazwy pliku (usuwa polskie znaki, spacje, znaki specjalne)
    """
    # Zamień polskie znaki na ASCII
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ASCII', 'ignore').decode('ASCII')
    
    # Usuń wszystko co nie jest literą, cyfrą, myślnikiem lub podkreślnikiem
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Zamień spacje i wielokrotne myślniki/podkreślniki na pojedyncze podkreślniki
    text = re.sub(r'[-\s]+', '_', text)
    
    # Usuń podkreślniki z początku i końca
    text = text.strip('_')
    
    return text

def encode_filename_header(filename: str) -> str:
    """
    Koduje nazwę pliku dla nagłówka Content-Disposition zgodnie z RFC 5987
    Obsługuje polskie znaki i jest kompatybilne z nowoczesnymi przeglądarkami
    """
    # Zakoduj filename używając UTF-8 i URL encoding
    encoded_filename = quote(filename)
    
    # RFC 5987: filename*=UTF-8''encoded_filename
    return f"attachment; filename*=UTF-8''{encoded_filename}"

@router.get("/records")
def get_records(
    file_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Pobierz rekordy z opcjonalnym filtrowaniem
    - file_id: filtruj po pliku
    - search: wyszukaj w nazwach, kodach, kategoriach
    - skip, limit: paginacja
    """
    if search:
        records = DataService.search_records(db, search, skip, limit)
    elif file_id:
        records = DataService.get_records_by_file(db, file_id, skip, limit)
    else:
        records = DataService.get_all_records(db, skip, limit)
    
    return {
        "records": [record.to_dict() for record in records],
        "skip": skip,
        "limit": limit,
        "count": len(records)
    }

@router.get("/records/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):
    """Pobierz pojedynczy rekord"""
    record = DataService.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    
    return record.to_dict()

@router.put("/records/{record_id}")
def update_record(
    record_id: int,
    update_data: RecordUpdate,
    db: Session = Depends(get_db)
):
    """Aktualizuj rekord"""
    # Usuń None wartości
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Brak danych do aktualizacji")
    
    record = DataService.update_record(db, record_id, update_dict)
    if not record:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    
    return {
        "success": True,
        "message": "Rekord zaktualizowany",
        "record": record.to_dict()
    }

@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Usuń rekord"""
    success = DataService.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rekord nie znaleziony")
    
    return {"success": True, "message": "Rekord usunięty"}

@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Pobierz statystyki aplikacji"""
    stats = DataService.get_statistics(db)
    return stats

@router.get("/files/{file_id}/firefighters")
def get_firefighters_in_file(file_id: int, db: Session = Depends(get_db)):
    """Pobierz listę unikalnych strażaków z danego pliku"""
    firefighters = DataService.get_unique_firefighters_in_file(db, file_id)
    return {"firefighters": firefighters}

@router.get("/files/{file_id}/records")
def get_file_records(
    file_id: int,
    firefighter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = 'asc',
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Pobierz rekordy z danego pliku
    """
    # Pobierz rekordy
    if date_from or date_to or firefighter:
        records = DataService.get_records_by_file_with_date_filter(
            db, file_id, date_from, date_to, firefighter, skip, limit, sort_by, sort_order
        )
        # Policz całkowitą liczbę bez paginacji
        total_count = DataService.count_records_by_file_with_date_filter(
            db, file_id, date_from, date_to, firefighter
        )
    else:
        records = DataService.get_records_by_file(
            db, file_id, skip, limit, sort_by, sort_order
        )
        # Policz całkowitą liczbę bez paginacji
        total_count = DataService.count_records_by_file(db, file_id)
    
    return {
        "records": [record.to_dict() for record in records],
        "file_id": file_id,
        "skip": skip,
        "limit": limit,
        "count": len(records),
        "total_count": total_count 
    }

@router.post("/files/{file_id}/records")
def create_record(
    file_id: int,
    record_data: RecordUpdate,
    db: Session = Depends(get_db)
):
    """Utwórz nowy rekord w pliku"""
    # Sprawdź czy plik istnieje
    from services.data_service import DataService
    file_record = DataService.get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    
    # Przygotuj dane (usuń None wartości)
    create_dict = {k: v for k, v in record_data.dict().items() if v is not None}
    
    if not create_dict:
        raise HTTPException(status_code=400, detail="Brak danych do zapisania")
    
    # Sprawdź wymagane pola
    if not create_dict.get('nazwisko_imie'):
        raise HTTPException(status_code=400, detail="Pole 'Nazwisko i Imię' jest wymagane")
    
    if not create_dict.get('nr_meldunku'):
        raise HTTPException(status_code=400, detail="Pole 'Nr meldunku' jest wymagane")
    
    # Sprawdź duplikaty
    existing_record = DataService.check_duplicate_record(
        db, 
        file_id, 
        create_dict['nazwisko_imie'], 
        create_dict['nr_meldunku']
    )
    
    if existing_record:
        raise HTTPException(
            status_code=409,  # 409 Conflict
            detail=f"Rekord dla '{create_dict['nazwisko_imie']}' z meldunkiem '{create_dict['nr_meldunku']}' już istnieje w tym pliku"
        )
    
    # Dodaj file_id do danych
    create_dict['file_id'] = file_id
    
    # Utwórz rekord
    record = DataService.create_single_record(db, create_dict)
    
    return {
        "success": True,
        "message": "Rekord utworzony pomyślnie",
        "record": record.to_dict()
    }



# Inicjalizacja serwisu Excel (dodaj na górze z innymi inicjalizacjami)
departures_excel_service = DeparturesExcelService()

@router.get("/files/{file_id}/export/excel")
def export_departures_to_excel(
    file_id: int,
    firefighter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Eksportuj wyjazdy z danego pliku do Excel
    Obsługuje te same filtry co endpoint listowania
    """
    try:
        # Pobierz wszystkie rekordy z filtrami (bez limitów paginacji)
        if date_from or date_to or firefighter:
            records = DataService.get_records_by_file_with_date_filter(
                db, file_id, date_from, date_to, firefighter, skip=0, limit=100000
            )
        else:
            records = DataService.get_records_by_file(
                db, file_id, skip=0, limit=100000
            )
        
        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")
        
        # Konwertuj do słowników
        records_data = [record.to_dict() for record in records]
        
        # Generuj plik Excel
        file_content = departures_excel_service.export_to_excel(records_data)
        
        # Buduj nazwę pliku z filtrami (BEZ normalizacji - zachowaj polskie znaki!)
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_parts = ["wyjazdy"]
        
        if firefighter:
            # Zachowaj polskie znaki, tylko zamień spacje na podkreślniki
            firefighter_clean = firefighter.replace(" ", "_")
            filename_parts.append(firefighter_clean)
        
        if date_from and date_to:
            filename_parts.append(f"{date_from}_do_{date_to}")
        elif date_from:
            filename_parts.append(f"od_{date_from}")
        elif date_to:
            filename_parts.append(f"do_{date_to}")
        
        filename_parts.append(timestamp)
        filename = "_".join(filename_parts) + ".xlsx"
        
        return StreamingResponse(
            file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": encode_filename_header(filename),  # Użyj nowej funkcji!
                "Access-Control-Expose-Headers": "Content-Disposition",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ BŁĄD EKSPORTU EXCEL: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/export/csv")
def export_departures_to_csv(
    file_id: int,
    firefighter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Eksportuj wyjazdy z danego pliku do CSV
    Obsługuje te same filtry co endpoint listowania
    """
    try:
        # Pobierz wszystkie rekordy z filtrami (bez limitów paginacji)
        if date_from or date_to or firefighter:
            records = DataService.get_records_by_file_with_date_filter(
                db, file_id, date_from, date_to, firefighter, skip=0, limit=100000
            )
        else:
            records = DataService.get_records_by_file(
                db, file_id, skip=0, limit=100000
            )
        
        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do eksportu")
        
        # Konwertuj do słowników
        records_data = [record.to_dict() for record in records]
        
        # Generuj plik CSV
        file_content = departures_excel_service.export_to_csv(records_data)
        
        # Buduj nazwę pliku z filtrami (BEZ normalizacji - zachowaj polskie znaki!)
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_parts = ["wyjazdy"]
        
        if firefighter:
            # Zachowaj polskie znaki, tylko zamień spacje na podkreślniki
            firefighter_clean = firefighter.replace(" ", "_")
            filename_parts.append(firefighter_clean)
        
        if date_from and date_to:
            filename_parts.append(f"{date_from}_do_{date_to}")
        elif date_from:
            filename_parts.append(f"od_{date_from}")
        elif date_to:
            filename_parts.append(f"do_{date_to}")
        
        filename_parts.append(timestamp)
        filename = "_".join(filename_parts) + ".csv"
        
        return StreamingResponse(
            file_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": encode_filename_header(filename),  # Użyj nowej funkcji!
                "Access-Control-Expose-Headers": "Content-Disposition",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ BŁĄD EKSPORTU CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    


# Inicjalizacja serwisu generowania dokumentów
document_service = DocumentGeneratorService()

@router.get("/files/{file_id}/generate-document/{format}")
def generate_document(
    file_id: int,
    format: str,  # html, pdf, docx
    firefighter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Generuje dokument karty wyjazdów w wybranym formacie
    Formaty: html, pdf, docx
    """
    try:
        # Walidacja formatu
        if format not in ['html', 'pdf', 'docx']:
            raise HTTPException(status_code=400, detail="Nieprawidłowy format. Dostępne: html, pdf, docx")
        
        # Sprawdź czy wybrano strażaka
        if not firefighter:
            raise HTTPException(status_code=400, detail="Musisz wybrać strażaka aby wygenerować dokument")
        
        # WALIDACJA DAT - muszą być wybrane obie daty
        if not date_from or not date_to:
            raise HTTPException(
                status_code=400, 
                detail="Musisz wybrać zakres dat (od - do) aby wygenerować dokument"
            )
        
        # Pobierz wszystkie rekordy z filtrami
        if date_from or date_to or firefighter:
            records = DataService.get_records_by_file_with_date_filter(
                db, file_id, date_from, date_to, firefighter, skip=0, limit=100000
            )
        else:
            records = DataService.get_records_by_file(
                db, file_id, skip=0, limit=100000
            )
        
        if not records:
            raise HTTPException(status_code=404, detail="Brak danych do wygenerowania dokumentu")
        
        # Konwertuj do słowników
        records_data = [record.to_dict() for record in records]
        
        # Pobierz dane strażaka z bazy Firefighters (jeśli istnieje)
        from services.firefighter_service import FirefighterService
        
        firefighter_data = None
        try:
            # Spróbuj znaleźć strażaka w bazie
            firefighters = FirefighterService.search_firefighters(db, firefighter, skip=0, limit=1)
            if firefighters and len(firefighters) > 0:
                ff = firefighters[0]
                firefighter_data = {
                    'stopien': ff.stopien,
                    'nazwisko_imie': ff.nazwisko_imie,
                    'stanowisko': ff.stanowisko
                }
        except Exception as e:
            print(f"⚠️ Nie znaleziono strażaka w bazie Firefighters: {e}")
            # Jeśli nie znaleziono, użyj domyślnych wartości
            firefighter_data = None
        
        # Przygotuj nazwę pliku
        from datetime import datetime
        from urllib.parse import quote
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        firefighter_clean = firefighter.replace(" ", "_")
        filename_base = f"karta_wyjazdow_{firefighter_clean}_{timestamp}"
        
        # Generuj dokument w wybranym formacie
        if format == 'html':
            content = document_service.generate_html(
                firefighter, records_data, date_from, date_to, firefighter_data
            )
            filename = f"{filename_base}.html"
            
            return StreamingResponse(
                iter([content.encode('utf-8')]),
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                }
            )
        
        elif format == 'pdf':
            file_content = document_service.generate_pdf(
                firefighter, records_data, date_from, date_to, firefighter_data
            )
            filename = f"{filename_base}.pdf"
            
            return StreamingResponse(
                file_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                }
            )
        
        elif format == 'docx':
            file_content = document_service.generate_docx(
                firefighter, records_data, date_from, date_to, firefighter_data
            )
            filename = f"{filename_base}.docx"
            
            return StreamingResponse(
                file_content,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ BŁĄD GENEROWANIA DOKUMENTU: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))