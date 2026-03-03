import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget, QVBoxLayout

#Qwindget - container
#konkretny uklad
#QVBoxLayout - vertical box

#styling
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        container = QWidget()

        self.setCentralWidget(container)

        layout = QVBoxLayout(container)

        label = QLabel("Hello grafika")
        label2 = QLabel("Hello grafika")
        label3 = QLabel("Hello grafika")
        
        layout.addWidget(label)

        layout.addWidget(label2)
        layout.addWidget(label3)

        button = QPushButton("przycisk")
        #argument is a function to react on button pushed
        button.clicked.connect(lambda: print("button pressed"))
        
        layout.addWidget(button)





app = QApplication()

window = MainWindow()

window.show()

# Uruchamiamy pętlę zdarzeń
sys.exit(app.exec())