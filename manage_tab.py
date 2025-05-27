from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QTextEdit, QTabWidget, QListWidget, QHBoxLayout, 
    QPushButton, QSizePolicy, QLineEdit, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class ManageTab(QWidget):
    def __init__(self, parent=None, data_dirs=None): # Add data_dirs parameter
        super().__init__(parent)
        self.data_dirs = data_dirs if data_dirs is not None else {} # Store data_dirs
        self.songbook = [] # Songbook data will be managed here

        self.manage_layout = QVBoxLayout(self)

        self.songbook_list_widget = QListWidget()
        self.manage_layout.addWidget(self.songbook_list_widget)
        # self.songbook_list_widget.currentRowChanged.connect(self._populate_edit_fields) # Connect selection change

        edit_layout = QHBoxLayout()
        self.edit_title_input = QLineEdit()
        self.edit_title_input.setPlaceholderText("Edit Song Title")
        self.edit_pdf_input = QLineEdit()
        self.edit_pdf_input.setPlaceholderText("Edit PDF Filename")
        self.edit_desc_input = QLineEdit()
        self.edit_desc_input.setPlaceholderText("Edit Description Filename (optional)")
        self.save_edit_button = QPushButton("Save Changes")
        # self.save_edit_button.clicked.connect(self._save_edited_song)
        edit_layout.addWidget(self.edit_title_input)
        edit_layout.addWidget(self.edit_pdf_input)
        edit_layout.addWidget(self.edit_desc_input)
        edit_layout.addWidget(self.save_edit_button)
        self.manage_layout.addLayout(edit_layout)

        add_layout = QHBoxLayout()
        self.add_title_input = QLineEdit()
        self.add_title_input.setPlaceholderText("Song Title")
        self.add_pdf_input = QLineEdit()
        self.add_pdf_input.setPlaceholderText("PDF Filename")
        self.add_desc_input = QLineEdit()
        self.add_desc_input.setPlaceholderText("Description Filename (optional)")
        self.add_button = QPushButton("Add Song")
        # self.add_button.clicked.connect(self._add_song_to_songbook)
        add_layout.addWidget(self.add_title_input)
        add_layout.addWidget(self.add_pdf_input)
        add_layout.addWidget(self.add_desc_input)
        add_layout.addWidget(self.add_button)
        self.manage_layout.addLayout(add_layout)

        button_layout = QHBoxLayout()
        self.remove_button = QPushButton("Remove Song")
        #self.remove_button.clicked.connect(self._remove_selected_song)
        self.move_up_button = QPushButton("Move Up")
        #self.move_up_button.clicked.connect(self._move_song_up)
        self.move_down_button = QPushButton("Move Down")
        #self.move_down_button.clicked.connect(self._move_song_down)
        self.load_button = QPushButton("Load Songbook")
        #self.load_button.clicked.connect(self._load_songbook_from_file)
        self.save_button = QPushButton("Save Songbook")
        #self.save_button.clicked.connect(self._save_songbook_to_file)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.move_up_button)
        button_layout.addWidget(self.move_down_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        self.manage_layout.addLayout(button_layout)

        # self._populate_songbook_list()

    def _populate_edit_fields(self, song):
        selected_song = song
        self.edit_title_input.setText(selected_song.title)
        self.edit_pdf_input.setText(selected_song.pdf_filename)
        self.edit_desc_input.setText(selected_song.description_filename)

    def _clear_add_fields(self):
        self.add_title_input.clear()
        self.add_pdf_input.clear()
        self.add_desc_input.clear()
    
    