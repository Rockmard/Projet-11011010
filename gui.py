from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QLineEdit
)
from PySide6.QtGui import QFont
from request import RiotWorker, get_players_in_league, get_player_by_puuid, get_player_by_riotid
import sys

class MainWindow(QWidget):
    api_key = ""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("League Auto Scout App v1.2")

        self.setFixedSize(500, 400)

        self.main_layout = QVBoxLayout()

        # BUTTONS
        self.get_lists_button = QPushButton("Fill the lists")
        self.get_player_info_button = QPushButton("Get Player Info")
        self.api_key_button = QPushButton("Register API KEY")

        # LABEL
        self.label = QLabel("Waiting...")
        self.label.setFont(QFont("Arial", 12))

        # TEXT FIELD
        self.api_key_field = QLineEdit()
        self.api_key_field.setPlaceholderText("API KEY")
        self.text_field = QLineEdit()
        self.text_field.setPlaceholderText("Example : GameName#TagLine / PUUID")
        #self.text_field.setProperty("class", "puuid_field")

        # ADDING EVERYTHING TO THE LAYOUT
        self.main_layout.addWidget(self.api_key_field)
        self.main_layout.addWidget(self.api_key_button)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.get_lists_button)
        self.main_layout.addWidget(self.text_field)
        self.main_layout.addWidget(self.get_player_info_button)
        self.setLayout(self.main_layout)

        # CONNECTING THE BUTTONS TO THE RIGHT API CALL
        self.api_key_button.clicked.connect(self.validate_api_key)
        self.get_lists_button.clicked.connect(self.fill_lists)
        self.get_player_info_button.clicked.connect(self.get_player_info)

        # STYLESHEET
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

    def validate_api_key(self):
        self.api_key = self.api_key_field.text()
        self.api_key_field.setText("")
        self.api_key_field.setPlaceholderText("Your key has been registered !")
        self.api_key_field.setStyleSheet("border : 1px solid grey; padding-top: 1px; padding-bottom: 1px; border-radius: 3px")

    # REQUESTS
    def fill_lists(self):
        self.label.setText("Calling API...")
        self.get_lists_button.setEnabled(False)

        self.list_worker = RiotWorker(get_players_in_league, self.api_key)
        self.list_worker.finished.connect(self.handle_result)
        self.list_worker.finished.connect(self.list_worker.deleteLater)
        self.list_worker.start()

    def get_player_info(self):
        account_key = self.text_field.text()
        if (account_key == "") :
            self.text_field.setStyleSheet("border : 1px solid red; padding-top: 1px; padding-bottom: 1px; border-radius: 3px")
        else :
            self.text_field.setStyleSheet("border : 1px solid grey; padding-top: 2px; padding-bottom: 2px; border-radius: 2px")
            self.get_player_info_button.setEnabled(False)
            if ('#' in account_key) :
                name, tag = account_key.split('#', 1)
                self.player_info_worker = RiotWorker(get_player_by_riotid, name, tag, self.api_key)
            else :
                self.player_info_worker = RiotWorker(get_player_by_puuid, account_key, self.api_key)
            self.player_info_worker.finished.connect(self.handle_result2)
            self.player_info_worker.finished.connect(self.player_info_worker.deleteLater)
            self.player_info_worker.start()

    # RESULT OF THREADS
    def handle_result(self, message: str):
        self.label.setText(message)
        self.get_lists_button.setEnabled(True)
        if ("401 : Unauthorized" in message) :
            self.api_key_field.setStyleSheet("border : 1px solid red; padding-top: 1px; padding-bottom: 1px; border-radius: 3px")

    def handle_result2(self, message: str):
        print(message)
        self.get_player_info_button.setEnabled(True)
        if ("401 : Unauthorized" in message) :
            self.api_key_field.setStyleSheet("border : 1px solid red; padding-top: 1px; padding-bottom: 1px; border-radius: 3px")

def init_gui() :
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())