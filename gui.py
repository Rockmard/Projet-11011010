import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QLineEdit
)
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtCore import Qt, QPoint, QEvent
from request import RiotWorker, get_players_in_league, get_player_by_puuid, get_player_by_riotid
from constants import MAIN_BACKGROUND_PATH

class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.mouse_pos = QPoint(self.width() // 2, self.height() // 2)
        self.background = QPixmap(MAIN_BACKGROUND_PATH)

    def update_mouse_pos(self, pos):
        self.mouse_pos = pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.mouse_pos.isNull():
            self.mouse_pos = QPoint(self.width() // 2, self.height() // 2)

        # DEBUG:
        # print(f"Painting at mouse_pos={self.mouse_pos}")

        dx = (self.mouse_pos.x() - self.width() // 2) // 10  # smaller divisor for stronger movement
        dy = (self.mouse_pos.y() - self.height() // 2) // 10

        scale_factor = 1.2
        scaled_width = int(self.width() * scale_factor)
        scaled_height = int(self.height() * scale_factor)

        scaled_bg = self.background.scaled(
            scaled_width, scaled_height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        x = (self.width() - scaled_bg.width()) // 2 - dx
        y = (self.height() - scaled_bg.height()) // 2 - dy

        painter.drawPixmap(x, y, scaled_bg)

class MainWindow(QWidget):
    api_key = ""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("League Auto Scout App v1.2")
        self.setFixedSize(500, 400)
        self.setMouseTracking(True)

        # LAYOUT
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

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

        # CONNECTING THE BUTTONS TO THE RIGHT API CALL
        self.api_key_button.clicked.connect(self.validate_api_key)
        self.get_lists_button.clicked.connect(self.fill_lists)
        self.get_player_info_button.clicked.connect(self.get_player_info)

        # BACKGROUND WIDGET
        self.background_widget = BackgroundWidget(self)
        self.background_widget.setGeometry(0, 0, self.width(), self.height())
        self.background_widget.show()
        self.background_widget.lower()

        # PUTTING MOUSE TRACKING ON EVERY WIDGETS
        for widget in [self.api_key_field, self.api_key_button, self.label,
                    self.get_lists_button, self.text_field, self.get_player_info_button]:
            widget.setMouseTracking(True)
            widget.installEventFilter(self)
        
        # STYLESHEET
        self.setStyleSheet("""                      
            QWidget {
                background-color: transparent;
                color: white;
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

    # MOUSE TRACKING 
    def mouseMoveEvent(self, event):
        pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
        # Map the position relative to background widget:
        pos = self.background_widget.mapFrom(self, pos)
        self.background_widget.update_mouse_pos(pos)
        super().mouseMoveEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            # Map position properly
            pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            global_pos = obj.mapToGlobal(pos)
            bg_pos = self.background_widget.mapFromGlobal(global_pos)
            self.background_widget.update_mouse_pos(bg_pos)
        return super().eventFilter(obj, event)

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