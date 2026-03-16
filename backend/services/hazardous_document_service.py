"""
backend/services/hazardous_document_service.py

Serwis do generowania zestawienia czynności w warunkach szkodliwych.
Wzorowany na DocumentGeneratorService — identyczna struktura.
Szablon: backend/templates/zestawienie_dodatku_szkodliwego.html
"""
from pathlib import Path
from typing import List, Dict, Any
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
import sys
import math


class HazardousDocumentService:

    def __init__(self):
        self.templates_dir = self._get_templates_path()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir))
        )

    def _get_templates_path(self) -> Path:
        try:
            base_path = sys._MEIPASS
            return Path(base_path) / "backend" / "templates"
        except AttributeError:
            base_path = Path(__file__).parent.parent
            return Path(base_path) / "templates"

    # ── Przygotowanie rekordów ────────────────────────────────────────────────

    ROMAN = {
        1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
        6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
    }

    def _to_roman(self, value) -> str:
        """Konwertuje liczbę całkowitą na cyfrę rzymską (1–10). Inne wartości zwraca bez zmian."""
        try:
            return self.ROMAN.get(int(value), str(value))
        except (ValueError, TypeError):
            return str(value) if value else ''

    def _parse_czas(self, raw: str) -> str:
        """
        Wyciąga czas z pola dodatek_szkodliwy w formacie '01:48 (2)' → '01:48'
        lub '00:00 (0)' → '00:00'. Jeśli brak spacji — zwraca wartość bez zmian.
        """
        if not raw:
            return ''
        raw = str(raw).strip()
        return raw.split(' ')[0] if ' ' in raw else raw

    def _round_up_time(self, czas: str) -> str:
        """
        Zaokrągla czas w górę do pełnej godziny jeśli minut > 30.
        '01:48' → '2', '00:25' → '0', '00:30' → '0', '01:31' → '2'
        Zwraca pełne godziny jako liczbę (bez ':00').
        """
        if not czas or ':' not in czas:
            return ''
        try:
            parts = czas.split(':')
            h = int(parts[0])
            m = int(parts[1])
            if m > 30:
                h += 1
            return str(h)
        except (ValueError, IndexError):
            return ''

    def _prepare_records(
        self,
        records: List[Dict[str, Any]],
        only_eligible: bool = False,
        only_unassigned: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Mapuje rekordy HazardousRecord na wiersze dokumentu.
        Uwzględnia tylko rekordy z przypisanym stopniem szkodliwości.
        """
        result = []
        idx = 1

        for record in records:
            # Poprawka 1: tylko rekordy z przypisanym stopniem szkodliwości
            if not record.get('hazardous_degree_id'):
                continue

            # Filtr: tylko zaliczone do dodatku (af != '1' AND czas_udzialu > '00:30')
            if only_eligible:
                af = str(record.get('af') or '').strip()
                czas_udzialu = str(record.get('czas_udzialu') or '').strip()
                if af == '1':
                    continue
                if not czas_udzialu or czas_udzialu <= '00:30':
                    continue

            # Filtr: tylko bez przypisanego stopnia — przy pkt 1 ten filtr jest sprzeczny,
            # zostawiamy dla spójności z API ale w praktyce da pusty wynik
            if only_unassigned:
                continue

            # Data zdarzenia — pierwsze 10 znaków z czas_od
            czas_od = str(record.get('czas_od') or '')
            data = czas_od[:10] if len(czas_od) >= 10 else czas_od

            # Rodzaj zdarzenia
            p_value  = str(record.get('p')  or '').strip()
            mz_value = str(record.get('mz') or '').strip()
            if p_value == '1':
                rodzaj = 'P'
            elif mz_value == '1':
                rodzaj = 'MZ'
            else:
                rodzaj = ''

            # Poprawka 2: kolumna 5 — tylko opis (bez stopnia i punktu)
            degree = record.get('hazardous_degree')
            if degree and isinstance(degree, dict):
                opis_czynnosci = degree.get('opis', '')
            else:
                opis_czynnosci = str(record.get('opis_st_szkodliwosci') or '')

            # Poprawka 3: kolumna 6 — stopień jako cyfra rzymska
            if degree and isinstance(degree, dict):
                stopien_szkodliwosci = self._to_roman(degree.get('stopien', ''))
            else:
                stopien_szkodliwosci = self._to_roman(record.get('stopien_szkodliwosci', ''))

            # Czas służby — z dodatek_szkodliwy (część przed spacją)
            czas_raw = str(record.get('dodatek_szkodliwy') or '')
            czas_udzialu_doc = self._parse_czas(czas_raw)

            # Poprawka 4: czas zaokrąglony jako pełna liczba godzin (1, 2, 3...)
            czas_zaokraglony = self._round_up_time(czas_udzialu_doc)

            result.append({
                'lp':                    idx,
                'data':                  data,
                'nr_meldunku':           str(record.get('nr_meldunku') or ''),
                'rodzaj_zagrozenia':     rodzaj,
                'opis_czynnosci':        opis_czynnosci,
                'stopien_szkodliwosci':  stopien_szkodliwosci,
                'czas_udzialu':          czas_udzialu_doc,
                'czas_udzialu_zaokraglony': czas_zaokraglony,
            })
            idx += 1

        return result

    def _paginate(self, all_records: List[Dict]) -> List[Dict]:
        """Strona 1 = 12 wierszy, kolejne = 16 wierszy"""
        pages = []
        page_number = 1
        remaining = all_records[:]

        while remaining:
            limit = 12 if page_number == 1 else 16
            page_records = remaining[:limit]
            remaining    = remaining[limit:]
            pages.append({
                'page_number': page_number,
                'records':     page_records,
                'is_last_page': len(remaining) == 0,
            })
            page_number += 1

        return pages

    # ── Generowanie HTML ──────────────────────────────────────────────────────

    def generate_html(
        self,
        firefighter_name: str,
        records: List[Dict[str, Any]],
        firefighter_data: Dict[str, str] = None,
        polrocze: str = None,
        jednostka: str = None,
        filters: Dict[str, Any] = None,
    ) -> str:
        """
        Generuje zestawienie w formacie HTML używając szablonu
        zestawienie_dodatku_szkodliwego.html
        """
        filters = filters or {}

        template = self.jinja_env.get_template('zestawienie_dodatku_szkodliwego.html')

        fd = firefighter_data or {}
        stopien      = fd.get('stopien',      '.....................')
        nazwisko_imie = fd.get('nazwisko_imie', firefighter_name)
        stanowisko   = fd.get('stanowisko',   '.....................')
        jednostka    = jednostka or fd.get('jednostka', '.....................')
        polrocze     = polrocze  or '.....................'

        all_records = self._prepare_records(
            records,
            only_eligible=filters.get('only_eligible', False),
            only_unassigned=filters.get('only_unassigned', False),
        )

        # pages = self._paginate(all_records)

        return template.render(
            firefighter_name=firefighter_name,
            polrocze=polrocze,
            stopien=stopien,
            nazwisko_imie=nazwisko_imie,
            stanowisko=stanowisko,
            jednostka=jednostka,
            records=all_records,
        )

    # ── Generowanie DOCX ──────────────────────────────────────────────────────

    def generate_docx(
            self,
            firefighter_name: str,
            records: List[Dict[str, Any]],
            firefighter_data: Dict[str, str] = None,
            polrocze: str = None,
            jednostka: str = None,
            filters: Dict[str, Any] = None,
        ) -> BytesIO:
            """
            Generuje zestawienie w formacie DOCX używając szablonu
            zestawienie_dodatku_szkodliwego.docx (docxtpl).
            Bez paginacji — jedna tabela, Word sam łamie strony
            i powtarza nagłówek (Repeat Header Row w szablonie).
            """
            from docxtpl import DocxTemplate
    
            template_path = self.templates_dir / "zestawienie_dodatku_szkodliwego.docx"
            if not template_path.exists():
                raise FileNotFoundError(f"Szablon DOCX nie znaleziony: {template_path}")
    
            filters = filters or {}
    
            fd = firefighter_data or {}
            stopien       = fd.get('stopien',       '.....................')
            nazwisko_imie = fd.get('nazwisko_imie',  firefighter_name)
            stanowisko    = fd.get('stanowisko',    '.....................')
            jednostka     = jednostka or fd.get('jednostka', '.....................')
            polrocze      = polrocze  or '.....................'
    
            # Płaska lista rekordów — bez paginacji
            all_records = self._prepare_records(
                records,
                only_eligible=filters.get('only_eligible', False),
                only_unassigned=filters.get('only_unassigned', False),
            )
    
            context = {
                'firefighter_name': firefighter_name,
                'polrocze':         polrocze,
                'stopien':          stopien,
                'nazwisko_imie':    nazwisko_imie,
                'stanowisko':       stanowisko,
                'jednostka':        jednostka,
                'records':          all_records,   
            }
    
            doc = DocxTemplate(template_path)
            doc.render(context)
    
            output = BytesIO()
            doc.save(output)
            output.seek(0)
            return output
 