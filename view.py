from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QTextEdit, QTabWidget, QListWidget, QHBoxLayout, 
    QPushButton, QSizePolicy, QLineEdit, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class PDFViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MusicViewer - Perform Songbook")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        # ... (set up tabs, layouts, widgets as in your current code)
        # All UI elements should be attributes here, but NO business logic!
    #def __init__(self):
       # super().__init__()
        #self.setWindowTitle("MusicViewer - Perform Songbook")
        self.songbook = []  # Initialize as empty
        self.current_song_index = 0
        self.pdf_document = None
        self.current_page_index_within_song = -2  # Start with overview
        self.description_text_content = ""
        

        #self.central_widget = QWidget()
        #self.setCentralWidget(self.central_widget)
        self.central_widget.setFocusPolicy(Qt.StrongFocus)
        #self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.perform_tab = QWidget()
        self.manage_tab = QWidget()
        self.tabs.addTab(self.perform_tab, "Perform")
        self.tabs.addTab(self.manage_tab, "Manage Songbook")
        self.main_layout.addWidget(self.tabs)

        self.statusbar = self.statusBar()
        #self.statusbar.showMessage("Ready", 5000)
        
        self._setup_perform_tab()
        self._setup_manage_tab()

        self.setMinimumSize(600, 800)

        #self.tabs.currentChanged.connect(self._prompt_save_on_tab_change) # Connect tab change signal

        # self._load_songbook_from_file() # Load songbook from file
        # self.show()
        # QTimer.singleShot(100, self._show_songbook_overview) # Show initial overview

    def set_controller(self, controller):
        self.controller = controller
   
    def _setup_perform_tab(self):
        self.perform_layout = QVBoxLayout(self.perform_tab)

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

        # We no longer add a QLabel for the status bar here
        # self.statusbar = QLabel("Ready")
        # self.statusbar.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        # self.perform_layout.addWidget(self.statusbar)

        # self._load_current_song()
        # QTimer.singleShot(100, self._show_content)
        # self._update_status_bar()

    def _setup_manage_tab(self):
        self.manage_layout = QVBoxLayout(self.manage_tab)

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

    def _update_status_bar(self):
        total_songs = self.songbook.size()
        current_song = self.songbook.songs[self.current_song_index] if self.songbook else {"title": "No Songs"}
        current_song_title = current_song.get("title", "No Title")
        current_pdf_pages = len(self.pdf_document) if self.pdf_document else 0
        current_display_page = self.current_page_index_within_song + 1 if self.current_page_index_within_song != -1 else "Desc"

        status_text = f"Song: {self.current_song_index + 1}/{total_songs} ({current_song_title}) | Page: {current_display_page}/{current_pdf_pages}"
        self.window.statusbar.showMessage(status_text, 0)  # Use showMessage with a timeout of 0 (persistent)

    def _populate_edit_fields(self, song):
            selected_song = song
            self.edit_title_input.setText(selected_song.title)
            self.edit_pdf_input.setText(selected_song.pdf_filename)
            self.edit_desc_input.setText(selected_song.description_filename)

    def _clear_add_fields(self):
        self.add_title_input.clear()
        self.add_pdf_input.clear()
        self.add_desc_input.clear()
    

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.controller.handle_PageDown_event(event)
            
            # if self.current_page_index_within_song == -2: # From overview, go to first song's description
            #     self.current_song_index = 0
            #     self._load_current_song() # This will set current_page_index_within_song to -1
            #     self._show_content() # Show description
            # elif self.current_page_index_within_song == -1:
            #     self.current_page_index_within_song = 0
            #     self._show_content()
            #     if self.pdf_document and len(self.pdf_document) > 1:
            #         QTimer.singleShot(0, self._force_scale_page_two)
            # elif self.pdf_document and self.current_page_index_within_song < len(self.pdf_document) - 1:
            #     self.current_page_index_within_song += 1
            #     self._show_content()
            # else:
            #     self._next_song()
            #     return
        elif event.key() == Qt.Key_PageUp:
            self.controller.handle_PageUp_event(event)
        #     if self.current_page_index_within_song > 0:
        #         self.current_page_index_within_song -= 1
        #         self._show_content()
        #     elif self.current_page_index_within_song == 0:
        #         self.current_page_index_within_song = -1
        #         self._show_content()
        #     elif self.current_page_index_within_song == -1:
        #         if self.current_song_index > 0:
        #             self.current_song_index -= 1
        #             self._load_current_song() # Load previous song
        #             if self.pdf_document and len(self.pdf_document) > 1:
        #                 QTimer.singleShot(0, self._force_scale_last_page) # New: Force scale last page
        #             elif self.pdf_document:
        #                 self.current_page_index_within_song = len(self.pdf_document) - 1 # Go to last page
        #             else:
        #                 self.current_page_index_within_song = -1 # No PDF, show description
        #             self._show_content()
        #         else:
        #             self._show_songbook_overview()
        #     else:
        #         self._prev_song()
        #         return
        # elif event.key() == Qt.Key_Left:
        #     if self.current_page_index_within_song > 0:
        #         self.current_page_index_within_song -= 1
        #         self._show_content()
        # elif event.key() == Qt.Key_Right:
        #     if self.pdf_document and self.current_page_index_within_song < len(self.pdf_document) - 1:
        #         self.current_page_index_within_song += 1
        #         self._show_content()
        # self._update_status_bar()
        super().keyPressEvent(event)