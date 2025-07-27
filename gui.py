from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton
)
from PySide6.QtGui import QFont
from request import RiotWorker, get_players_in_league
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("League Auto Scout App v1.1")
        self.setFixedSize(500, 400)

        self.main_layout = QVBoxLayout()
        self.get_lists_button = QPushButton("Call Riot API")
        self.label = QLabel("Waiting...")
        self.label.setFont(QFont("Arial", 12))

        self.main_layout.addWidget(self.get_lists_button)
        self.main_layout.addWidget(self.label)
        self.setLayout(self.main_layout)

        self.get_lists_button.clicked.connect(self.fill_lists)

        # Apply custom style
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005F99;
            }
            QLabel {
                padding: 4px;
            }
        """)

    def fill_lists(self):
        self.label.setText("Calling API...")
        self.get_lists_button.setEnabled(False)

        self.worker = RiotWorker(get_players_in_league)
        self.worker.finished.connect(self.handle_result)
        self.worker.start()

    def handle_result(self, message: str):
        self.label.setText(message)
        self.get_lists_button.setEnabled(True)

def init_gui() :
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())