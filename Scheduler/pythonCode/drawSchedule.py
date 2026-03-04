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
    def __init__(self, workers, places, scheduler, main_window=None):
        super().__init__()
        self.workers_list = workers
        self.place_list = places
        self.scheduler = scheduler 

        self.main_window = main_window
        
        # current week
        self.week_num = datetime.date.today().isocalendar()[1]

        base_path = os.path.dirname(__file__)
        ui_path = os.path.join(base_path, "GUI", "schedule_table.ui")

        loader = QUiLoader()
        ui_file = QFile(ui_path)
        


        if not ui_file.open(QFile.ReadOnly):
            print(f"File not found {ui_path}")
            sys.exit(-1)
            
        self.ui = loader.load(ui_file)
        ui_file.close()

        # 
        self.ui.schedule_return.clicked.connect(self.return_to_main)

        # filling combobox with workers
        self.ui.comboBox.clear() 
        for worker in self.workers_list:
            text = f"{worker.name} {worker.surname}"
            self.ui.comboBox.addItem(text)

        # Łączenie zmiany pracownika z rysowaniem grafiku
        # Używamy lambda, żeby odrzucić domyślny argument (index przesyłany przez sygnał) 
        # i pobrać go bezpośrednio wewnątrz metody
        self.ui.comboBox.currentIndexChanged.connect(self.draw_schedule)

        # Przyciski następny/poprzedni tydzień (zakładam, że masz takie metody zdefiniowane lub je dopiszesz)
        self.ui.previous.clicked.connect(self.previous_week)
        self.ui.next.clicked.connect(self.next_week)

        #forced draving after entering
        if len(self.workers_list) > 0:
            self.draw_schedule()
        

    def draw_schedule(self):
        """Rysuje grafik dla aktualnie wybranego pracownika z ComboBoxa"""
        # Pobieramy index i tabelę prosto z UI
        index = self.ui.comboBox.currentIndex()
        if index < 0 or index >= len(self.workers_list):
            return # worker not selected
            
        schedule_table = self.ui.tableWidget # Upewnij się, że Twoja tabela nazywa się tableWidget w UI!

        schedule_table.clearContents() 
        schedule_table.setColumnCount(7)
        schedule_table.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        schedule_table.setRowCount(0)

        # Pobieramy wybranego pracownika
        worker = self.workers_list[index]
        
        # Obliczamy rok i miesiąc na podstawie aktualnego numeru tygodnia (self.week_num)
        # Bierzemy pierwszy dzień danego tygodnia, żeby sprawdzić jaki to miesiąc
        rok_startowy = datetime.date.today().year
        data_tygodnia = datetime.date.fromisocalendar(rok_startowy, self.week_num, 1)
        
        current_year = data_tygodnia.year
        current_month = data_tygodnia.month
        
        # Wywołujemy nową wersję funkcji
        self.scheduler.defaultSchedule(worker, current_year, current_month)

        # tracking things in every column
        row_trackers = {i: 0 for i in range(7)}

        for shift in worker.rqSchedule:
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

                
                shift_text = f"{shift.begin.strftime('%H:%M')} - {shift.end.strftime('%H:%M')}"
                
                
                miejsce = getattr(shift.place, 'name', shift.place)
                shift_text += f"\n{miejsce}"

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


    def previous_week(self):
        """Cofa harmonogram o jeden tydzień i rysuje go ponownie."""
        self.week_num -= 1
        
        # Zabezpieczenie przed zejściem poniżej 1. tygodnia roku
        if self.week_num < 1:
            self.week_num = 52 # Cofamy się do ostatniego tygodnia poprzedniego roku
            
        # Opcjonalnie: Jeśli masz w UI label pokazujący numer tygodnia, zaktualizuj go tutaj
        # np. self.ui.week_label.setText(f"Tydzień: {self.week_num}")
            
        self.draw_schedule() # Rysujemy grafik od nowa dla nowego tygodnia

    def next_week(self):
        """Przesuwa harmonogram o jeden tydzień do przodu i rysuje go ponownie."""
        self.week_num += 1
        
        # Zabezpieczenie przed wyjściem poza 52. tydzień roku
        if self.week_num > 52:
            self.week_num = 1 # Przechodzimy do pierwszego tygodnia nowego roku
            
        # Opcjonalnie: aktualizacja tekstu w UI
        # np. self.ui.week_label.setText(f"Tydzień: {self.week_num}")
            
        self.draw_schedule() # Rysujemy grafik od nowa dla nowego tygodnia