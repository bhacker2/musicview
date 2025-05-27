from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QTextEdit, QTabWidget, QListWidget, QHBoxLayout, 
    QPushButton, QSizePolicy, QLineEdit, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from manage_tab import ManageTab
from perform_tab import PerformTab

class PDFViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MusicViewer - Perform Songbook")
        
        self.songbook = []  # Initialize as empty
        self.current_song_index = 0
        self.pdf_document = None
        self.current_page_index_within_song = -2  # Start with overview
        self.description_text_content = ""        
        
        # Define your configurable data directories here
        self.data_dirs = {
            "scores": "scores/",  # Example: relative path to a 'scores' folder
            "descriptions": "descriptions/", # Example: relative path to a 'descriptions' folder
            "songbooks": "songbooks/" # Default location for songbook files
        }
        # You might want to make these absolute paths or allow user configuration later
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.central_widget.setFocusPolicy(Qt.StrongFocus)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Pass data_dirs to the tab constructors
        self.perform_tab_widget = PerformTab(self, self.data_dirs)
        self.manage_tab_widget = ManageTab(self, self.data_dirs)

        self.tabs.addTab(self.perform_tab_widget, "Perform")
        self.tabs.addTab(self.manage_tab_widget, "Manage Songbook")


        self.statusbar = self.statusBar()
    
        self.setMinimumSize(600, 800)

    def set_controller(self, controller):
        self.controller = controller
   

    # def _update_status_bar(self):
    #     total_songs = self.songbook.size()
    #     current_song = self.songbook.songs[self.current_song_index] if self.songbook else {"title": "No Songs"}
    #     current_song_title = current_song.get("title", "No Title")
    #     current_pdf_pages = len(self.pdf_document) if self.pdf_document else 0
    #     current_display_page = self.current_page_index_within_song + 1 if self.current_page_index_within_song != -1 else "Desc"

    #     status_text = f"Song: {self.current_song_index + 1}/{total_songs} ({current_song_title}) | Page: {current_display_page}/{current_pdf_pages}"
    #     self.window.statusbar.showMessage(status_text, 0)  # Use showMessage with a timeout of 0 (persistent)
    

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.controller.handle_PageDown_event(event)
        elif event.key() == Qt.Key_PageUp:
            self.controller.handle_PageUp_event(event)
        super().keyPressEvent(event)