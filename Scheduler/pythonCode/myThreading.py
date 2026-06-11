from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QHeaderView, QMainWindow, QPushButton, QTableWidgetItem, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
#for creating rule form
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTableWidgetItem, 
                               QWidget, QVBoxLayout, QFormLayout, QLabel, QSpinBox, 
                               QListWidget, QListWidgetItem, QHBoxLayout, QComboBox, 
                               QDialog, QDialogButtonBox, QLineEdit)
from PySide6.QtCore import Qt

#regular expression - input veryfication
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QCloseEvent
from PySide6.QtGui import QMovie

import os

class SchedulingWorker(QThread):
    """Wątek robotnika, który wykonuje ciężkie obliczenia w tle."""
    finished_signal = Signal(int)  # Przekazuje wynik (1 lub -1) po zakończeniu

    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler

    def run(self):
        # praca w osobnym watku
        result = self.scheduler.createPlan()
        self.finished_signal.emit(result)


class LoadingDialog(QDialog):
    """Modalne okno ładowania z animacją kręcącego się kółka."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Usuwamy standardowy pasek tytułu i przyciski zamknij/minimalizuj
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(True) # Blokuje klikanie w okno główne pod spodem
        self.setWindowTitle("Generowanie grafiku...")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        #
        self.label_text = QLabel("Trwa generowanie grafiku zaawansowanym\nalgorytmem genetycznym. Proszę czekać...")
        self.label_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_text)
        
        layout.addSpacing(10)
        
        #NIE DZIALA
        # Etykieta na animację GIF
        self.label_gif = QLabel()
        self.label_gif.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_gif)
        
        # Ładowanie pliku GIF 
        gif_path = os.path.join(os.path.dirname(__file__), "/gifs/spinner.gif")
        self.movie = QMovie(gif_path)
        self.label_gif.setMovie(self.movie)
        
        self.setLayout(layout)

    def showEvent(self, event):
        """Uruchamia animację w momencie pokazania się okna."""
        super().showEvent(event)
        self.movie.start()

    def closeEvent(self, event):
        """Zatrzymuje animację przy zamykaniu."""
        self.movie.stop()
        super().closeEvent(event)