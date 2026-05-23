import os
import sys
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QObject
import datetime

# Załóżmy, że potrzebujesz schedulera
from scheduler import Scheduler

class MainWindow(QObject):
    #add scheduler to constructor
    def __init__(self, workers, places, scheduler, window_type, month, main_window=None):
        super().__init__()
        self.workers_list = workers
        self.place_list = places
        self.scheduler = scheduler 

        #it decides of it is window for places or workers
        self.window_type = window_type

        self.main_window = main_window
        
        # current week
        base_path = os.path.dirname(__file__)
        ui_path = os.path.join(base_path, "GUI", "schedule_table.ui")

        loader = QUiLoader()
        ui_file = QFile(ui_path)
        


        if not ui_file.open(QFile.ReadOnly):
            print(f"File not found {ui_path}")
            sys.exit(-1)
            
        self.ui = loader.load(ui_file)
        ui_file.close()

        #month combo box
    
        
        #current month as default
        #current_month_idx = datetime.date.today().month - 1
        current_month_idx = month
        self.ui.monthCombo.setCurrentIndex(current_month_idx)

        # change month -> refresh table
        self.ui.monthCombo.currentIndexChanged.connect(self.update_month_view)

        self.ui.schedule_return.clicked.connect(self.return_to_main)

        # filling combobox with workers
        self.ui.comboBox.clear() 

        if(window_type == 'worker' or window_type == 'request_worker'):
            for worker in self.workers_list:
                text = f"{worker.name} {worker.surname}"
                self.ui.comboBox.addItem(text)
        elif window_type == 'place':
            #for places
            for place in self.place_list:
                text = f"{place.name}"
                self.ui.comboBox.addItem(text)



        # Łączenie zmiany pracownika z rysowaniem grafiku
        # Używamy lambda, żeby odrzucić domyślny argument (index przesyłany przez sygnał) 
        # i pobrać go bezpośrednio wewnątrz metody
        self.ui.comboBox.currentIndexChanged.connect(self.draw_schedule)

        # Przyciski następny/poprzedni tydzień (zakładam, że masz takie metody zdefiniowane lub je dopiszesz)
        self.ui.previous.clicked.connect(self.previous_week)
        self.ui.next.clicked.connect(self.next_week)

        self.update_month_view()

        #forced draving after entering
        if len(self.workers_list) > 0:
            self.draw_schedule()
        

    def draw_schedule(self):
        """Rysuje grafik i aktualizuje daty w nagłówkach"""
        index = self.ui.comboBox.currentIndex()
        if index < 0:
            return
        
        if hasattr(self, 'overlay_label'):
            self.overlay_label.hide()

            
        if self.window_type == 'place':
            place = self.place_list[index]
        else:
            worker = self.workers_list[index]

        schedule_table = self.ui.tableWidget
        
        # --- LOGIKA ODŚWIEŻANIA DAT W NAGŁÓWKACH ---
        year = datetime.date.today().year
        # Wyznaczamy poniedziałek dla aktualnie ustawionego self.week_num
        monday_of_week = datetime.date.fromisocalendar(year, self.week_num, 1)
        
        days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        headers = []

        for i in range(7):
            # Obliczamy datę dla każdego dnia (poniedziałek + i dni)
            current_day_date = monday_of_week + datetime.timedelta(days=i)
            # Tworzymy tekst nagłówka z nową linią \n
            header_text = f"{days_names[i]}\n{current_day_date.strftime('%d.%m')}"
            headers.append(header_text)

        # Ustawiamy nowe etykiety na tabeli
        schedule_table.setColumnCount(7)
        schedule_table.setHorizontalHeaderLabels(headers)
        # -------------------------------------------

        # Czyszczenie i rysowanie reszty tabeli
        schedule_table.clearContents()
        schedule_table.setRowCount(0)
        
        # Ważne: defaultSchedule musi dostać miesiąc z ComboBoxa, a nie z daty dzisiejszej
        selected_month = self.ui.monthCombo.currentIndex() + 1

        """
        if self.window_type == 'request_worker':
            #request schedule
            self.scheduler.defaultSchedule(worker, year, selected_month)
        else:
            #else we check if official schedule was calculated
            if self.scheduler.ready!= 1:
                from PySide6.QtWidgets import QLabel
                from PySide6.QtCore import Qt
                self.overlay_label = QLabel(self.ui.tableWidget)
                
                # Stylowanie, aby label był widoczny i czytelny
                self.overlay_label.setStyleSheet("""
                   # background-color: rgba(255, 255, 255, 230);
                   # font-size: 18px;
                   # font-weight: bold;
                   # color: #7f8c8d;
                #)
                #self.overlay_label.setAlignment(Qt.AlignCenter)
            
                # Dopasowujemy rozmiar labela do aktualnego rozmiaru tabeli
               # self.overlay_label.resize(self.ui.tableWidget.size())
               # self.overlay_label.setText("Schedule not available")
              #  self.overlay_label.show()
              #return"""


        row_trackers = {i: 0 for i in range(7)}

        shifts_to_draw = []

        if self.window_type == 'request_worker':
            worker = self.workers_list[index]
            self.ui.schedule_label.setText(f"REQUESTED AVAILABILITY")
            # Generujemy i bierzemy rqSchedule
            self.scheduler.defaultRequestedSchedule(worker, year, selected_month)
            shifts_to_draw = worker.rqSchedule

        elif self.window_type == 'worker':
            if self.scheduler.ready == 1:
                worker = self.workers_list[index]
                self.ui.schedule_label.setText(f"FINAL SCHEDULE")
                shifts_to_draw = worker.schedule
            else:
                # Jeśli scheduler.ready != 1, blokujemy widok
                self.ui.schedule_label.setText("SCHEDULE NOT READY")
                
                # POPRAWKA: Zamiast wywoływać nieistniejącą funkcję toggle_overlay, 
                # po prostu czyścimy zawartość tabeli i przerywamy rysowanie.
                self.ui.tableWidget.clearContents()
                return

        elif self.window_type == 'place':
            place = self.place_list[index]
            self.ui.schedule_label.setText(f"PLACE OCCUPANCY")
            #we create default schedule only ifit isn't created
            if self.scheduler.ready != 1:
                self.scheduler.defaultPlaceSchedule(year, selected_month)
            shifts_to_draw = place.schedule
        else:
            return
       

        for shift in shifts_to_draw:
        # Pobieramy numer tygodnia z daty zmiany
            shift_week = shift.begin.isocalendar()[1] 
        
            # only particular week
            if shift_week == self.week_num:
                
                # weekday() returns: 0=Monday, 6=Sunday
                col_index = shift.begin.weekday() 
                row_index = row_trackers[col_index]

                # adding new row
                if row_index >= schedule_table.rowCount():
                    schedule_table.insertRow(schedule_table.rowCount())

                shift_text = ''

      
        
                if self.window_type == 'place':
                    # Zabezpieczamy się na wypadek, gdyby zmiana nie miała jeszcze przypisanego pracownika (jest None)
                    if shift.worker:
                        worker_info = f"{shift.worker.name} {shift.worker.surname}"
                    else:
                        worker_info = "Empty" # LUB: "Brak"
                        
                    shift_text = f"{shift.begin.strftime('%H:%M')} - {shift.end.strftime('%H:%M')} \n {worker_info} "
                    
                elif self.window_type == 'worker' or self.window_type == 'request_worker':
                        # Wyciągamy konkretnie nazwę miejsca, a nie cały obiekt w pamięci
                        # Używamy getattr na wypadek gdyby shift.place był zwykłym stringiem (zależnie od tego jak wczytujesz reguły)
                        place_name = getattr(shift.place, 'name', shift.place)
                        
                        shift_text = f"{shift.begin.strftime('%H:%M')} - {shift.end.strftime('%H:%M')} \n {place_name} "
            
                item = QTableWidgetItem(shift_text)
                schedule_table.setItem(row_index, col_index, item)

                row_trackers[col_index] += 1

                
        schedule_table.resizeRowsToContents()


    def set_page(self, delta):
        """Zmienia tydzień i odświeża grafik"""
        self.week_num += delta
        self.draw_schedule()

    def return_to_main(self):
        """Zamyka okno grafiku i przywraca okno główne"""
        self.ui.close()
        if self.main_window:
            self.main_window.show()

    def update_month_view(self):
        """Ustawia tydzień na pierwszy tydzień wybranego miesiąca."""
        selected_month = self.ui.monthCombo.currentIndex() + 1
        year = datetime.date.today().year
        
        # Znalezienie pierwszego dnia miesiąca i jego numeru tygodnia
        first_day = datetime.date(year, selected_month, 1)
        self.week_num = first_day.isocalendar()[1]
        
        self.draw_schedule()


    def previous_week(self):
        print("Kliknięto Previous") # Debug
        selected_month = self.ui.monthCombo.currentIndex() + 1
        year = datetime.date.today().year
        
        potential_week = self.week_num - 1
        first_day_of_week = datetime.date.fromisocalendar(year, potential_week, 1)
        last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
        
        if first_day_of_week.month == selected_month or last_day_of_week.month == selected_month:
            self.week_num = potential_week
            self.draw_schedule()

    def next_week(self):
        print("Kliknięto Next") # Debug
        selected_month = self.ui.monthCombo.currentIndex() + 1
        year = datetime.date.today().year
        
        potential_week = self.week_num + 1
        first_day_of_week = datetime.date.fromisocalendar(year, potential_week, 1)
        last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
        
        if first_day_of_week.month == selected_month or last_day_of_week.month == selected_month:
            self.week_num = potential_week
            self.draw_schedule()