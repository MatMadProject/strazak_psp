from pathlib import Path
from typing import List, Dict, Any
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from docxtpl import DocxTemplate
from xhtml2pdf import pisa  # ← ZMIENIONE
import sys

class DocumentGeneratorService:
    """
    Serwis do generowania dokumentów kart wyjazdów w różnych formatach
    """
    
    def __init__(self):
        """Inicjalizacja - ścieżka do templates"""
        self.templates_dir = self._get_templates_path()
        
        # Jinja2 dla HTML
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir))
        )
    
    def _get_templates_path(self) -> Path:
        """Pobierz ścieżkę do templates (działa z PyInstaller)"""
        try:
            # PyInstaller
            base_path = sys._MEIPASS
            return Path(base_path) / "backend" / "templates"
        except AttributeError:
            # Development
            base_path = Path(__file__).parent.parent
            return Path(base_path) / "templates"
    
    def _prepare_records_data(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Przygotuj dane rekordów (logika wspólna dla wszystkich formatów)
        """
        idx = 1
        all_records = []
        
        for record in records:
            # Pomiń jeśli nie zaliczony do emerytury
            if record.get('zaliczono_do_emerytury', '') != '1':
                continue
            
            # Data
            czas_rozp = record.get('czas_rozp_zdarzenia', '')
            data = czas_rozp[:10] if len(czas_rozp) >= 10 else czas_rozp
            
            # Rodzaj zagrożenia
            rodzaj_zagrozenia = ''
            p_value = str(record.get('p', '')).strip()
            mz_value = str(record.get('mz', '')).strip()
            
            if p_value == '1':
                rodzaj_zagrozenia = 'pożar'
            elif mz_value == '1':
                rodzaj_zagrozenia = 'm.zagrożenie'
            
            # Zadanie podstawowe
            funkcja = record.get('funkcja', '').lower()
            zadanie_podstawowe = 'X' if 'ratownik' in funkcja else ''
            
            # Zadanie specjalistyczne
            zadanie_specjalistyczne = ''
            
            # Kierowanie
            kierowanie = 'X' if 'dowódca' in funkcja or 'dowodca' in funkcja else ''
            
            all_records.append({
                'lp': idx,
                'data': data,
                'rodzaj_zagrozenia': rodzaj_zagrozenia,
                'zadanie_podstawowe': zadanie_podstawowe,
                'zadanie_specjalistyczne': zadanie_specjalistyczne,
                'kierowanie': kierowanie,
                'nr_meldunku': record.get('nr_meldunku', ''),
            })
            idx += 1
        
        return all_records
    
    def _paginate_records(self, all_records: List[Dict]) -> List[Dict]:
        """
        Paginacja: strona 1 = 16 wierszy, kolejne = 20 wierszy
        """
        pages = []
        page_number = 1
        records_remaining = all_records[:]
        
        while records_remaining:
            if page_number == 1:
                page_records = records_remaining[:16]
                records_remaining = records_remaining[16:]
            else:
                page_records = records_remaining[:20]
                records_remaining = records_remaining[20:]
            
            pages.append({
                'page_number': page_number,
                'records': page_records,
                'is_last_page': len(records_remaining) == 0
            })
            page_number += 1
        
        return pages
    
    # ========================================
    # HTML - BEZ ZMIAN
    # ========================================
    def generate_html(self, firefighter_name: str, records: List[Dict[str, Any]],
                      date_from: str = None, date_to: str = None,
                      firefighter_data: Dict[str, str] = None) -> str:
        """
        Generuje kartę wyjazdów w formacie HTML używając szablonu z pliku
        """
        template = self.jinja_env.get_template('karta_wyjazdow.html')
        
        # Dane strażaka
        stopien = firefighter_data.get('stopien', '.....................') if firefighter_data else '.....................'
        nazwisko_imie = firefighter_data.get('nazwisko_imie', firefighter_name) if firefighter_data else firefighter_name
        stanowisko = firefighter_data.get('stanowisko', '.....................') if firefighter_data else '.....................'
        
        # Przygotuj rekordy
        all_records = self._prepare_records_data(records)
        
        # Paginacja
        pages = self._paginate_records(all_records)
        
        # Renderuj
        html_content = template.render(
            firefighter_name=firefighter_name,
            stopien=stopien,
            nazwisko_imie=nazwisko_imie,
            stanowisko=stanowisko,
            date_from=date_from if date_from else '.....................',
            date_to=date_to if date_to else '.....................',
            pages=pages
        )
        
        return html_content
    
    # ========================================
    # PDF z HTML (xhtml2pdf) - ZMIENIONE
    # ========================================
    def generate_pdf(self, firefighter_name: str, records: List[Dict[str, Any]], 
                     date_from: str = None, date_to: str = None, 
                     firefighter_data: Dict[str, str] = None) -> BytesIO:
        """
        Generuje PDF z HTML używając xhtml2pdf
        ORIENTACJA POZIOMA (LANDSCAPE)
        """
        # Wygeneruj HTML
        html_content = self.generate_html(
            firefighter_name, records, date_from, date_to, firefighter_data
        )
        
        # Przygotuj output
        output = BytesIO()
        
        # Konwertuj HTML -> PDF
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=output,
            encoding='utf-8'
        )
        
        # Sprawdź błędy
        if pisa_status.err:
            raise Exception(f"Błąd generowania PDF: {pisa_status.err}")
        
        # Zwróć PDF
        output.seek(0)
        return output
    
    # ========================================
    # DOCX z szablonu Word
    # ========================================
    def generate_docx(self, firefighter_name: str, records: List[Dict[str, Any]], 
                      date_from: str = None, date_to: str = None,
                      firefighter_data: Dict[str, str] = None) -> BytesIO:
        """
        Generuje DOCX z szablonu Word używając docxtpl
        """
        # Załaduj szablon
        template_path = self.templates_dir / "karta_wyjazdow.docx"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Szablon DOCX nie znaleziony: {template_path}")
        
        doc = DocxTemplate(template_path)
        
        # Dane strażaka
        stopien = firefighter_data.get('stopien', '.....................') if firefighter_data else '.....................'
        nazwisko_imie = firefighter_data.get('nazwisko_imie', firefighter_name) if firefighter_data else firefighter_name
        stanowisko = firefighter_data.get('stanowisko', '.....................') if firefighter_data else '.....................'
        
        # Przygotuj rekordy
        all_records = self._prepare_records_data(records)
        
        # Paginacja
        pages = self._paginate_records(all_records)
        
        # Kontekst dla szablonu
        context = {
            'stopien': stopien,
            'nazwisko_imie': nazwisko_imie,
            'stanowisko': stanowisko,
            'date_from': date_from if date_from else '.....................',
            'date_to': date_to if date_to else '.....................',
            'pages': pages,
        }
        
        # Renderuj
        doc.render(context)
        
        # Zapisz do BytesIO
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        
        return output