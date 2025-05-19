import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QTextEdit,
    QTabWidget,  # Import QTabWidget
    QListWidget,  # Import QListWidget for songbook management
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QStatusBar,  
    QFileDialog, 
    QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import json  # For saving and loading songbooks

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MusicViewer - Perform Songbook")
        self.songbook = []  # Initialize as empty
        self.current_song_index = 0
        self.pdf_document = None
        self.current_page_index_within_song = -2  # Start with overview
        self.description_text_content = ""
        self.songbook_modified = False  # Flag to track changes

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setFocusPolicy(Qt.StrongFocus)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.perform_tab = QWidget()
        self.manage_tab = QWidget()
        self.tabs.addTab(self.perform_tab, "Perform")
        self.tabs.addTab(self.manage_tab, "Manage Songbook")
        self.main_layout.addWidget(self.tabs)

        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready", 5000)
        
        self._setup_perform_tab()
        self._setup_manage_tab()

        self.tabs.currentChanged.connect(self._prompt_save_on_tab_change) # Connect tab change signal

        self._load_songbook_from_file() # Load songbook from file
        self.show()
        QTimer.singleShot(100, self._show_songbook_overview) # Show initial overview

    def _set_songbook_modified(self, modified=True):
        self.songbook_modified = modified

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

        self._load_current_song()
        QTimer.singleShot(100, self._show_content)
        self._update_status_bar()

    def _setup_manage_tab(self):
        self.manage_layout = QVBoxLayout(self.manage_tab)

        self.songbook_list_widget = QListWidget()
        self.manage_layout.addWidget(self.songbook_list_widget)
        self.songbook_list_widget.currentRowChanged.connect(self._populate_edit_fields) # Connect selection change

        edit_layout = QHBoxLayout()
        self.edit_title_input = QLineEdit()
        self.edit_title_input.setPlaceholderText("Edit Song Title")
        self.edit_pdf_input = QLineEdit()
        self.edit_pdf_input.setPlaceholderText("Edit PDF Filename")
        self.edit_desc_input = QLineEdit()
        self.edit_desc_input.setPlaceholderText("Edit Description Filename (optional)")
        self.save_edit_button = QPushButton("Save Changes")
        self.save_edit_button.clicked.connect(self._save_edited_song)
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
        self.add_button.clicked.connect(self._add_song_to_songbook)
        add_layout.addWidget(self.add_title_input)
        add_layout.addWidget(self.add_pdf_input)
        add_layout.addWidget(self.add_desc_input)
        add_layout.addWidget(self.add_button)
        self.manage_layout.addLayout(add_layout)

        button_layout = QHBoxLayout()
        self.remove_button = QPushButton("Remove Song")
        self.remove_button.clicked.connect(self._remove_selected_song)
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self._move_song_up)
        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self._move_song_down)
        self.load_button = QPushButton("Load Songbook")
        self.load_button.clicked.connect(self._load_songbook_from_file)
        self.save_button = QPushButton("Save Songbook")
        self.save_button.clicked.connect(self._save_songbook_to_file)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.move_up_button)
        button_layout.addWidget(self.move_down_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        self.manage_layout.addLayout(button_layout)

        self._populate_songbook_list()

    def _populate_songbook_list(self):
        self.songbook_list_widget.clear()
        for song in self.songbook:
            self.songbook_list_widget.addItem(f"{song['title']} ({song['pdf_filename']})")


    def _add_song_to_songbook(self):
        title = self.add_title_input.text().strip()
        pdf_filename = self.add_pdf_input.text().strip()
        desc_filename = self.add_desc_input.text().strip() if self.add_desc_input.text().strip() else None
        if title and pdf_filename:
            selected_index = self.songbook_list_widget.currentRow()
            if selected_index >= 0:
                self.songbook.insert(selected_index + 1, {"title": title, "pdf_filename": pdf_filename, "description_filename": desc_filename})  # Insert after selected
            else:
                self.songbook.append({"title": title, "pdf_filename": pdf_filename, "description_filename": desc_filename})  # Append if no selection
            self._populate_songbook_list()
            self.add_title_input.clear()
            self.add_pdf_input.clear()
            self.add_desc_input.clear()
        self._set_songbook_modified()

    def _remove_selected_song(self):
        selected_index = self.songbook_list_widget.currentRow()
        if selected_index >= 0:
            del self.songbook[selected_index]
            self._populate_songbook_list()
            if self.songbook:
                self.current_song_index = min(self.current_song_index, len(self.songbook) - 1)
                self._load_current_song()
            else:
                self.current_song_index = 0
                self._clear_performance_view()
        self._set_songbook_modified()

    def _populate_edit_fields(self, index):
        if 0 <= index < len(self.songbook):
            selected_song = self.songbook[index]
            self.edit_title_input.setText(selected_song['title'])
            self.edit_pdf_input.setText(selected_song['pdf_filename'])
            self.edit_desc_input.setText(selected_song.get('description_filename', ''))

    def _edit_selected_song(self):
        selected_index = self.songbook_list_widget.currentRow()
        if 0 <= selected_index < len(self.songbook):
            selected_song = self.songbook[selected_index]
            self._populate_edit_fields(selected_index) # Populate fields for editing

    def _save_edited_song(self):
        selected_index = self.songbook_list_widget.currentRow()
        if 0 <= selected_index < len(self.songbook):
            self.songbook[selected_index]['title'] = self.edit_title_input.text().strip()
            self.songbook[selected_index]['pdf_filename'] = self.edit_pdf_input.text().strip()
            desc = self.edit_desc_input.text().strip()
            self.songbook[selected_index]['description_filename'] = desc if desc else None
            self._populate_songbook_list()
            self._load_current_song() # Update perform view if current song was edited
        self._set_songbook_modified()

    def _move_song_up(self):
        selected_index = self.songbook_list_widget.currentRow()
        if selected_index > 0:
            self.songbook[selected_index], self.songbook[selected_index - 1] = self.songbook[selected_index - 1], self.songbook[selected_index]
            self._populate_songbook_list()
            self.songbook_list_widget.setCurrentRow(selected_index - 1)
        self._set_songbook_modified()

    def _move_song_down(self):
        selected_index = self.songbook_list_widget.currentRow()
        if 0 <= selected_index < len(self.songbook) - 1:
            self.songbook[selected_index], self.songbook[selected_index + 1] = self.songbook[selected_index + 1], self.songbook[selected_index]
            self._populate_songbook_list() 
            self.songbook_list_widget.setCurrentRow(selected_index + 1)
        self._set_songbook_modified()


    def _save_songbook_to_file(self):
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Songbook", "", "JSON Files (*.json);;All Files (*)", options=options)
            if file_name:
                if not file_name.endswith(".json"):
                    file_name += ".json"
                try:
                    with open(file_name, 'w') as f:
                        json.dump(self.songbook, f, indent=4)
                    self.statusbar.showMessage(f"Songbook saved to {file_name}", 5000)
                except Exception as e:
                    QMessageBox.critical(self, "Error Saving Songbook", f"An error occurred while saving the songbook: {e}")

    def _load_songbook_from_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Songbook", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.songbook = json.load(f)
                self._populate_songbook_list()
                if self.songbook:
                    self._load_current_song()
                else:
                    self._clear_performance_view()
                self.statusbar.showMessage(f"Songbook loaded from {file_name}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error Loading Songbook", f"An error occurred while loading the songbook: {e}")

    def _reload_songbook(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Reload Songbook", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.songbook = json.load(f)
                self._populate_songbook_list()
                if self.songbook:
                    self._load_current_song()
                else:
                    self._clear_performance_view()
                self.statusbar.showMessage(f"Songbook reloaded from {file_name}", 5000)
                self.songbook_modified = False # Reset modified flag after reload
            except Exception as e:
                QMessageBox.critical(self, "Error Reloading Songbook", f"An error occurred while reloading the songbook: {e}")

    def _prompt_save_on_tab_change(self, index):
        if self.songbook_modified and index == self.tabs.indexOf(self.perform_tab):
            reply = self._prompt_save()
            if reply == QMessageBox.Cancel:
                self.tabs.setCurrentIndex(self.tabs.indexOf(self.manage_tab)) # Stay on Manage tab

    def _prompt_save(self):
        reply = QMessageBox.question(self, "Save Changes", "Do you want to save changes to the songbook?",
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
        result = reply
        if result == QMessageBox.Save:
            self._save_songbook_to_file()
            self.songbook_modified = False
            return QMessageBox.Save
        elif result == QMessageBox.Discard:
            self._reload_songbook() # Reload from file
            return QMessageBox.Discard
        else:
            return QMessageBox.Cancel

    def closeEvent(self, event):
        if self.songbook_modified:
            reply = self._prompt_save()
            if reply == QMessageBox.Cancel:
                event.ignore() # Don't close
            else:
                event.accept() # Close if Save or Discard
        else:
            event.accept() # Close if no changes

    def _show_songbook_overview(self):
        self.pdf_label.hide()
        self.description_display.show()
        overview_text = "Planned Performance:\n"
        for i, song in enumerate(self.songbook):
            overview_text += f"{i + 1}. {song['title']}\n"
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

    def _load_description(self):
        current_song

    def _update_status_bar(self):
        total_songs = len(self.songbook)
        current_song = self.songbook[self.current_song_index] if self.songbook else {"title": "No Songs"}
        current_song_title = current_song.get("title", "No Title")
        current_pdf_pages = len(self.pdf_document) if self.pdf_document else 0
        current_display_page = self.current_page_index_within_song + 1 if self.current_page_index_within_song != -1 else "Desc"

        status_text = f"Song: {self.current_song_index + 1}/{total_songs} ({current_song_title}) | Page: {current_display_page}/{current_pdf_pages}"
        self.statusbar.showMessage(status_text, 0)  # Use showMessage with a timeout of 0 (persistent)

    def _load_description(self):
        current_song = self.songbook[self.current_song_index]
        description_filename = current_song.get('description_filename')
        if description_filename:
            try:
                with open(description_filename, 'r') as f:
                    self.description_text_content = f.read()
            except FileNotFoundError:
                self.description_text_content = f"Description file not found: {description_filename}"
            except Exception as e:
                self.description_text_content = f"Error loading description: {e}"
        else:
            self.description_text_content = ""

    def _load_current_song(self):
        if 0 <= self.current_song_index < len(self.songbook):
            current_song = self.songbook[self.current_song_index]
            self.setWindowTitle(f"MusicViewer - Performing: {current_song['title']}")
            self.song_title_label.setText(current_song['title'])
            try:
                self.pdf_document = fitz.open(current_song['pdf_filename'])
                self.current_page_index_within_song = -1  # Start with description
            except Exception as e:
                self.pdf_label.setText(f"Error loading PDF: {current_song['pdf_filename']} - {e}")
                self.pdf_document = None
                self.current_page_index_within_song = -1
            self._load_description()
            self._show_content()
        else:
            self.song_title_label.setText("End of Songbook")
            self.pdf_label.clear()
            self.pdf_document = None
            self.description_display.clear()
            self.current_page_index_within_song = -1
        self._update_status_bar()

    def _show_first_pdf_page_scaled(self):
        if self.pdf_document:
            self.current_page_index_within_song = 0
            self._show_content()

    def _show_content(self):
        if self.current_page_index_within_song == -1:
            self.pdf_label.hide()
            self.description_display.show()
            self.description_display.setText(self.description_text_content)
        elif self.pdf_document:
            self.pdf_label.show()
            self.description_display.hide()
            if 0 <= self.current_page_index_within_song < len(self.pdf_document):
                page = self.pdf_document.load_page(self.current_page_index_within_song)
                pix = page.get_pixmap()
                img = QImage(
                    pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888
                )
                pdf_pixmap = QPixmap.fromImage(img)

                label_size = self.pdf_label.size()
                scaled_pixmap = pdf_pixmap.scaled(
                    label_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.pdf_label.setPixmap(scaled_pixmap)
            else:
                self.pdf_label.setText("End of PDF")
        else:
            self.pdf_label.setText("No PDF loaded.")
            self.description_display.clear()
        self._update_status_bar()


    def resizeEvent(self, event):
        if self.current_page_index_within_song == -2:
            self._show_songbook_overview()
        elif self.pdf_document and self.current_page_index_within_song != -1:
            self._show_content()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            if self.current_page_index_within_song == -2: # From overview, go to first song's description
                self.current_song_index = 0
                self._load_current_song() # This will set current_page_index_within_song to -1
                self._show_content() # Show description
            elif self.current_page_index_within_song == -1:
                self.current_page_index_within_song = 0
                self._show_content()
                if self.pdf_document and len(self.pdf_document) > 1:
                    QTimer.singleShot(0, self._force_scale_page_two)
            elif self.pdf_document and self.current_page_index_within_song < len(self.pdf_document) - 1:
                self.current_page_index_within_song += 1
                self._show_content()
            else:
                self._next_song()
                return
        elif event.key() == Qt.Key_PageUp:
            if self.current_page_index_within_song > 0:
                self.current_page_index_within_song -= 1
                self._show_content()
            elif self.current_page_index_within_song == 0:
                self.current_page_index_within_song = -1
                self._show_content()
            elif self.current_page_index_within_song == -1:
                if self.current_song_index > 0:
                    self.current_song_index -= 1
                    self._load_current_song() # Load previous song
                    if self.pdf_document and len(self.pdf_document) > 1:
                        QTimer.singleShot(0, self._force_scale_last_page) # New: Force scale last page
                    elif self.pdf_document:
                        self.current_page_index_within_song = len(self.pdf_document) - 1 # Go to last page
                    else:
                        self.current_page_index_within_song = -1 # No PDF, show description
                    self._show_content()
                else:
                    self._show_songbook_overview()
            else:
                self._prev_song()
                return
        elif event.key() == Qt.Key_Left:
            if self.current_page_index_within_song > 0:
                self.current_page_index_within_song -= 1
                self._show_content()
        elif event.key() == Qt.Key_Right:
            if self.pdf_document and self.current_page_index_within_song < len(self.pdf_document) - 1:
                self.current_page_index_within_song += 1
                self._show_content()
        self._update_status_bar()
        super().keyPressEvent(event)

    def _force_scale_page_two(self):
        if self.pdf_document and len(self.pdf_document) > 1:
            self.current_page_index_within_song = 1
            self._show_content()
            QTimer.singleShot(0, self._revert_to_page_one)

    def _revert_to_page_one(self):
        if self.pdf_document:
            self.current_page_index_within_song = 0
            self._show_content()

    def _force_scale_last_page(self):
        if self.pdf_document and len(self.pdf_document) > 1:
            last_page_index = len(self.pdf_document) - 1
            self.current_page_index_within_song = last_page_index - 1 # Briefly go to second to last
            self._show_content()
            QTimer.singleShot(0, self._revert_to_last_page)

    def _revert_to_last_page(self):
        if self.pdf_document:
            self.current_page_index_within_song = len(self.pdf_document) - 1
            self._show_content()


    def _prev_song(self):
        if self.current_song_index > 0:
            self.current_song_index -= 1
            self._load_current_song()
        else:
            self.song_title_label.setText("First Song")
            self.pdf_document = None
            self.description_display.clear()
            self.pdf_label.clear()
            self.current_song_index = -1 
            self.current_page_index_within_song = -1
        self._update_status_bar()

    def _next_song(self):
        if self.current_song_index < len(self.songbook) - 1:
            self.current_song_index += 1
            self.current_page_index_within_song = -1 # Reset to description on next song
            self._load_current_song()
        else:
            self.song_title_label.setText("Last Song")
            self.pdf_document = None
            self.description_display.clear()
            self.pdf_label.clear()
            self.current_page_index_within_song = -1
        self._update_status_bar()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.showMaximized()
    sys.exit(app.exec_())