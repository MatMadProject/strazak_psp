import pandas as pd
from pathlib import Path
from typing import Dict, Any
from config import settings
import sys

# Import biblioteki zestawienie-swd
try:
    from zestawienie_swd import import_zestawienie, CollectionZestawienieWiersz
    ZESTAWIENIE_SWD_AVAILABLE = True
    if settings.IS_DESKTOP: 
        print("[OK] Biblioteka zestawienie_swd załadowana pomyślnie")
    else:
        print("✅ Biblioteka zestawienie_swd załadowana pomyślnie")    
except ImportError as e:
    ZESTAWIENIE_SWD_AVAILABLE = False
    if settings.IS_DESKTOP: 
        print("[ERROR] UWAGA: Biblioteka zestawienie-swd nie jest zainstalowana")
        print("Zainstaluj: pip install git+https://github.com/MatMadProject/zestawienie-udzialu-swd.git")
        print(f"Błąd importu: {e}")
    else:
        print("❌ UWAGA: Biblioteka zestawienie-swd nie jest zainstalowana")
        print("Zainstaluj: pip install git+https://github.com/MatMadProject/zestawienie-udzialu-swd.git")
        print(f"Błąd importu: {e}")  
    

class ExcelProcessor:
    """
    Klasa do przetwarzania plików Excel z wykorzystaniem
    biblioteki zestawienie-swd
    """
    
    def __init__(self):
        if not ZESTAWIENIE_SWD_AVAILABLE:
            if settings.IS_DESKTOP: 
                print("[WARNING] ExcelProcessor działa w trybie awaryjnym (bez zestawienie_swd)")
            else:
                print("⚠️ ExcelProcessor działa w trybie awaryjnym (bez zestawienie_swd)")
    
    def validate_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Walidacja pliku Excel
        Returns: (is_valid, error_message)
        """
        try:
            if not file_path.exists():
                return False, "Plik nie istnieje"
            
            if file_path.suffix.lower() not in ['.xlsx', '.xls']:
                return False, "Nieprawidłowe rozszerzenie pliku (wymagany .xlsx)"
            
            # Sprawdź czy plik można otworzyć
            try:
                df = pd.read_excel(file_path, nrows=1)
                if df.empty:
                    return False, "Plik Excel jest pusty"
            except Exception as e:
                return False, f"Nie można odczytać pliku Excel: {str(e)}"
            
            return True, ""
        except Exception as e:
            return False, f"Błąd walidacji: {str(e)}"
    
    def process_excel_file(self, file_path: Path) -> CollectionZestawienieWiersz:
        """
        Przetwarza plik Excel używając biblioteki zestawienie-swd
        
        Returns: CollectionZestawienieWiersz z danymi do zapisu w bazie
        """
        import traceback
        
        try:
            print(f"[EXCEL PROCESSOR] Rozpoczynam przetwarzanie: {file_path}")
            
            # KROK 1: Walidacja
            print(f"[EXCEL PROCESSOR] Walidacja pliku...")
            is_valid, error = self.validate_file(file_path)
            if not is_valid:
                if settings.IS_DESKTOP: 
                    print(f"[ERROR] [EXCEL PROCESSOR] Walidacja nieudana: {error}")
                else:
                    print(f"❌ [EXCEL PROCESSOR] Walidacja nieudana: {error}")
                
                raise ValueError(error)
            
            if settings.IS_DESKTOP: 
                print(f"[OK] [EXCEL PROCESSOR] Walidacja OK")
            else:
                print(f"✅ [EXCEL PROCESSOR] Walidacja OK")
            
            
            # KROK 2: Sprawdź czy biblioteka jest dostępna
            if not ZESTAWIENIE_SWD_AVAILABLE:
                raise ImportError(
                    "Biblioteka zestawienie_swd nie jest zainstalowana. "
                    "Zainstaluj: pip install git+https://github.com/MatMadProject/zestawienie-udzialu-swd.git"
                )
            
            # KROK 3: Przetwarzanie z biblioteką zestawienie-swd
            print(f"[EXCEL PROCESSOR] Importowanie zestawienia...")
            result = import_zestawienie(str(file_path)).get_zestawienie_szkodliwosci()
            
            if settings.IS_DESKTOP: 
                print(f"[OK]] [EXCEL PROCESSOR] Przetworzono {len(result.items)} rekordów")
            else:
                print(f"✅ [EXCEL PROCESSOR] Przetworzono {len(result.items)} rekordów")
            
            
            # Debug: pokaż pierwsze 3 rekordy
            if result.items:
                for i, item in enumerate(result.items[:3]):
                    print(f"[EXCEL PROCESSOR] Rekord {i}: {item.nazwisko_imie} - {item.funkcja}")
            
            return result
            
        except Exception as e:
            if settings.IS_DESKTOP: 
                print(f"[ERROR] [EXCEL PROCESSOR] BŁĄD: {str(e)}")
                print(f"[ERROR] [EXCEL PROCESSOR] Typ błędu: {type(e).__name__}")
            else:
                print(f"❌ [EXCEL PROCESSOR] BŁĄD: {str(e)}")
                print(f"❌ [EXCEL PROCESSOR] Typ błędu: {type(e).__name__}")
            
            traceback.print_exc()
            raise Exception(f"Błąd przetwarzania pliku: {str(e)}")
    
    def get_file_summary(self, file_path: Path) -> Dict[str, Any]:
        """Zwraca podsumowanie pliku Excel"""
        try:
            df = pd.read_excel(file_path)
            return {
                "rows_count": len(df),
                "columns_count": len(df.columns),
                "columns": df.columns.tolist(),
                "preview": df.head(5).to_dict('records')
            }
        except Exception as e:
            return {"error": str(e)}