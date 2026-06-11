import sys
import os
from PySide6.QtWidgets import QApplication, QHeaderView, QMainWindow, QPushButton, QTableWidgetItem, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
#for creating rule form
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTableWidgetItem, 
                               QWidget, QVBoxLayout, QFormLayout, QLabel, QSpinBox, 
                               QListWidget, QListWidgetItem, QHBoxLayout, QComboBox, 
                               QDialog, QDialogButtonBox, QLineEdit, QFileDialog,)
from PySide6.QtCore import Qt

#regular expression - input veryfication
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QCloseEvent


#different opening and closing window
from PySide6.QtCore import QObject 

#first filename than class name
from worker import Worker
from place import Place
from shift import ShiftPlace
from genetic import GeneticScheduler

from drawSchedule import MainWindow as ScheduleWindow
from datetime import datetime, time, timedelta
import rules

from saving import Saving
import sys
import traceback
from pdf_exporter import SchedulePDFExporter

import myThreading

#for errors showing
def custom_excepthook(exc_type, exc_value, exc_traceback):
    print("\n--- BŁĄD KRYTYCZNY PYTHON ---", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("-----------------------------\n", file=sys.stderr)

sys.excepthook = custom_excepthook

class MainWindow(QObject):


  

    # Definiujemy wzorzec: 
    # ^ - begining of text
    # \d - every number
    # {11} - no more no less
    # $ - end of text
    pesel_regex = QRegularExpression(r"^\d{11}$")

    natural_numbers = QRegularExpression(r"^\d+$")

    hours_regex = QRegularExpression(r"^(?:[01]?\d|2[0-3])[:.][0-5]\d$")

    def __init__(self):

        super().__init__()
        self.workers_list = []
        self.place_list = []

        self.saving = Saving(self.workers_list, self.place_list, "MojeDane")
        
        
        self.saving.reading()
        
        #rules typoe dictionary
        self.rules_registry = {
            "Free Weekend": self.create_empty_ui,
            "Between Shifts": self.create_between_shifts_ui, # Jeśli nie ma parametrów, dajemy empty
            "Unordered Rule": self.create_unordered_ui,
            "Cyclic Rule": self.create_cyclic_ui,
            "Place Specific Rule": self.create_empty_ui
        }

        

        #current pash
        base_path = os.path.dirname(__file__)

        # adding folder with GUI
        ui_path = os.path.join(base_path, "GUI", "main_window.ui")

        # loading .ui file
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        
        if not ui_file.open(QFile.ReadOnly):
            print(f"File not found {ui_path}")
            sys.exit(-1)

        #when we don't pass self argument our window won't have parent -which is good
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.ui.setWindowTitle("Scheduler")

        #our own method for closing window
        self.ui.closeEvent = self.closeEvent

        #flagi czy dany grafik jest utworzony
        self.workplace_requirements_done = False
        self.worker_availability_done = False
       

        #activating button
        self.ui.add_worker.clicked.connect(self.add_worker)
        self.ui.add_workplace.clicked.connect(self.add_workplace)
        self.ui.view_worker.clicked.connect(self.view_worker)
        self.ui.view_workplace.clicked.connect(self.view_workplace)

        self.ui.workplace_availability.clicked.connect(self.view_workplace_aval)

        self.ui.create_schedule.clicked.connect(self.create_schedule)

        self.ui.worker_schedule.clicked.connect(self.worker_schedule)

        self.btn_save_schedule = self.ui.findChild(QPushButton, "save_schedule")

        # Podpięcie zdarzenia kliknięcia:
        self.btn_save_schedule.clicked.connect(self.handle_save_all_schedules)

        self.ui.worker_availability.clicked.connect(self.open_schedule_view)

        self.main_year_edit = self.ui.findChild(QLineEdit, "year_line_edit")  
        self.main_month_combo = self.ui.findChild(QComboBox, "month_combo_box")

        today = datetime.today()

        plan_month = 0
        plan_year = today.year

        # today.month zwraca format systemowy (1 - 12)
        if today.month == 12:
            # Jeśli jest grudzień (12), planujemy na styczeń (0) kolejnego roku
            self.main_month_combo.setCurrentIndex(0)
            self.main_year_edit.setText(str(today.year + 1))
            plan_year = today.year + 1
            plan_month = 0
        else:
            # planujemy na nastepny miesiac(wartosci 0 - 11)
    
            self.main_month_combo.setCurrentIndex(today.month)
            plan_month = today.month
            self.main_year_edit.setText(str(today.year))
            plan_year = today.year
            
        self.scheduler = GeneticScheduler(self.workers_list, self.place_list, plan_month, plan_year )

        if self.main_year_edit and self.main_month_combo:
          
            self.main_year_edit.textChanged.connect(self.handle_date_selection_changed)
            self.main_month_combo.currentIndexChanged.connect(self.handle_date_selection_changed)



    def handle_date_selection_changed(self):

        self.reset_schedule_flags()
       
        year_str = self.main_year_edit.text().strip()
        if not year_str.isdigit() or len(year_str) < 4:
            return  

        selected_year = int(year_str)

        selected_month = self.main_month_combo.currentIndex() 

        self.scheduler.updateDate(selected_month, selected_year)

    def closeEvent(self, event: QCloseEvent):
      
        try:
            self.saving.saving()
            print("[SAVER SUCCESS] Dane i nowe reguły zostały zapisane.")
        except Exception as e:
            print(f"[SAVER ERROR] Coś poszło nie tak: {e}")
            
        event.accept()

    def _execute_workplace_requirements_logic(self):
        """Wykonuje logikę kroku 1 w tle, bez otwierania okna UI."""
        print("[LOGIKA] Przetwarzanie wymagań miejsc pracy w tle...")
        self.schedule_window = ScheduleWindow(self.workers_list, self.place_list,self.scheduler,'place',self.main_month_combo.currentIndex(), self.ui)
        self.workplace_requirements_done = True



    def view_workplace_aval(self):

        self.workplace_requirements_done = True
        self.schedule_window = ScheduleWindow(self.workers_list, self.place_list,self.scheduler,'place',self.main_month_combo.currentIndex(), self.ui)
  
        self.ui.hide()

        self.schedule_window.ui.show()

 

    def generate_pdf_report(self):
    
        exporter = SchedulePDFExporter(month=self.scheduler.month, year=self.scheduler.year)
        
        #Dla kazdego pracownika
        print("[PDF] Generowanie indywidualnych grafików...")
        for worker in self.scheduler.workers:
           
            filename = f"grafik_{worker.name}_{worker.surname}.pdf"
            exporter.export_individual_pdf(worker, filename)
            
        # grafik na basen
        print("[PDF] Generowanie grafiku zbiorczego dla kierownikow...")
        for place in self.scheduler.places:
            pdf_name = "grafik_zbiorczy_" + place.name+ ".pdf"
            exporter.export_manager_collective_pdf(
                place = place,
                workers=self.scheduler.workers, 
                output_path=pdf_name
            )
        print("[PDF] Wszystkie pliki PDF zostały pomyślnie wygenerowane!")

        
    #generowanie grafiku w watku
    def create_schedule(self):

        if not self.workplace_requirements_done:
            print("[AUTO-CREATE] Brak Kroku 1. Uruchamianie Workplace requirements...")
            self._execute_workplace_requirements_logic()
            
            
        # 2. Jeśli nie zrobiono dostępności pracowników, uruchom krok 2
        if not self.worker_availability_done:
            print("[AUTO-CREATE] Brak Kroku 2. Uruchamianie Worker availability...")
            self._execute_worker_availability_logic()
            
           
        self.scheduler.ready = 0
        
        # okno ladowania
        self.loading_dialog = myThreading.LoadingDialog(self.ui)
        
        # generator grafiku
        self.scheduling_thread = myThreading.SchedulingWorker(self.scheduler)
        
        self.scheduling_thread.finished_signal.connect(self.handle_schedule_finished)
        
        self.scheduling_thread.start()
        self.loading_dialog.show() 

    def handle_save_all_schedules(self):
        """Obsługuje wybór folderu i zapisuje wszystkie PDF-y do nowego podfolderu."""
        
        if not hasattr(self, 'scheduler') or self.scheduler.ready == 0:
            QMessageBox.warning(self.ui, "Brak grafiku", "Grafik nie został jeszcze wygenerowany! Wygeneruj grafik przed zapisem.")
            return

        base_dir = QFileDialog.getExistingDirectory(
            self.ui, 
            "Wybierz miejsce docelowe do zapisu grafików",
            os.path.expanduser("~")
        )
        
        if not base_dir:
            return # uzytkownik anulowal okno

        try:
           
            current_month_idx = self.main_month_combo.currentIndex()
            current_year = int(self.main_year_edit.text().strip())
            
            month_num = current_month_idx + 1
            timestamp = datetime.now().strftime("%H%M%S")
            folder_name = f"Grafiki_{current_year}_{month_num:02d}_{timestamp}"
            
            target_folder_path = os.path.join(base_dir, folder_name)
            os.makedirs(target_folder_path, exist_ok=True)

            # eksporter pdf
            exporter = SchedulePDFExporter(current_month_idx, current_year)

            # indywidualni
            personal_folder = os.path.join(target_folder_path, "Grafiki_Indywidualne")
            os.makedirs(personal_folder, exist_ok=True)
            
            for worker in self.scheduler.workers:
                safe_name = f"{worker.surname}_{worker.name}".replace(" ", "_")
                file_path = os.path.join(personal_folder, f"Grafik_{safe_name}.pdf")
                exporter.export_individual_pdf(worker, file_path)

            #zbiorowy
            pools_folder = os.path.join(target_folder_path, "Grafiki_Zbiorcze_Baseny")
            os.makedirs(pools_folder, exist_ok=True)
            
            if hasattr(self, 'place_list') and self.place_list:
                for place in self.place_list:
                    p_name = place.name if hasattr(place, 'name') else str(place)
                    safe_place_name = p_name.replace(" ", "_")
                    file_path = os.path.join(pools_folder, f"Grafik_Zbiorczy_{safe_place_name}.pdf")
                    
                    exporter.export_manager_collective_pdf(place, self.scheduler.workers, file_path)

            QMessageBox.information(
                self.ui, 
                "Sukces", 
                f"Wszystkie grafiki zostały pomyślnie zapisane w folderze:\n{target_folder_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self.ui, 
                "Błąd krytyczny", 
                f"Wystąpił błąd podczas zapisywania plików:\n{str(e)}"
            )

    
    def handle_schedule_finished(self, result):
      

        if hasattr(self, 'loading_dialog') and self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog.deleteLater()
            
        if hasattr(self, 'scheduling_thread') and self.scheduling_thread:
            self.scheduling_thread.quit()
            self.scheduling_thread.wait()
            self.scheduling_thread.deleteLater()

        if result == -1:
            QMessageBox.information(None, "Failed to create schedule", "Check availability.")
        else:
            QMessageBox.information(None, "Success", "Schedule created")
           

    def worker_schedule(self):

        if(self.scheduler.ready == 0):
            QMessageBox.information(None, "Not available", "Schedule hasn't been created yet")
        else:

            self.schedule_window = ScheduleWindow(self.workers_list, self.place_list, self.scheduler, 'worker', self.scheduler.month, self.ui)
            self.ui.hide()
            self.schedule_window.ui.show()

    def add_worker(self):
     
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "add_worker_widget.ui")
       
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        
        
        self.dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        validator = QRegularExpressionValidator(self.pesel_regex, self)
        #adding to particular ui object
        self.dialog.pesel_line.setValidator(validator)
        #char limit in ui
        self.dialog.pesel_line.setMaxLength(11)

        validator2 = QRegularExpressionValidator(self.natural_numbers, self)

        self.dialog.etat_line.setValidator(validator2)

        wynik = self.dialog.exec() 

        if wynik == 1: # Jeśli użytkownik kliknął OK (standard w QDialog)
           name = self.dialog.name_line.text()
           surname = self.dialog.surname_line.text()
           pesel = self.dialog.pesel_line.text()
 
           worker = Worker(name, surname, pesel)

           self.workers_list.append(worker)
        
           self.reset_schedule_flags()


    def _execute_worker_availability_logic(self):
        """Wykonuje logikę kroku 2 w tle, bez otwierania okna UI."""
        print("[LOGIKA] Przetwarzanie dostępności pracowników v tle...")
        # Zabezpieczamy wykonanie kroku 1 w tle, jeśli nie był zrobiony
        if not self.workplace_requirements_done:
            self._execute_workplace_requirements_logic()
            
        # Aktualizacja daty lub załadowanie preferencji do schedulera w tle:
        current_month_idx = self.main_month_combo.currentIndex()
        current_year = int(self.main_year_edit.text().strip())
        self.scheduler.updateDate(current_month_idx, current_year)

        self.schedule_window = ScheduleWindow(self.workers_list, self.place_list,self.scheduler,'request_worker', self.main_month_combo.currentIndex(), self.ui)

        
        self.worker_availability_done = True    

    def reset_schedule_flags(self):
        """Resetuje flagi kroków, wymuszając ponowne przetworzenie logiki w tle."""
        self.workplace_requirements_done = False
        self.worker_availability_done = False
        print("[FLAGI] Dane uległy zmianie – zresetowano flagi generowania grafiku.")  

    #opens requested shedule for worker
    def open_schedule_view(self):

        if not self.workplace_requirements_done:
            print("[AUTO] Uruchamianie automatycznego przygotowania wymagań miejsc pracy...")
            self._execute_workplace_requirements_logic()
            # Ponieważ view_workplace_aval ukrywa okno i otwiera nowe, przerywamy wykonywanie,
            # aby nie otworzyć dwóch okien na raz.
            

        # Oznaczenie, że dostępność pracowników została otwarta
        self.worker_availability_done = True

        #create new window and class
        self.schedule_window = ScheduleWindow(self.workers_list, self.place_list,self.scheduler,'request_worker', self.main_month_combo.currentIndex(), self.ui)
  
        self.ui.hide()

        self.schedule_window.ui.show()

    def add_workplace(self):
     
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "add_workplace_widget.ui")
       
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        
        
        self.dialog = loader.load(ui_file, self.ui)
        ui_file.close()
    
        #focus on this window unless it is closed
        wynik = self.dialog.exec() 
      
        if wynik == 1: #when ok is pressed
           name = self.dialog.name_line.text()
           address = self.dialog.address_line.text()

           place = Place(name, address)
           self.place_list.append(place)
           self.reset_schedule_flags()
           

    def view_workplace(self):

        #disappear main menu
        self.ui.main_menu_container.hide()
     
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "workplace_list.ui")
       
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        
        
        self.place_view = loader.load(ui_file, self.ui)
        ui_file.close()

        self.place_view.return_to_main.clicked.connect(self.return_to_main)

        header = self.place_view.workplace_list.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        

        for i in range(len(self.place_list)):
            #create new row
            self.place_view.workplace_list.insertRow(i)


    
            #adding content to columnsclea
            self.place_view.workplace_list.setItem(i, 0, QTableWidgetItem(self.place_list[i].name))
            self.place_view.workplace_list.setItem(i, 1, QTableWidgetItem(self.place_list[i].address))
           

            #adding button to last column

            
            btn_rules = QPushButton("Rules")
            
            # Łączymy kliknięcie z funkcją otwierającą okno
            # Używamy lambda, aby przekazać dane o tym konkretnym pracowniku
            #idx is needed so lamba will remember its index
            #checked = False because when button is clicked it is returned as first value
            btn_rules.clicked.connect(lambda checked = False, obj=self.place_list[i]: self.manage_rules(obj))
            
            # Wstawiamy przycisk do tabeli
            self.place_view.workplace_list.setCellWidget(i, 3, btn_rules)

        self.place_view.show() 

    def view_worker(self):

        self.ui.main_menu_container.hide()
     
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "workers_list.ui")
       
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        
        
        self.workers_view = loader.load(ui_file, self.ui)
        ui_file.close()

        self.workers_view.return_to_main.clicked.connect(self.return_to_main)

        header = self.workers_view.workers_list.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        for i in range(len(self.workers_list)):
            #create new row
            self.workers_view.workers_list.insertRow(i)


    
            #adding content to columns
            self.workers_view.workers_list.setItem(i, 0, QTableWidgetItem(self.workers_list[i].name))
            self.workers_view.workers_list.setItem(i, 1, QTableWidgetItem(self.workers_list[i].surname))
            self.workers_view.workers_list.setItem(i, 2, QTableWidgetItem(self.workers_list[i].pesel))

            #adding button to last column

            
            btn_rules = QPushButton("Rules")
            
            # Łączymy kliknięcie z funkcją otwierającą okno
            # Używamy lambda, aby przekazać dane o tym konkretnym pracowniku
            #idx is needed so lamba will remember its index
            #checked = False because when button is clicked it is returned as first value
            btn_rules.clicked.connect(lambda checked = False, obj=self.workers_list[i]: self.manage_rules(obj))
            
            # Wstawiamy przycisk do tabeli
            self.workers_view.workers_list.setCellWidget(i, 3, btn_rules)


       

         # 4. Wyświetlenie jako okno modalne
        # .exec() zatrzymuje kod w tym miejscu, aż zamkniesz okno
        self.workers_view.show() 

    def return_to_main(self):


        #close view if exists
        if hasattr(self, 'workers_view'):
            self.workers_view.close()
    
    
        if hasattr(self, 'place_view'):
            self.place_view.close()

        #focus on main window

        self.ui.activateWindow() 
        self.ui.raise_()         # for Mac or Windows systems
        self.ui.setFocus()       # active coursor

        #show mian manu buttons
        self.ui.main_menu_container.show()


    #RULES WINDOW
          
    def manage_rules(self, entity):

        #entity is worker or place which wants to add new rule
        self.current_entity = entity 
        
        # if self.rules = [] exists
        if not hasattr(self.current_entity, 'rules'):
            self.current_entity.rules = []

        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "rule_window.ui")
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.rules_dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        #cleaning widget
        while self.rules_dialog.rule_form.count() > 0:
            widget = self.rules_dialog.rule_form.widget(0)
            self.rules_dialog.rule_form.removeWidget(widget)
            widget.deleteLater()

        self.rules_dialog.combo_rule_type.clear()

        # building pages 
        for rule_name, ui_builder in self.rules_registry.items():

      

            #name in combo box
            self.rules_dialog.combo_rule_type.addItem(rule_name)
            
            page_widget = ui_builder()
            self.rules_dialog.rule_form.addWidget(page_widget)

        self.rules_dialog.combo_rule_type.currentIndexChanged.connect(self.rules_dialog.rule_form.setCurrentIndex)

        self.rules_dialog.return_view.clicked.connect(self.rules_dialog.close)
        self.rules_dialog.add_rule.clicked.connect(self.add_rule_handler)
        self.rules_dialog.delete_rule.clicked.connect(self.delete_rule_handler)

        self.refresh_rules_table()
        self.rules_dialog.exec()


    #show all rules in rule window
    def refresh_rules_table(self):
        # 1. KRYTYCZNE: Ustawiamy liczbę kolumn i ich nagłówki!
        self.rules_dialog.rules_list.setColumnCount(2)
        self.rules_dialog.rules_list.setHorizontalHeaderLabels(["Rule Details", "Type"])
        
        # 2. Czyścimy wiersze przed ponownym załadowaniem
        self.rules_dialog.rules_list.setRowCount(0)
        
        for i, rule in enumerate(self.current_entity.rules):
            self.rules_dialog.rules_list.insertRow(i)
           
            # 3. Wyciągamy typ i nazwę (zabezpieczone getattr)
      
            nazwa_reguly = getattr(rule, 'name', 'Brak nazwy')
            typ = rule.__class__.__name__
            
            # Łączymy to w jeden czytelny tekst
            wyswietlany_tekst = f" {nazwa_reguly}"
            
            # 4. Dodajemy elementy do kolumny 0 i kolumny 1
            self.rules_dialog.rules_list.setItem(i, 0, QTableWidgetItem(wyswietlany_tekst))
            self.rules_dialog.rules_list.setItem(i, 1, QTableWidgetItem(typ))
            
        self.rules_dialog.rules_list.horizontalHeader().setStretchLastSection(True)


    def add_rule_handler(self):
        rule_type = self.rules_dialog.combo_rule_type.currentText()
        rule_name = self.rules_dialog.rule_name.text()
        
        # obecnie wybrany widget strony formularza
        current_page = self.rules_dialog.rule_form.currentWidget()
        
        new_rule = None

        if rule_type == "Free Weekend":
            new_rule = rules.FreeWeekend(self.current_entity, rule_name)

        elif rule_type == "Between Shifts":
            rest_widget = current_page.findChild(QSpinBox, "rest_hours_input")
            if rest_widget:
                hours_value = rest_widget.value()
                rest_timedelta = timedelta(hours=hours_value)
                new_rule = rules.BetweenShifts(self.current_entity, rule_name, rest_timedelta) 
            
        elif rule_type == "Unordered Rule":
            shift_list_widget = current_page.findChild(QListWidget, "unordered_shift_list")
            if shift_list_widget and shift_list_widget.count() > 0:
                shifts_array = []
                for i in range(shift_list_widget.count()):
                    item = shift_list_widget.item(i)
                    shift_obj = item.data(Qt.UserRole)
                    shifts_array.append(shift_obj)
                new_rule = rules.UnorderedRule(shifts_array, rule_name)
            else:
                print("Błąd: Nie dodano żadnych zmian do reguły!")
                
        elif rule_type == "Cyclic Rule":
            interval_widget = current_page.findChild(QSpinBox, "interval_input")
            if interval_widget and hasattr(current_page, 'selected_begin_shift') and current_page.selected_begin_shift:
                interval = interval_widget.value()
                begin_shift = current_page.selected_begin_shift
                new_rule = rules.CyclicRule(begin_shift, timedelta(days=interval), rule_name)
            else:
                print("Błąd: Musisz najpierw ustawić zmianę początkową (Set Begin Shift)!")

        # ZAPIS I GENEROWANIE ID
        if new_rule:
            base_rule_class = new_rule.__class__.__base__.__base__
            if not hasattr(base_rule_class, 'idBase'):
                new_rule.id = rules.Rule.idBase
                rules.Rule.idBase += 1
            else:
                new_rule.id = base_rule_class.idBase
                base_rule_class.idBase += 1
            
            self.current_entity.rules.append(new_rule)
            self.refresh_rules_table()
            self.rules_dialog.rule_name.clear()

            self.reset_schedule_flags()
            
            # Bezpieczny zapis na dysk
            try:
                self.saving.saving()
                print(f"[SYSTEM SUCCESS] Reguła '{rule_name}' została zapisana na dysku pod ID: {new_rule.id}")
            except Exception as e:
                print(f"[SYSTEM ERROR] Nie udało się zapisać nowej reguły: {e}")


    def delete_rule_handler(self):
        selected_row = self.rules_dialog.rules_list.currentRow()
        
        if selected_row >= 0:

            self.reset_schedule_flags()
            # delete rule from memory
            del self.current_entity.rules[selected_row]
            # refresh ui UI
            self.refresh_rules_table()

    def new_shift(self, sender):
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "new_datetime_shift.ui")
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.shift_dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        # filling combobox with places
        place_names = [place.name for place in self.place_list]
        self.shift_dialog.selected_place.addItems(place_names)

        now = datetime.now()
        # Tworzymy obiekt QDateTime z dzisiejszą datą i aktualną godziną z widgetu
        current_begin = self.shift_dialog.begin_datetime.dateTime()
        current_begin.setDate(now.date()) 
        
        self.shift_dialog.begin_datetime.setDateTime(current_begin)
        self.shift_dialog.end_datetime.setDateTime(current_begin) # End też startuje z dzisiejszą datą

        self.shift_dialog.begin_datetime.dateTimeChanged.connect(self.sync_shift_dates)

        # show window
        wynik = self.shift_dialog.exec() 

        if wynik == 1: # ok button is clicked
           
            begin_qt = self.shift_dialog.begin_datetime.dateTime() 
            end_qt = self.shift_dialog.end_datetime.dateTime()
            
            # Konwertujemy na natywny datetime Pythona
            begin_dt = begin_qt.toPython() 
            end_dt = end_qt.toPython()
            
            place_name = self.shift_dialog.selected_place.currentText()
            
            actual_place_object = next((p for p in self.place_list if p.name == place_name), None)
            
            if actual_place_object is None:
                print(f"[SYSTEM WARNING] Nie znaleziono obiektu Place dla nazwy: {place_name}. Tworzę zastępczy.")
                actual_place_object = Place(place_name, "")
            
            # 4. Tworzymy obiekt ShiftPlace przekazując żywy OBIEKT klasy Place, a nie string!
            shift = ShiftPlace(begin_dt, end_dt, actual_place_object, sender)

            return shift

        self.shift_dialog.deleteLater()
        return None


    def sync_shift_dates(self, new_datetime):
        """
        Automatycznie ustawia datę w end_time na taką samą, 
        jaka została wybrana w begin_time, zachowując godzinę w end_time.
        """
        # Pobieramy aktualny stan end_time
        end_dt = self.shift_dialog.end_datetime.dateTime()
        
        # Podmieniamy tylko datę na tę z new_datetime (begin_time)
        end_dt.setDate(new_datetime.date())
        
        # Blokujemy sygnały na chwilę, aby uniknąć pętli, jeśli end_time też coś wyzwala
        self.shift_dialog.end_datetime.blockSignals(True)
        self.shift_dialog.end_datetime.setDateTime(end_dt)
        self.shift_dialog.end_datetime.blockSignals(False)

