from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QLineEdit
)
from PySide6.QtGui import QFont
from request import RiotWorker, get_players_in_league, get_player_by_puuid
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("League Auto Scout App v1.1")

        self.setFixedSize(500, 400)

        self.main_layout = QVBoxLayout()

        self.get_lists_button = QPushButton("Call Riot API")
        self.get_player_info_button = QPushButton("Get Player Info")

        self.label = QLabel("Waiting...")
        self.label.setFont(QFont("Arial", 12))

        self.text_field = QLineEdit()
        self.text_field.setPlaceholderText("Default Text")
        self.text_field.setProperty("class", "puuid_field")

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.get_lists_button)
        self.main_layout.addWidget(self.text_field)
        self.main_layout.addWidget(self.get_player_info_button)
        self.setLayout(self.main_layout)

        self.get_lists_button.clicked.connect(self.fill_lists)
        self.get_player_info_button.clicked.connect(self.get_player_info)
        # Apply custom style
        self.setStyleSheet("""                      
            QWidget {
                background-color: black;
            }

            QPushButton {
                background-color: #3d3d3d;
                padding: 15px;
            }        
                               
            QPushButton:hover {
                background-color: grey;
            }
        """)

    def fill_lists(self):
        self.label.setText("Calling API...")
        self.get_lists_button.setEnabled(False)

        self.worker = RiotWorker(get_players_in_league)
        self.worker.finished.connect(self.handle_result)
        self.worker.start()

    def get_player_info(self):
        puuid = self.text_field.text()
        if (puuid == "") :
            self.text_field.setStyleSheet("border : 1px solid red; padding-top: 1px; padding-bottom: 1px; border-radius: 3px")
        else :
            self.text_field.setStyleSheet("border : 1px solid black; padding-top: 2px; padding-bottom: 2px; border-radius: 2px")
            self.get_player_info_button.setEnabled(False)
            self.worker = RiotWorker(get_player_by_puuid, puuid)
            self.worker.finished.connect(self.handle_result2)
            self.worker.start()

    def handle_result(self, message: str):
        self.label.setText(message)
        self.get_lists_button.setEnabled(True)

    def handle_result2(self, message: str):
        print(message)
        self.get_player_info_button.setEnabled(True)

def init_gui() :
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())