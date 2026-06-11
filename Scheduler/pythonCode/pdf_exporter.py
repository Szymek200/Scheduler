# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import calendar
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

class SchedulePDFExporter:
    def __init__(self, month: int, year: int):
        # main.py przekazuje indeks 0-11. Konwertujemy na 1-12.
        self.month = month + 1
        self.year = year
        
        self.days_in_month = calendar.monthrange(self.year, self.month)[1]
        
        self.month_name = [
            "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", 
            "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
        ][self.month]
        
        self.styles = getSampleStyleSheet()
        
        self.title_style = ParagraphStyle(
            'PDFTitle', parent=self.styles['Heading1'],
            fontName='Helvetica-Bold', fontSize=18, leading=22,
            textColor=colors.HexColor('#1A365D'), alignment=1
        )
        self.subtitle_style = ParagraphStyle(
            'PDFSubtitle', parent=self.styles['Normal'],
            fontName='Helvetica', fontSize=11, leading=14,
            textColor=colors.HexColor('#4A5568'), alignment=1
        )
        self.cell_style = ParagraphStyle(
            'PDFCell', parent=self.styles['Normal'],
            fontName='Helvetica', fontSize=8, leading=10, alignment=1
        )
        self.cell_bold_style = ParagraphStyle(
            'PDFCellBold', parent=self.styles['Normal'],
            fontName='Helvetica-Bold', fontSize=9, leading=11, alignment=1
        )
        self.cal_day_num_off_style = ParagraphStyle(
            'CalDayNumOff', parent=self.styles['Normal'],
            fontName='Helvetica', fontSize=10, leading=12, alignment=0,
            textColor=colors.HexColor('#A0AEC0')
        )

    def export_individual_pdf(self, worker, output_path: str):
        """Generuje PDF z grafikiem dla pojedynczego pracownika w formie kalendarza"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1.5*cm, leftMargin=1.5*cm,
            topMargin=1.5*cm, bottomMargin=1.5*cm
        )
        
        story = []
        story.append(Paragraph(f"INDYWIDUALNY GRAFIK PRACY (KALENDARZ)", self.title_style))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f"Pracownik: {worker.name} {worker.surname} | Okres: {self.month_name} {self.year}", self.subtitle_style))
        story.append(Spacer(1, 0.6*cm))
        
        weekdays_pl = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
        table_data = [[Paragraph(f"<b>{day}</b>", self.cell_bold_style) for day in weekdays_pl]]
        
        days_map = {i: [] for i in range(1, self.days_in_month + 1)}
        total_month_duration = timedelta(0)

       
        for shift in worker.schedule:
            if shift.begin.month == self.month and shift.begin.year == self.year:
                days_map[shift.begin.day].append(shift)
                total_month_duration += shift.duration()
        
        cal = calendar.Calendar(firstweekday=0)
        month_weeks = cal.monthdayscalendar(self.year, self.month)
        
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]
        
        current_row_idx = 1
        for week in month_weeks:
            row_content = []
            for col_idx, day in enumerate(week):
                if day == 0:
                    row_content.append(Paragraph("", self.cal_day_num_off_style))
                    t_style.append(('BACKGROUND', (col_idx, current_row_idx), (col_idx, current_row_idx), colors.HexColor('#F7FAFC')))
                else:
                    cell_elements = [f"<font color='#4A5568'><b>{day}</b></font>", "<br/>"]
                    shifts_today = days_map[day]
                    
                    if shifts_today:
                        for shift in shifts_today:
                            p_name = shift.place.name if hasattr(shift.place, 'name') else str(shift.place)
                            time_str = f"{shift.begin.strftime('%H:%M')}-{shift.end.strftime('%H:%M')}"
                            cell_elements.append(f"<font color='#2B6CB0'><b>{time_str}</b></font>")
                            cell_elements.append(f"<font color='#718096' size='7'>{p_name}</font>")
                        t_style.append(('BACKGROUND', (col_idx, current_row_idx), (col_idx, current_row_idx), colors.HexColor('#EBF8FF')))
                    else:
                        cell_elements.append("<font color='#A0AEC0'><i>WOLNE</i></font>")
                        if col_idx in [5, 6]:
                            t_style.append(('BACKGROUND', (col_idx, current_row_idx), (col_idx, current_row_idx), colors.HexColor('#EDF2F7')))
                        else:
                            t_style.append(('BACKGROUND', (col_idx, current_row_idx), (col_idx, current_row_idx), colors.white))
                            
                    full_cell_text = "<br/>".join(cell_elements)
                    row_content.append(Paragraph(full_cell_text, self.cell_style))
                    
            table_data.append(row_content)
            current_row_idx += 1
            
        col_width = 26.7 * cm / 7
        row_heights = [0.8 * cm] + [2.2 * cm] * len(month_weeks)
        
        t = Table(table_data, colWidths=[col_width]*7, rowHeights=row_heights)
        t.setStyle(TableStyle(t_style))
        story.append(t)
        
        story.append(Spacer(1, 0.4*cm))
        total_hours_str = f"{total_month_duration.total_seconds() / 3600:.1f} godz."
        story.append(Paragraph(f"<b>Suma zaplanowanych godzin w miesiącu:</b> {total_hours_str}", self.cell_bold_style))
        
        doc.build(story)


    def export_manager_collective_pdf(self, place, workers: list, output_path: str):
        """
        Generuje grafik zbiorczy dedykowany dla konkretnego BASENU (miejsca).
        Układ przypomina kalendarz, ale zawiera dodatkową kolumnę z godzinami zmian,
        a w środku wpisane są nazwiska pracowników pełniących dyżur.
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1.2*cm, leftMargin=1.2*cm,
            topMargin=1.2*cm, bottomMargin=1.2*cm
        )
        
        story = []
        place_name = place.name if hasattr(place, 'name') else str(place)
        story.append(Paragraph(f"ZBIORCZY GRAFIK OBSADY BASENU", self.title_style))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f"Obiekt: {place_name} | Okres: {self.month_name} {self.year}", self.subtitle_style))
        story.append(Spacer(1, 0.6*cm))
        
        shift_hours = set()
        for worker in workers:
            for shift in worker.schedule:
                if shift.begin.month == self.month and shift.begin.year == self.year:
                   
                    s_place_name = shift.place.name if hasattr(shift.place, 'name') else str(shift.place)
                    if s_place_name == place_name:
                        time_tuple = (shift.begin.time(), shift.end.time())
                        shift_hours.add(time_tuple)
        
        # Sortujemy godziny zmian chronologicznie
        sorted_hours = sorted(list(shift_hours))
        if not sorted_hours:
            # Wypełnienie domyślne, jeśli algorytm nic nie przypisał na ten basen
            sorted_hours = [(datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("14:00", "%H:%M").time()),
                            datetime.strptime("14:00", "%H:%M").time(), datetime.strptime("22:00", "%H:%M").time()]

        # Budowanie struktury tabeli (Kalendarz)
      
        weekdays_pl = ["Godziny", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
        table_data = [[Paragraph(f"<b>{day}</b>", self.cell_bold_style) for day in weekdays_pl]]
        
        cal = calendar.Calendar(firstweekday=0)
        month_weeks = cal.monthdayscalendar(self.year, self.month)
        
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]
        
        current_row_idx = 1
        
     
        for week_idx, week in enumerate(month_weeks):
            # Dla każdej zdefiniowanej godziny zmiany tworzymy osobny wiersz w tym tygodniu
            for hour_idx, (b_time, e_time) in enumerate(sorted_hours):
                row_content = []
                
                # Pierwsza kolumna: Przedział godzinowy zmiany
                time_str = f"{b_time.strftime('%H:%M')}\n-\n{e_time.strftime('%H:%M')}"
                row_content.append(Paragraph(f"<b>{time_str}</b>", self.cell_bold_style))
                
                # Kolumny 1-7: Dni tygodnia
                for col_idx, day in enumerate(week):
                    if day == 0:
                        # Dni poza zakresem miesiąca
                        row_content.append(Paragraph("", self.cell_style))
                        t_style.append(('BACKGROUND', (col_idx + 1, current_row_idx), (col_idx + 1, current_row_idx), colors.HexColor('#F7FAFC')))
                    else:
                        # Szukamy pracowników, którzy pracują tego dnia, w tych godzinach, na tym basenie
                        staff_today = []
                        for worker in workers:
                            for shift in worker.schedule:
                                if shift.begin.month == self.month and shift.begin.year == self.year and shift.begin.day == day:
                                    s_place_name = shift.place.name if hasattr(shift.place, 'name') else str(shift.place)
                                    if s_place_name == place_name:
                                        if shift.begin.time() == b_time and shift.end.time() == e_time:
                                            staff_today.append(f"{worker.surname} {worker.name[0]}.")
                        
                        # Konstruowanie tekstu komórki
                        cell_elements = [f"<font color='#4A5568'><b>{day}</b></font>"]
                        if staff_today:
                            # Jeśli ktoś pracuje, wpisujemy nazwiska
                            names_str = "<br/>".join(staff_today)
                            cell_elements.append(f"<font color='#2B6CB0'><b>{names_str}</b></font>")
                            t_style.append(('BACKGROUND', (col_idx + 1, current_row_idx), (col_idx + 1, current_row_idx), colors.HexColor('#EBF8FF')))
                        else:
                            # Brak obsady na danej zmianie
                            cell_elements.append("<font color='#A0AEC0'>-</font>")
                            if col_idx in [5, 6]: # Weekend
                                t_style.append(('BACKGROUND', (col_idx + 1, current_row_idx), (col_idx + 1, current_row_idx), colors.HexColor('#EDF2F7')))
                            else:
                                t_style.append(('BACKGROUND', (col_idx + 1, current_row_idx), (col_idx + 1, current_row_idx), colors.white))
                        
                        row_content.append(Paragraph("<br/>".join(cell_elements), self.cell_style))
                        
                table_data.append(row_content)
                current_row_idx += 1
                
            
            t_style.append(('LINEBELOW', (0, current_row_idx - 1), (-1, current_row_idx - 1), 1.5, colors.HexColor('#4A5568')))
            
       
        col_widths = [2.1 * cm] + [3.6 * cm] * 7
        
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle(t_style))
        story.append(t)
        
        doc.build(story)