#functions that return widget for selected rule

    def create_empty_ui(self):
        """Empty form for rule without parameters"""
        page = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Additional parameters don't required")
        layout.addWidget(label)
        page.setLayout(layout)
        return page

    def create_cyclic_ui(self):
        """Form for cyclic rule"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # Pole do wpisywania interwału
        form_layout = QFormLayout()
        spin_box = QSpinBox()
        spin_box.setMinimum(1)
        spin_box.setObjectName("interval_input") 
        form_layout.addRow("Interval (days):", spin_box)
        layout.addLayout(form_layout)

        # Przycisk i etykieta dla zmiany (Shift)
        shift_layout = QHBoxLayout()
        btn_set_shift = QPushButton("Set Begin Shift")
        lbl_shift_info = QLabel("No shift selected")
        
        # Zmienna wewnątrz obiektu strony, by przechować wybraną zmianę
        page.selected_begin_shift = None

        # Funkcja wewnętrzna wywoływana po kliknięciu "Set Begin Shift"
        def handle_set_shift():
            shift = self.new_shift(self.current_entity)
            if shift:
                page.selected_begin_shift = shift # Zapisujemy zmianę w obiekcie strony
                
                # Aktualizujemy tekst etykiety
                początek = shift.begin.strftime('%Y-%m-%d %H:%M')
                miejsce = getattr(shift.place, 'name', shift.place)
                lbl_shift_info.setText(f"Selected: {początek} at {miejsce}")

        btn_set_shift.clicked.connect(handle_set_shift)

        shift_layout.addWidget(btn_set_shift)
        shift_layout.addWidget(lbl_shift_info)
        layout.addLayout(shift_layout)

        page.setLayout(layout)
        return page

    def create_between_shifts_ui(self):
        """Form for 'Between Shifts' rule"""
        page = QWidget()
        layout = QFormLayout()
        
        spin_box = QSpinBox()
        spin_box.setMinimum(1)
        spin_box.setMaximum(48)
        spin_box.setValue(11) # default eleven hours sleep
        spin_box.setObjectName("rest_hours_input") 
        
        layout.addRow("Minimum rest (hours):", spin_box)
        page.setLayout(layout)
        return page
    
    def handle_add_unordered_shift(self):
        #window with adding shift
        new_shift_obj = self.new_shift(self.current_entity)
        
        if new_shift_obj:
            # currently opened shift list
            current_page = self.rules_dialog.rule_form.currentWidget()
            shift_list = current_page.findChild(QListWidget, "unordered_shift_list")
            
            if shift_list:
               
                początek = new_shift_obj.begin.strftime('%Y-%m-%d %H:%M')
                koniec = new_shift_obj.end.strftime('%H:%M')
                miejsce = new_shift_obj.place
                
                display_text = f"Shift: {początek} - {koniec} at {miejsce}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, new_shift_obj) 
                shift_list.addItem(item)
    
    def create_unordered_ui(self):
        """Form for unordered rule"""
        page = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("Shifts you want to work this month:")
        layout.addWidget(label)

        # list with added shifts
        shift_list = QListWidget()
        shift_list.setObjectName("unordered_shift_list") # usefull for looking
        layout.addWidget(shift_list)

        
        btn_add_shift = QPushButton("Add Shift to list")
        
        btn_add_shift.clicked.connect(self.handle_add_unordered_shift)
        layout.addWidget(btn_add_shift)

        page.setLayout(layout)
        return page

#entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.ui.show() 

    sys.exit(app.exec())