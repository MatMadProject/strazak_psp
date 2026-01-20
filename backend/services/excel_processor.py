import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import sys

# Import biblioteki zestawienie-udzialu-swd
# Dostosuj import w zależności od struktury biblioteki
try:
    # Przykładowy import - dostosuj do rzeczywistej biblioteki
    # from zestawienie_udzialu_swd import process_file, parse_data
    pass
except ImportError:
    print("UWAGA: Biblioteka zestawienie-udzialu-swd nie jest zainstalowana")
    print("Zainstaluj: pip install git+https://github.com/MatMadProject/zestawienie-udzialu-swd.git")

class ExcelProcessor:
    """
    Klasa do przetwarzania plików Excel z wykorzystaniem
    biblioteki zestawienie-udzialu-swd
    """
    
    def __init__(self):
        pass
    
    def validate_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Walidacja pliku Excel
        Returns: (is_valid, error_message)
        """
        try:
            if not file_path.exists():
                return False, "Plik nie istnieje"
            
            if file_path.suffix.lower() not in ['.xlsx', '.xls']:
                return False, "Nieprawidłowe rozszerzenie pliku"
            
            # Sprawdź czy plik można otworzyć
            df = pd.read_excel(file_path, nrows=1)
            
            return True, ""
        except Exception as e:
            return False, f"Błąd walidacji: {str(e)}"
    
    def process_excel_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Przetwarza plik Excel używając biblioteki zestawienie-udzialu-swd
        
        Returns: Lista słowników z danymi do zapisu w bazie
        """
        try:
            # KROK 1: Walidacja
            is_valid, error = self.validate_file(file_path)
            if not is_valid:
                raise ValueError(error)
            
            # KROK 2: Przetwarzanie z użyciem biblioteki zestawienie-udzialu-swd
            # TODO: Dostosuj do rzeczywistego API biblioteki
            # Przykładowe użycie (do modyfikacji):
            """
            from zestawienie_udzialu_swd import process_file
            result = process_file(str(file_path))
            processed_data = result.get_data()
            """
            
            # TYMCZASOWE ROZWIĄZANIE: Odczyt bezpośredni z pandas
            # Zamień to na użycie biblioteki zestawienie-udzialu-swd
            df = pd.read_excel(file_path)
            
            records = []
            for _, row in df.iterrows():
                record = self._parse_row_to_record(row)
                if record:
                    records.append(record)
            
            return records
            
        except Exception as e:
            raise Exception(f"Błąd przetwarzania pliku: {str(e)}")
    
    def _parse_row_to_record(self, row: pd.Series) -> Dict[str, Any]:
        """
        Parsuje wiersz pandas Series do słownika dla modelu SWDRecord
        
        DOSTOSUJ TO DO STRUKTURY DANYCH Z BIBLIOTEKI zestawienie-udzialu-swd
        """
        try:
            # Przykładowe mapowanie kolumn - DOSTOSUJ!
            record = {
                "nazwa_swd": str(row.get('Nazwa', '')),
                "kod_swd": str(row.get('Kod', '')),
                "kategoria": str(row.get('Kategoria', '')),
                "wartosc": float(row.get('Wartość', 0)) if pd.notna(row.get('Wartość')) else None,
                "jednostka": str(row.get('Jednostka', '')),
                "data_pomiaru": str(row.get('Data', '')),
                "uwagi": str(row.get('Uwagi', ''))
            }
            return record
        except Exception as e:
            print(f"Błąd parsowania wiersza: {e}")
            return None
    
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