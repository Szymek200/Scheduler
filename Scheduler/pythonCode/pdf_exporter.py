# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import calendar
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

class SchedulePDFExporter:
    def __init__(self, month: int, year: int):
        self.month = month
        self.year = year
        self.days_in_month = calendar.monthrange(year, month)[1]
        self.month_name = [
            "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", 
            "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
        ][month]
        
        # Konfiguracja stylów bazowych
        self.styles = getSampleStyleSheet()
        
        # Własny styl dla nagłówków i tekstu (wspierający polskie znaki przez domyślny font Helvetica)
        self.title_style = ParagraphStyle(
            'PDFTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1A365D'),
            alignment=1 # Wyśrodkowanie
        )
        self.subtitle_style = ParagraphStyle(
            'PDFSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#4A5568'),
            alignment=1
        )
        self.cell_style = ParagraphStyle(
            'PDFCell',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=11,
            alignment=1
        )
        self.cell_bold_style = ParagraphStyle(
            'PDFCellBold',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            alignment=1
        )

    def export_individual_pdf(self, worker, output_path: str):
        """Generuje PDF z grafikiem dla pojedynczego pracownika"""
        # Dla pracownika stosujemy domyślny układ pionowy A4 (Portrait)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm, leftMargin=1.5*cm,
            topMargin=1.5*cm, bottomMargin=1.5*cm
        )
        
        story = []
        
        # Nagłówek dokumentu
        story.append(Paragraph(f"INDYWIDUALNY GRAFIK PRACY", self.title_style))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f"Pracownik: {worker.name} {worker.surname} | Okres: {self.month_name} {self.year}", self.subtitle_style))
        story.append(Spacer(1, 0.6*cm))
        
        # Przygotowanie tabeli dni i zmian
        # Nagłówki tabeli
        table_data = [[
            Paragraph("<b>Data</b>", self.cell_bold_style),
            Paragraph("<b>Dzień</b>", self.cell_bold_style),
            Paragraph("<b>Godziny pracy</b>", self.cell_bold_style),
            Paragraph("<b>Miejsce / Stanowisko</b>", self.cell_bold_style)
        ]]
        
        # Słownik ułatwiający szukanie zmian pracownika na dany dzień
        #teoretycznie moze miec wiele zmian w tym samym dniu
        days_map = {i: [] for i in range(1, self.days_in_month + 2)}
        print(f"ile dni ma self {self.days_in_month}")
        for shift in worker.schedule:
            days_map[shift.begin.day].append(shift)
        
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Wypełnianie danych dzień po dniu
        for day in range(1, self.days_in_month + 1):
            current_date = date(self.year, self.month, day)
            day_name = weekdays[current_date.weekday()]
            
            shifts_today = days_map[day]
            if shifts_today:
                # Jeśli pracownik ma zmiany w tym dniu
                for shift in shifts_today:
                    p_name = shift.place.name if hasattr(shift.place, 'name') else str(shift.place)
                    time_str = f"{shift.begin.strftime('%H:%M')} - {shift.end.strftime('%H:%M')}"
                    
                    table_data.append([
                        Paragraph(f"{day:02d}.{self.month:02d}.{self.year}", self.cell_style),
                        Paragraph(day_name, self.cell_style),
                        Paragraph(time_str, self.cell_style),
                        Paragraph(p_name, self.cell_style)
                    ])
            else:
                # Dzień wolny
                table_data.append([
                    Paragraph(f"{day:02d}.{self.month:02d}.{self.year}", self.cell_style),
                    Paragraph(day_name, self.cell_style),
                    Paragraph("WOLNE", self.cell_style),
                    Paragraph("-", self.cell_style)
                ])
                
        # Stylizacja tabeli
        t = Table(table_data, colWidths=[3.0*cm, 3.5*cm, 4.0*cm, 6.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            # Lekkie naprzemienne tła wierszy dla czytelności
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')])
        ]))
        
        story.append(t)
        
        # Podsumowanie godzin na dole strony
        story.append(Spacer(1, 0.5*cm))
        total_hours = worker.howManyHours()
        # Formatowanie timedelta do ładnego stringa godzinowego
        total_hours_str = f"{total_hours.total_seconds() / 3600:.1f} godz."
        story.append(Paragraph(f"<b>Suma zaplanowanych godzin:</b> {total_hours_str}", self.cell_bold_style))
        
        doc.build(story)

    def export_manager_collective_pdf(self, workers: list, output_path: str):
        """Generuje jeden zbiorczy grafik dla kierownika (Widok matrycy w układzie poziomym)"""
        # Dla kierownika ustawiamy układ POZIOMY (Landscape), ponieważ tabela jest bardzo szeroka
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1.0*cm, leftMargin=1.0*cm,
            topMargin=1.0*cm, bottomMargin=1.0*cm
        )
        
        story = []
        
        story.append(Paragraph(f"ZBIORCZY GRAFIK PRACY - KIEROWNIK BASENU", self.title_style))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f"Okres rozliczeniowy: {self.month_name} {self.year}", self.subtitle_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Konstruowanie nagłówków kolumn: [ Pracownik, 1, 2, 3, ..., Dni miesiąca ]
        header_row = [Paragraph("<b>Pracownik</b>", self.cell_bold_style)]
        for day in range(1, self.days_in_month + 1):
            header_row.append(Paragraph(f"<b>{day}</b>", self.cell_bold_style))
            
        table_data = [header_row]
        
        # Wypełnianie wierszy danymi pracowników
        for worker in workers:
            row = [Paragraph(f"<b>{worker.surname} {worker.name[0]}.</b>", self.cell_style)]
            
            # Mapowanie zmian pracownika na dni
            days_map = {i: [] for i in range(1, self.days_in_month + 1)}
            for shift in worker.schedule:
                if shift.begin.month == self.month and shift.begin.year == self.year:
                    days_map[shift.begin.day].append(shift)
                    
            for day in range(1, self.days_in_month + 1):
                shifts_today = days_map[day]
                if shifts_today:
                    # Wyświetlamy skrócony zapis godzin i opcjonalnie pierwszą literę lokacji basenu
                    cell_texts = []
                    for s in shifts_today:
                        p_name = s.place.name if hasattr(s.place, 'name') else str(s.place)
                        # np. "08-16 (B1)" albo samo "08-16"
                        cell_texts.append(f"{s.begin.strftime('%H')}-{s.end.strftime('%H')}")
                    
                    text = "<br/>".join(cell_texts)
                    row.append(Paragraph(f"<font color='#2B6CB0'><b>{text}</b></font>", self.cell_style))
                else:
                    # Dzień wolny - puste pole lub kropka dla czystości widoku
                    row.append(Paragraph("-", self.cell_style))
                    
            table_data.append(row)
            
        # Wyliczenie szerokości kolumn (Pierwsza kolumna szersza na nazwisko, reszta równomierna)
        # Dostępna szerokość na stronie A4 Landscape przy marginesach 1cm to ok. 27.7 cm
        col_widths = [2.7 * cm] + [0.8 * cm] * self.days_in_month
        
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Zaawansowane stylowanie macierzy kierownika
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 1),
            ('RIGHTPADDING', (0,0), (-1,-1), 1),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')])
        ]
        
        # Opcjonalnie: Możemy pokolorować weekendy w nagłówku tabeli, aby kierownik lepiej widział soboty/niedziele
        for day in range(1, self.days_in_month + 1):
            cur_date = date(self.year, self.month, day)
            if cur_date.weekday() in [5, 6]: # Sobota lub Niedziela
                # Dodaj lekkie wyróżnienie kolumny weekendowej w nagłówku
                t_style.append(('BACKGROUND', (day, 0), (day, 0), colors.HexColor('#2B6CB0')))
                
        t.setStyle(TableStyle(t_style))
        story.append(t)
        
        doc.build(story)