import sys
import os
from PySide6.QtWidgets import QApplication, QHeaderView, QMainWindow, QPushButton, QTableWidgetItem, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
#for creating rule form
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTableWidgetItem, 
                               QWidget, QVBoxLayout, QFormLayout, QLabel, QSpinBox, 
                               QListWidget, QListWidgetItem, QHBoxLayout, QComboBox, 
                               QDialog, QDialogButtonBox)
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
from scheduler import Scheduler

from drawSchedule import MainWindow as ScheduleWindow
from datetime import datetime, time, timedelta
import rules

from saving import Saving
import sys
import traceback

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

        setup_saver = Saving(self.workers_list, self.place_list, "MojeDane")
    
        self.workers_list, self.place_list = setup_saver.reading() 

        
        self.saving = Saving(self.workers_list, self.place_list, "MojeDane")
       

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


        #our own method for closing window
        self.ui.closeEvent = self.closeEvent
       

        #activating button
        self.ui.add_worker.clicked.connect(self.add_worker)
        self.ui.add_workplace.clicked.connect(self.add_workplace)
        self.ui.view_worker.clicked.connect(self.view_worker)
        self.ui.view_workplace.clicked.connect(self.view_workplace)

        self.ui.workplace_availability.clicked.connect(self.view_workplace_aval)

        self.ui.create_schedule.clicked.connect(self.create_schedule)

        self.ui.worker_schedule.clicked.connect(self.worker_schedule)

        self.scheduler = Scheduler(self.workers_list, self.place_list)

        self.ui.worker_availability.clicked.connect(self.open_schedule_view)

    def closeEvent(self, event: QCloseEvent):
        # This triggers right before the window closes
       
        
        saver = Saving(self.workers_list, self.place_list, "MojeDane")
        saver.saving()
        
        event.accept() #allow to close the window

    def view_workplace_aval(self):
        self.schedule_window = ScheduleWindow(self.workers_list, self.place_list,self.scheduler,'place', self.ui)
  
        self.ui.hide()

        self.schedule_window.ui.show()

    def create_schedule(self):
        dialog = QDialog(self.ui)
        dialog.setWindowTitle("Select Schedule Period")
        layout = QFormLayout(dialog)

        # 2. Tworzymy pole wyboru roku (QSpinBox)
        year_spin = QSpinBox()
        year_spin.setRange(2024, 2050) # Zakres lat
        year_spin.setValue(datetime.today().year) # Domyślnie obecny rok

        # 3. Tworzymy listę rozwijaną dla miesiąca (QComboBox)
        month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        month_combo.addItems(months)
        month_combo.setCurrentIndex(datetime.today().month - 1) # Domyślnie obecny miesiąc

        # Dodajemy elementy do okna
        layout.addRow("Year:", year_spin)
        layout.addRow("Month:", month_combo)

        # 4. Przyciski OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # 5. Wyświetlamy okno i czekamy na reakcję
        if dialog.exec() == QDialog.Accepted:
            selected_year = year_spin.value()
            selected_month = month_combo.currentIndex() + 1
            
            # Resetujemy flagę gotowości przed nowym generowaniem
            self.scheduler.ready = 0
            
            # Uruchamiamy algorytm dla wybranego miesiąca
            result = self.scheduler.createPlan(selected_month, selected_year)
            
            if result == -1:
                #self.ui.info_label.setText("Failed to create schedule (Check availability).")
                QMessageBox.information(None, "Failed to create schedule", "Check availability).")
            else:
                #self.ui.info_label.setText(f"Schedule created for {months[selected_month-1]} {selected_year}")
                QMessageBox.information(None, "Success", f"Schedule created for {months[selected_month-1]} {selected_year}")

    def worker_schedule(self):
        self.schedule_window = ScheduleWindow(self.workers_list, self.place_list,self.scheduler,'worker', self.ui)
  
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


        # 4. Wyświetlenie jako okno modalne
        # .exec() zatrzymuje kod w tym miejscu, aż zamkniesz okno
        wynik = self.dialog.exec() 

        if wynik == 1: # Jeśli użytkownik kliknął OK (standard w QDialog)
           name = self.dialog.name_line.text()
           surname = self.dialog.surname_line.text()
           pesel = self.dialog.pesel_line.text()
 
           worker = Worker(name, surname, pesel)

           self.workers_list.append(worker)
          
    def open_schedule_view(self):

        #create new window and class
        self.schedule_window = ScheduleWindow(self.workers_list, self.place_list,self.scheduler,'request_worker', self.ui)
  
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
            
        # Opcjonalnie: Rozszerzenie kolumn, żeby ładnie wyglądały
        self.rules_dialog.rules_list.horizontalHeader().setStretchLastSection(True)


    def add_rule_handler(self):
        rule_type = self.rules_dialog.combo_rule_type.currentText()
        rule_name = self.rules_dialog.rule_name.text()
        
        # currectly chosen page number
        current_page = self.rules_dialog.rule_form.currentWidget()
        
        new_rule = None

        if rule_type == "Free Weekend":
            new_rule = rules.FreeWeekend(self.current_entity, rule_name)

        elif rule_type == "Between Shifts":

            rest_widget = current_page.findChild(QSpinBox, "rest_hours_input")
            
            if rest_widget:
                # 2. Pobieramy wartość int (np. 11)
                hours_value = rest_widget.value()
                # 3. Konwertujemy na timedelta, bo tego oczekuje klasa BetweenShifts
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
                
                #creating rule
                new_rule = rules.UnorderedRule(shifts_array, rule_name)
            else:
                print("Błąd: Nie dodano żadnych zmian do reguły!")
                
        elif rule_type == "Cyclic Rule":
            
            interval_widget = current_page.findChild(QSpinBox, "interval_input")
            
            # Sprawdzamy, czy użytkownik ustawił "begin_shift" przyciskiem i zapisał to w obiekcie strony
            if interval_widget and hasattr(current_page, 'selected_begin_shift') and current_page.selected_begin_shift:
                interval = interval_widget.value()
                begin_shift = current_page.selected_begin_shift
                new_rule = rules.CyclicRule(begin_shift, timedelta(days=interval), rule_name)
            else:
                # Opcjonalnie: tutaj można dodać okienko z błędem dla użytkownika (QMessageBox)
                print("Błąd: Musisz najpierw ustawić zmianę początkową (Set Begin Shift)!")

        if new_rule:
            self.current_entity.rules.append(new_rule)
            self.refresh_rules_table()
            self.rules_dialog.rule_name.clear()


    def delete_rule_handler(self):
        selected_row = self.rules_dialog.rules_list.currentRow()
        
        if selected_row >= 0:
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

        # 2. Automatyczna zmiana daty w end_time przy zmianie w begin_time
        # Używamy sygnału dateTimeChanged
        self.shift_dialog.begin_datetime.dateTimeChanged.connect(self.sync_shift_dates)

        # show window
        wynik = self.shift_dialog.exec() 

        if wynik == 1: #ok ok button is clicked
            # 1. Pobieramy obiekty QDateTime z widgetów
            begin_qt = self.shift_dialog.begin_datetime.dateTime() 
            end_qt = self.shift_dialog.end_datetime.dateTime()
            
            # 2. Konwertujemy na natywny datetime Pythona
            begin_dt = begin_qt.toPython() 
            end_dt = end_qt.toPython()
            
            # 3. Pobieramy wybrane miejsce
            place_name = self.shift_dialog.selected_place.currentText()
            
            # 4. Tworzymy obiekt ShiftPlace (pamiętaj, że ShiftPlace przyjmuje set miejsc)
            shift = ShiftPlace(begin_dt, end_dt, place_name, sender)

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
        
        # 1. Pole do wpisywania interwału
        form_layout = QFormLayout()
        spin_box = QSpinBox()
        spin_box.setMinimum(1)
        spin_box.setObjectName("interval_input") 
        form_layout.addRow("Interval (days):", spin_box)
        layout.addLayout(form_layout)

        # 2. Przycisk i etykieta dla zmiany (Shift)
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


    # saving when command Q
    app.aboutToQuit.connect(window.saving.saving) 

    window.ui.show()

    sys.exit(app.exec())