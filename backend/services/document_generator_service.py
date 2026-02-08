from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from jinja2 import Template, Environment, FileSystemLoader
from io import BytesIO
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

# Dodaj importy dla ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class DocumentGeneratorService:
    """
    Serwis do generowania dokumentów kart wyjazdów w różnych formatach
    """
    
    def __init__(self):
        """Inicjalizacja - rejestruj czcionki dla polskich znaków"""
        try:
            # Spróbuj zarejestrować czcionkę Arial (Windows)
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
            self.font_name = 'Arial'
        except:
            # Fallback - użyj Helvetica (wbudowana)
            self.font_name = 'Helvetica'
        # Konfiguracja Jinja2 - ścieżka do szablonów
        template_dir = Path(__file__).parent.parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate_docx(self, firefighter_name: str, records: List[Dict[str, Any]], 
                    date_from: str = None, date_to: str = None,
                    firefighter_data: Dict[str, str] = None) -> BytesIO:
        """
        Generuje kartę wyjazdów w formacie DOCX
        ORIENTACJA POZIOMA (LANDSCAPE)
        """
        doc = Document()
        
        # Ustaw orientację poziomą i marginesy
        section = doc.sections[0]
        section.page_height = Cm(21)
        section.page_width = Cm(29.7)
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)
        
        # 1. GÓRNA SEKCJA: Pieczątka | Strona nr 1
        header_table = doc.add_table(rows=2, cols=2)
        header_table.autofit = False
        header_table.columns[0].width = Cm(15)
        header_table.columns[1].width = Cm(10)
        
        # Lewa kolumna - pieczątka
        header_table.cell(0, 0).text = "........................................"
        header_table.cell(1, 0).text = "(pieczątka jednostki organizacyjnej)"
        header_table.cell(1, 0).paragraphs[0].runs[0].font.size = Pt(8)
        header_table.cell(1, 0).paragraphs[0].runs[0].font.italic = True
        header_table.cell(1, 0).paragraphs[0].runs[0].font.color.rgb = RGBColor(128, 128, 128)
        
        # Prawa kolumna - numer strony
        cell_page = header_table.cell(0, 1)
        cell_page.text = "Strona nr 1"
        cell_page.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        doc.add_paragraph()
        
        # 2. NAGŁÓWEK DOKUMENTU
        title1 = doc.add_paragraph()
        title1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run1 = title1.add_run("Roczna karta ewidencji bezpośredniego udziału strażaka w działaniach ratowniczych,")
        run1.font.size = Pt(12)
        run1.font.bold = True
        
        title2 = doc.add_paragraph()
        title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run2 = title2.add_run("w tym ratowniczo-gaśniczych lub bezpośredniego kierowania tymi działaniami na miejscu zdarzenia")
        run2.font.size = Pt(12)
        run2.font.bold = True
        
        doc.add_paragraph()
        
        # 3. ZAKRES DAT
        date_range = doc.add_paragraph()
        date_range.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date_text = f"od {date_from if date_from else '.....................'} do {date_to if date_to else '.....................'}"
        date_run = date_range.add_run(date_text)
        date_run.font.size = Pt(10)
        
        doc.add_paragraph()
        
        # 4. DANE STRAŻAKA
        stopien = firefighter_data.get('stopien', '.....................') if firefighter_data else '.....................'
        nazwisko_imie = firefighter_data.get('nazwisko_imie', firefighter_name) if firefighter_data else firefighter_name
        stanowisko = firefighter_data.get('stanowisko', '.....................') if firefighter_data else '.....................'
        
        firefighter_info = doc.add_paragraph()
        firefighter_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ff_run = firefighter_info.add_run(f"{stopien}, {nazwisko_imie}, {stanowisko}")
        ff_run.font.size = Pt(11)
        
        firefighter_label = doc.add_paragraph()
        firefighter_label.alignment = WD_ALIGN_PARAGRAPH.CENTER
        label_run = firefighter_label.add_run("(stopień, tytuł, imię, nazwisko, stanowisko)")
        label_run.font.size = Pt(8)
        label_run.font.italic = True
        label_run.font.color.rgb = RGBColor(128, 128, 128)
        
        doc.add_paragraph()
        
        # 5. TABELA GŁÓWNA
        table = doc.add_table(rows=1, cols=7)
        table.style = 'Table Grid'
        
        # Nagłówki
        headers = ['Lp.', 'Data', 'Nr meldunku', 'Funkcja', 'Rodzaj zdarzenia', 'Zaliczono do 0,5%', 'Uwagi']
        header_cells = table.rows[0].cells
        
        for i, header in enumerate(headers):
            cell = header_cells[i]
            cell.text = header
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.size = Pt(9)
            self._set_cell_background(cell, "D3D3D3")
        
        # Dane
        for idx, record in enumerate(records, start=1):
            row_cells = table.add_row().cells
            
            # Wyciągnij datę
            czas_rozp = record.get('czas_rozp_zdarzenia', '')
            data = czas_rozp[:10] if len(czas_rozp) >= 10 else czas_rozp
            
            # Rodzaj zdarzenia
            rodzaj = ''
            if str(record.get('p', '')).strip() == '1':
                rodzaj = 'P'
            elif str(record.get('mz', '')).strip() == '1':
                rodzaj = 'MZ'
            elif str(record.get('af', '')).strip() == '1':
                rodzaj = 'AF'
            
            # Zaliczono
            zaliczono = record.get('zaliczono_do_emerytury', '')
            zaliczono_text = 'Tak' if str(zaliczono) == '1' else 'Nie' if str(zaliczono) == '0' else ''
            
            data_row = [
                str(idx),
                data,
                record.get('nr_meldunku', ''),
                record.get('funkcja', ''),
                rodzaj,
                zaliczono_text,
                ''
            ]
            
            for i, value in enumerate(data_row):
                row_cells[i].text = value
                for paragraph in row_cells[i].paragraphs:
                    if i in [0, 1]:  # Lp i Data - wyśrodkowane
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        run.font.size = Pt(8)
        
        doc.add_paragraph()
        
        # Podsumowanie
        summary = doc.add_paragraph()
        summary_run = summary.add_run(f"Łącznie wyjazdów: {len(records)}")
        summary_run.font.size = Pt(10)
        summary_run.font.bold = True
        
        doc.add_paragraph()
        
        # Stopka
        footer = doc.add_paragraph()
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer.add_run("app.straznica.com.pl 2026 wszelkie prawa zastrzeżone")
        footer_run.font.size = Pt(7)
        footer_run.font.italic = True
        footer_run.font.color.rgb = RGBColor(128, 128, 128)
        
        # Zapisz
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        
        return output
    
    def _set_cell_background(self, cell, color):
        """Ustaw kolor tła komórki"""
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), color)
        cell._element.get_or_add_tcPr().append(shading_elm)
    
    def generate_html(self, firefighter_name: str, records: List[Dict[str, Any]],
                    date_from: str = None, date_to: str = None,
                    firefighter_data: Dict[str, str] = None) -> str:
        """
        Generuje kartę wyjazdów w formacie HTML używając szablonu z pliku
        ORIENTACJA POZIOMA (LANDSCAPE)
        Z PAGINACJĄ: strona 1 = 16 wierszy, kolejne strony = 20 wierszy
        """
        # Załaduj szablon z pliku
        template = self.jinja_env.get_template('karta_wyjazdow.html')
        
        # Przygotuj dane strażaka
        stopien = firefighter_data.get('stopien', '.....................') if firefighter_data else '.....................'
        nazwisko_imie = firefighter_data.get('nazwisko_imie', firefighter_name) if firefighter_data else firefighter_name
        stanowisko = firefighter_data.get('stanowisko', '.....................') if firefighter_data else '.....................'
        idx = 1
        # Przygotuj dane dla szablonu
        all_records = []
        for id, record in enumerate(records, start=1):
            # Pomiń rekord jeżele nie zaliczony do emerytury
            if record.get('zaliczono_do_emerytury', '') != '1':
                continue
            # Wyciągnij datę (pierwsze 10 znaków)
            czas_rozp = record.get('czas_rozp_zdarzenia', '')
            data = czas_rozp[:10] if len(czas_rozp) >= 10 else czas_rozp
            
            # Określ rodzaj zagrożenia
            rodzaj_zagrozenia = ''
            p_value = str(record.get('p', '')).strip()
            mz_value = str(record.get('mz', '')).strip()
            
            if p_value == '1':
                rodzaj_zagrozenia = 'pożar'
            elif mz_value == '1':
                rodzaj_zagrozenia = 'm.zagrożenie'
            
            # Określ zadanie podstawowe (X jeśli ratownik)
            funkcja = record.get('funkcja', '').lower()
            zadanie_podstawowe = 'X' if 'ratownik' in funkcja else ''
            
            # Zadanie specjalistyczne - na razie puste (do implementacji po zmianie modelu)
            zadanie_specjalistyczne = ''
            
            # Kierowanie działaniami (X jeśli dowódca)
            kierowanie = 'X' if 'dowódca' in funkcja or 'dowodca' in funkcja else ''
            
            all_records.append({
                'lp': idx,  # Globalne Lp przez wszystkie strony
                'data': data,
                'rodzaj_zagrozenia': rodzaj_zagrozenia,
                'zadanie_podstawowe': zadanie_podstawowe,
                'zadanie_specjalistyczne': zadanie_specjalistyczne,
                'kierowanie': kierowanie,
                'nr_meldunku': record.get('nr_meldunku', ''),
            })
            # Zwieksz licznik
            idx += 1
        
        # PAGINACJA: Strona 1 = 16 wierszy, kolejne = 20 wierszy
        pages = []
        page_number = 1
        records_remaining = all_records[:]
        
        while records_remaining:
            if page_number == 1:
                # Pierwsza strona - 16 wierszy
                page_records = records_remaining[:16]
                records_remaining = records_remaining[16:]
            else:
                # Kolejne strony - 20 wierszy
                page_records = records_remaining[:20]
                records_remaining = records_remaining[20:]
            
            pages.append({
                'page_number': page_number,
                'records': page_records,
                'is_last_page': len(records_remaining) == 0
            })
            
            page_number += 1
        
        # Renderuj szablon
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
    
    def generate_pdf(self, firefighter_name: str, records: List[Dict[str, Any]], 
                 date_from: str = None, date_to: str = None, 
                 firefighter_data: Dict[str, str] = None) -> BytesIO:
        """
        Generuje kartę wyjazdów w formacie PDF używając ReportLab
        ORIENTACJA POZIOMA (LANDSCAPE)
        """
        from reportlab.lib.pagesizes import landscape, A4
        
        output = BytesIO()
        
        # Utwórz dokument PDF w orientacji poziomej
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),  # ORIENTACJA POZIOMA
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )
        
        # Elementy dokumentu
        elements = []
        
        # Style
        styles = getSampleStyleSheet()
        
        # 1. GÓRNA SEKCJA: Pieczątka jednostki (lewa) | Strona nr 1 (prawa)
        header_data = [
            [
                Paragraph("........................................", styles['Normal']),
                Paragraph("Strona nr 1", ParagraphStyle(
                    'PageNum',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_CENTER
                ))
            ],
            [
                Paragraph("<i>(pieczątka jednostki organizacyjnej)</i>", ParagraphStyle(
                    'Stamp',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.grey
                )),
                ""
            ]
        ]
        
        header_table = Table(header_data, colWidths=[12*cm, 8*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # 2. NAGŁÓWEK DOKUMENTU (2 linie)
        title_style1 = ParagraphStyle(
            'Title1',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            fontName=f'{self.font_name}-Bold' if self.font_name == 'Arial' else 'Helvetica-Bold',
            spaceAfter=2
        )
        
        title_style2 = ParagraphStyle(
            'Title2',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            fontName=f'{self.font_name}-Bold' if self.font_name == 'Arial' else 'Helvetica-Bold',
            spaceAfter=15
        )
        
        title1 = Paragraph(
            "Roczna karta ewidencji bezpośredniego udziału strażaka w działaniach ratowniczych,",
            title_style1
        )
        title2 = Paragraph(
            "w tym ratowniczo-gaśniczych lub bezpośredniego kierowania tymi działaniami na miejscu zdarzenia",
            title_style2
        )
        
        elements.append(title1)
        elements.append(title2)
        
        # 3. ZAKRES DAT
        date_style = ParagraphStyle(
            'DateRange',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        date_range_text = f"od {date_from if date_from else '.....................'} do {date_to if date_to else '.....................'}"
        date_range = Paragraph(date_range_text, date_style)
        elements.append(date_range)
        
        # 4. DANE STRAŻAKA
        stopien = firefighter_data.get('stopien', '.....................') if firefighter_data else '.....................'
        nazwisko_imie = firefighter_data.get('nazwisko_imie', firefighter_name) if firefighter_data else firefighter_name
        stanowisko = firefighter_data.get('stanowisko', '.....................') if firefighter_data else '.....................'
        
        firefighter_style = ParagraphStyle(
            'Firefighter',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=2
        )
        
        firefighter_info_style = ParagraphStyle(
            'FirefighterInfo',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        firefighter_text = f"{stopien}, {nazwisko_imie}, {stanowisko}"
        firefighter_para = Paragraph(firefighter_text, firefighter_style)
        firefighter_label = Paragraph("<i>(stopień, tytuł, imię, nazwisko, stanowisko)</i>", firefighter_info_style)
        
        elements.append(firefighter_para)
        elements.append(firefighter_label)
        
        # 5. TABELA GŁÓWNA
        # Nagłówki: Lp., Data, Nr meldunku, Funkcja, Rodzaj, Zaliczono, Uwagi
        table_data = [['Lp.', 'Data', 'Nr meldunku', 'Funkcja', 'Rodzaj zdarzenia', 'Zaliczono do 0,5%', 'Uwagi']]
        
        for idx, record in enumerate(records, start=1):
            # Wyciągnij samą datę z czas_rozp_zdarzenia (pierwsze 10 znaków: YYYY-MM-DD)
            czas_rozp = record.get('czas_rozp_zdarzenia', '')
            data = czas_rozp[:10] if len(czas_rozp) >= 10 else czas_rozp
            
            # Określ rodzaj zdarzenia
            rodzaj = ''
            if str(record.get('p', '')).strip() == '1':
                rodzaj = 'P'
            elif str(record.get('mz', '')).strip() == '1':
                rodzaj = 'MZ'
            elif str(record.get('af', '')).strip() == '1':
                rodzaj = 'AF'
            
            # Zaliczono do emerytury
            zaliczono = record.get('zaliczono_do_emerytury', '')
            zaliczono_text = 'Tak' if str(zaliczono) == '1' else 'Nie' if str(zaliczono) == '0' else ''
            
            table_data.append([
                str(idx),
                data,
                record.get('nr_meldunku', ''),
                record.get('funkcja', ''),
                rodzaj,
                zaliczono_text,
                ''
            ])
        
        # Szerokości kolumn (dostosowane do orientacji poziomej - mamy więcej miejsca)
        table = Table(table_data, colWidths=[1.5*cm, 2.5*cm, 3.5*cm, 4*cm, 3*cm, 3*cm, 4*cm])
        
        # Styl tabeli
        table.setStyle(TableStyle([
            # Nagłówek
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), f'{self.font_name}-Bold' if self.font_name == 'Arial' else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Dane
            ('FONTNAME', (0, 1), (-1, -1), self.font_name if self.font_name == 'Arial' else 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Lp
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Data
            ('ALIGN', (4, 1), (5, -1), 'CENTER'),  # Rodzaj i Zaliczono
            
            # Ramki
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Podsumowanie
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            fontName=f'{self.font_name}-Bold' if self.font_name == 'Arial' else 'Helvetica-Bold'
        )
        
        summary = Paragraph(f"Łącznie wyjazdów: {len(records)}", summary_style)
        elements.append(summary)
        
        # Stopka
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_CENTER,
            fontName=self.font_name if self.font_name == 'Arial' else 'Helvetica'
        )
        
        footer = Paragraph("app.straznica.com.pl 2026 wszelkie prawa zastrzeżone", footer_style)
        elements.append(footer)
        
        # Zbuduj PDF
        doc.build(elements)
        output.seek(0)
        
        return output