from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

import os
import sys
#first filename than class name
from worker import Worker
from place import Place
from shift import ShiftPlace
from scheduler import Scheduler

import datetime

import rules

class MainWindow(QMainWindow):
    def __init__(self, workers, places):
        super().__init__()
        self.workers_list = workers
        self.place_list = places

        week_num = 1

          #current pash
        base_path = os.path.dirname(__file__)
        # adding folder with GUI
        ui_path = os.path.join(base_path, "GUI", "schedule_table.ui")

        # loading .ui file
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        
        if not ui_file.open(QFile.ReadOnly):
            print(f"File not found {ui_path}")
            sys.exit(-1)
            
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.ui.schedule_return.clicked.connect(self.return_to_main)

        for worker in self.workers_list:
            text = worker.name + " " + worker.surname
            self.dialog.comboBox.addItem(text)

        self.ui.moj_combobox.currentIndexChanged.connect(self.draw_schedule)

        self.ui.previous.clicked.connect(lambda: self.set_page(-1))
        self.ui.next.clicked.connect(lambda: self.set_page(1))

        self.ui.show() 



    def worker_rqSchedule(self):

        self.ui.main_menu_container.hide()
     
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "schedule_table.ui")
       
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        
        self.dialog.moj_combobox.clear()
        self.dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        self.dialog.schedule_return.clicked.connect(self.return_to_main)

        for worker in self.workers_list:
            text = worker.name + " " + worker.surname
            self.dialog.comboBox.addItem(text)

        self.dialog.moj_combobox.currentIndexChanged.connect(self.draw_schedule)

        self.dialog.previous.connect( self.previous_week)
        self.dialog.next.connect(self.next_week(-1))

        self.dialog.show() 


    def draw_schedule(self, index, schedule_table):

        schedule_table.clearContents() 
        schedule_table.setColumnCount(7)
        schedule_table.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])


        #every element in widget table is created as TableWidgetItem

        self.scheduler.defaultSchedule(self.workers_list[index])


        schedule_table.setRowCount(0)

        # Pobieramy wybranego pracownika
        worker = self.workers_list[index]
        self.scheduler.defaultSchedule(worker)

        #which row is free for every column
        row_trackers = {i: 0 for i in range(7)}

        for shift in worker.rqSchedule:
            
            # Pobieramy numer tygodnia z daty zmiany (np. od 1 do 52)
            shift_week = shift.begin.isocalendar()[1] 
            
            #shifts from this week
            if shift_week == self.week_num:
                
                # .weekday() returns: 0 for Monday, 6 for Sunday
                col_index = shift.begin.weekday() 
                
                # check which row 
                row_index = row_trackers[col_index]

                # Jeśli brakuje nam wierszy w tabeli graficznej, dodajemy nowy na sam dół
                if row_index >= schedule_table.rowCount():
                    schedule_table.insertRow(schedule_table.rowCount())

                # text for elem
                shift_text = f"{shift.begin.strftime('%H:%M')} - {shift.end.strftime('%H:%M')}"
                
                # add place if exists
                if hasattr(shift, 'places') and shift.places:
                    places_str = ", ".join(shift.places)
                    shift_text += f"\n{places_str}"

                # create element 
                item = QTableWidgetItem(shift_text)
                schedule_table.setItem(row_index, col_index, item)

                #increase row for particular column
                row_trackers[col_index] += 1
                
        
        schedule_table.resizeRowsToContents()
         