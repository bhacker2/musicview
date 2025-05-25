from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QTextEdit, QTabWidget, QListWidget, QHBoxLayout, 
    QPushButton, QSizePolicy, QLineEdit, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt



class PerformTab(QWidget):
    def __init__(self, parent=None, data_dirs=None): # Add data_dirs parameter
        super().__init__(parent)
        self.data_dirs = data_dirs if data_dirs is not None else {} # Store data_dirs
        
        self.perform_layout = QVBoxLayout(self)

        self.song_title_label = QLabel()
        self.song_title_label.setAlignment(Qt.AlignCenter)
        self.perform_layout.addWidget(self.song_title_label)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pdf_label.setMinimumSize(1, 1)
        self.content_layout.addWidget(self.pdf_label)
        self.description_display = QTextEdit()
        self.description_display.setReadOnly(True)
        font = self.description_display.font()
        font.setPointSize(14)  # Set the font size to 14 (you can adjust this value)
        self.description_display.setFont(font)
        self.content_layout.addWidget(self.description_display)
        self.perform_layout.addWidget(self.content_area, 1)

    def _show_songbook_overview(self, songbook):
        self.pdf_label.hide()
        self.description_display.show()
        overview_text = "Planned Performance:\n"
        for i, song in enumerate(songbook.songs):
            overview_text += f"{i + 1}. {song.title}\n"
        self.description_display.setText(overview_text)
        self.setWindowTitle("MusicViewer - Songbook Overview")
        self.song_title_label.setText("Songbook Overview")
        self.current_page_index_within_song = -2 # Ensure it's set to overview state

    def _clear_performance_view(self):
        self.song_title_label.clear()
        self.pdf_label.clear()
        self.description_display.clear()
        self.pdf_document = None
        self.current_page_index_within_song = -1