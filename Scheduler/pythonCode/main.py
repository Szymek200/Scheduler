import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
#for creating rule form
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QSpinBox, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

#regular expression - input veryfication
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

#first filename than class name
from worker import Worker
from place import Place
from shift import ShiftPlace

import rules

class MainWindow(QMainWindow):


  

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

        #rules typoe dictionary
        self.worker_rules_registry = {
            "Free Weekend": self.create_empty_ui,
            "Between Shifts": self.create_between_shifts_ui, # Jeśli nie ma parametrów, dajemy empty
            "Unordered Rule": self.create_unordered_ui
        }

        self.place_rules_registry = {
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
            
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        #activating button
        self.ui.add_worker.clicked.connect(self.add_worker)
        self.ui.add_workplace.clicked.connect(self.add_workplace)
        self.ui.view_worker.clicked.connect(self.view_worker)
        self.ui.view_workplace.clicked.connect(self.view_workplace)

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

        # Zabezpieczenie przed pustym polem
        etat_text = self.dialog.etat_line.text()
        etat = int(etat_text) if etat_text else 0

        # 4. Wyświetlenie jako okno modalne
        # .exec() zatrzymuje kod w tym miejscu, aż zamkniesz okno
        wynik = self.dialog.exec() 

      
      

        if wynik == 1: # Jeśli użytkownik kliknął OK (standard w QDialog)
           name = self.dialog.name_line.text()
           surname = self.dialog.surname_line.text()
           pesel = self.dialog.pesel_line.text()
           etat = int(self.dialog.etat_line.text())
           worker = Worker(name, surname, pesel, etat)

           self.workers_list.append(worker)
          
           

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
        
        
        self.dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        self.dialog.return_to_main.clicked.connect(self.return_to_main)
        

        for i in range(len(self.place_list)):
            #create new row
            self.dialog.workplace_list.insertRow(i)


    
            #adding content to columnsclea
            self.dialog.workplace_list.setItem(i, 0, QTableWidgetItem(self.place_list[i].name))
            self.dialog.workplace_list.setItem(i, 1, QTableWidgetItem(self.place_list[i].address))
           

            #adding button to last column

            
            btn_rules = QPushButton("Rules")
            
            # Łączymy kliknięcie z funkcją otwierającą okno
            # Używamy lambda, aby przekazać dane o tym konkretnym pracowniku
            #idx is needed so lamba will remember its index
            #checked = False because when button is clicked it is returned as first value
            btn_rules.clicked.connect(lambda checked = False, obj=self.place_list[i]: self.manage_rules(obj))
            
            # Wstawiamy przycisk do tabeli
            self.ui.workplace_list.setCellWidget(i, 3, btn_rules)

        self.dialog.show() 

    def view_worker(self):

        self.ui.main_menu_container.hide()
     
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "workers_list.ui")
       
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        
        
        self.dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        self.dialog.return_to_main.clicked.connect(self.return_to_main)

        for i in range(len(self.workers_list)):
            #create new row
            self.dialog.workers_list.insertRow(i)


    
            #adding content to columns
            self.dialog.workers_list.setItem(i, 0, QTableWidgetItem(self.workers_list[i].name))
            self.dialog.workers_list.setItem(i, 1, QTableWidgetItem(self.workers_list[i].surname))
            self.dialog.workers_list.setItem(i, 2, QTableWidgetItem(self.workers_list[i].pesel))

            #adding button to last column

            
            btn_rules = QPushButton("Rules")
            
            # Łączymy kliknięcie z funkcją otwierającą okno
            # Używamy lambda, aby przekazać dane o tym konkretnym pracowniku
            #idx is needed so lamba will remember its index
            #checked = False because when button is clicked it is returned as first value
            btn_rules.clicked.connect(lambda checked = False, obj=self.workers_list[i]: self.manage_rules(obj))
            
            # Wstawiamy przycisk do tabeli
            self.dialog.workers_list.setCellWidget(i, 3, btn_rules)


       

         # 4. Wyświetlenie jako okno modalne
        # .exec() zatrzymuje kod w tym miejscu, aż zamkniesz okno
        self.dialog.show() 

    def return_to_main(self):


    
        self.dialog.close()

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
        self.dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        #cleaning widget
        while self.dialog.rule_form.count() > 0:
            widget = self.dialog.rule_form.widget(0)
            self.dialog.rule_form.removeWidget(widget)
            widget.deleteLater()

        self.dialog.combo_rule_type.clear()

        # choosing worker or workplace register
        if isinstance(self.current_entity, Worker):
            registry = self.worker_rules_registry
        else:
            registry = self.place_rules_registry

        # building pages 
        for rule_name, ui_builder in registry.items():
            #name in combo box
            self.dialog.combo_rule_type.addItem(rule_name)
            
            
            page_widget = ui_builder()
            self.dialog.rule_form.addWidget(page_widget)

        self.dialog.combo_rule_type.currentIndexChanged.connect(self.dialog.rule_form.setCurrentIndex)

        self.dialog.return_view.clicked.connect(self.dialog.close)
        self.dialog.add_rule.clicked.connect(self.add_rule_handler)
        self.dialog.delete_rule.clicked.connect(self.delete_rule_handler)

        self.refresh_rules_table()
        self.dialog.exec()


    #show all rules in rule window
    def refresh_rules_table(self):
        self.dialog.rules_list.setRowCount(0)
        
        for i, rule in enumerate(self.current_entity.rules):
            self.dialog.rules_list.insertRow(i)
           
           #if rule does not have name attribute
            nazwa = getattr(rule, 'name', 'Brak nazwy')
            
            self.dialog.rules_list.setItem(i, 0, QTableWidgetItem(nazwa))
            self.dialog.rules_list.setItem(i, 1, QTableWidgetItem(rule.type_name))


    def add_rule_handler(self):
        rule_type = self.dialog.combo_rule_type.currentText()
        rule_name = self.dialog.rule_name.text()
        
        # currectly chosen page number
        current_page = self.dialog.rule_form.currentWidget()
        
        new_rule = None

        if rule_type == "Free Weekend":
            new_rule = rules.FreeWeekend(self.current_entity, rule_name)
            
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
            if interval_widget:
                interval = interval_widget.value()
                # creating cyclic rule
                begin_shift = self.new_shift(self.current_entity)
                if begin_shift:
                    new_rule = rules.CyclicRule(begin_shift, interval, rule_name)

        if new_rule:
            self.current_entity.rules.append(new_rule)
            self.refresh_rules_table()
            self.dialog.rule_name.clear()


    def delete_rule_handler(self):
        selected_row = self.dialog.rules_list.currentRow()
        
        if selected_row >= 0:
            # delete rule from memory
            del self.current_entity.rules[selected_row]
            # refresh ui UI
            self.refresh_rules_table()

    def new_shift(self, sender):
        ui_path = os.path.join(os.path.dirname(__file__), "GUI", "new_shift.ui")
       
        loader = QUiLoader()
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        
        
        self.shift_dialog = loader.load(ui_file, self.ui)
        ui_file.close()

        validator = QRegularExpressionValidator(self.hours_regex, self)
        #adding to particular ui object
        self.shift_dialog.begin_time.setValidator(validator)

        self.shift_dialog.end_time.setValidator(validator)

        place_names =[]
        for place in self.place_list:
            place_names.append(place.name)

         # filling combo box
        self.shift_dialog.selected_place.addItems(place_names)

        # Zabezpieczenie przed pustym polem
        etat_text = self.shift_dialog.etat_line.text()
        etat = int(etat_text) if etat_text else 0

        # 4. Wyświetlenie jako okno modalne
        # .exec() zatrzymuje kod w tym miejscu, aż zamkniesz okno
        wynik = self.shift_dialog.exec() 

        if wynik == 1: # Jeśli użytkownik kliknął OK (standard w QDialog)
           begin = self.shift_dialog.begin_time.text()
           end = self.shift_dialog.end_time.text()
           place = self.shift_dialog.selected_place.current_text()
           
           shift = ShiftPlace(begin, end, place, sender)

           return shift


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
        layout = QFormLayout()
        
        spin_box = QSpinBox()
        spin_box.setMinimum(1)
        # BARDZO WAŻNE: Nadajemy objectName, żeby potem łatwo wyciągnąć z niego dane!
        spin_box.setObjectName("interval_input") 
        
        layout.addRow("Interval (days):", spin_box)
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
            current_page = self.dialog.rule_form.currentWidget()
            shift_list = current_page.findChild(QListWidget, "unordered_shift_list")
            
            if shift_list:
                # text for user
                display_text = f"Shift: {new_shift_obj.begin} - {new_shift_obj.end} at {new_shift_obj.places}"
                
                
                item = QListWidgetItem(display_text)
                
                # we save shiftPlace object
                item.setData(Qt.UserRole, new_shift_obj) 
                
                # add to the view
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