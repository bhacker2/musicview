from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from model import Song, Songbook
from view import PDFViewerWindow
import sys
import fitz  # PyMuPDF

class PDFViewerController:
    def __init__(self, window: PDFViewerWindow):
        self.window = window
        self.songbook = Songbook()
        self.current_song_index = 0
        self.songbook_modified = False  # Flag to track changes

        # Connect signals and slots here
        # e.g., self.window.add_button.clicked.connect(self.add_song)
        # Implement all logic for add, remove, move, save, load, etc.
        self.window.songbook_list_widget.currentRowChanged.connect(self._populate_edit_fields) # Con
        self.window.save_edit_button.clicked.connect(self._save_edited_song)
        self.window.add_button.clicked.connect(self._add_song_to_songbook)
        
        self.window.remove_button.clicked.connect(self._remove_selected_song)
        self.window.move_up_button.clicked.connect(self._move_song_up)
        self.window.move_down_button.clicked.connect(self._move_song_down)
        self.window.load_button.clicked.connect(self._load_songbook_from_file)
        self.window.save_button.clicked.connect(self._save_songbook_to_file)
        self.window.tabs.currentChanged.connect(self._prompt_save_on_tab_change) # Connect tab change signal
 
        #fill view components with data as expected
        #perform
        self._load_songbook_from_file() # Load songbook from file
        self._load_current_song()
        QTimer.singleShot(100, self._show_content)
        self._update_status_bar()
        #manage
        self._populate_songbook_list()

        self.window.show()
        QTimer.singleShot(100, self._show_songbook_overview) # Show initial overview


    def add_song(self):
        # Gather input from view, update model, refresh view
        pass

    def remove_song(self):
        pass

    # ... more controller methods for each action
    def _set_songbook_modified(self, modified=True):
        self.songbook_modified = modified

    def _populate_songbook_list(self):
        self.window.songbook_list_widget.clear()
        for song in self.songbook.songs:
            song_title = song.title
            song.pdfilename = song.pdf_filename
            self.window.songbook_list_widget.addItem(f"{song.title} {song.pdf_filename}")


    def _add_song_to_songbook(self):
        title = self.window.add_title_input.text().strip()
        pdf_filename = self.window.add_pdf_input.text().strip()
        desc_filename = self.window.add_desc_input.text().strip() if self.window.add_desc_input.text().strip() else None
        new_song = Song(title, pdf_filename, desc_filename)
        if title and pdf_filename:
            selected_index = self.window.songbook_list_widget.currentRow()
            if selected_index >= 0:
                self.songbook.add_song(new_song, selected_index)
            else:
                self.songbook.add_song(new_song)
            self._populate_songbook_list()
            self.window._clear_add_fields()
        self._set_songbook_modified()

    def _remove_selected_song(self):
        selected_index = self.window.songbook_list_widget.currentRow()
        if selected_index >= 0:
            del self.songbook.songs[selected_index]
            self._populate_songbook_list()
            if self.songbook:
                self.current_song_index = min(self.current_song_index, self.songbook.song_count() - 1)
                self._load_current_song()
            else:
                self.current_song_index = 0
                self._clear_performance_view()
        self._set_songbook_modified()

    def _populate_edit_fields(self, index):
        if 0 <= index < self.songbook.song_count():
            self.window._populate_edit_fields(self.songbook.songs[index])

    def _edit_selected_song(self):
        selected_index = self.window.songbook_list_widget.currentRow()
        if 0 <= selected_index < self.songbook.song_count():
            selected_song = self.songbook.songs[selected_index]
            self._populate_edit_fields(selected_index) # Populate fields for editing

    def _save_edited_song(self):
        selected_index = self.window.songbook_list_widget.currentRow()
        if 0 <= selected_index < self.songbook.song_count():
            title = self.window.edit_title_input.text().strip()
            pdf_filename = self.window.edit_pdf_input.text().strip()
            desc_filename = self.window.edit_desc_input.text().strip() if self.window.edit_desc_input.text().strip() else None
            new_song = Song(title, pdf_filename, desc_filename)
            self.songbook.remove_song(selected_index)
            self.songbook.add_song(new_song,selected_index)
            # self.songbook[selected_index]['title'] = self.window.edit_title_input.text().strip()
            # self.songbook[selected_index]['pdf_filename'] = self.window.edit_pdf_input.text().strip()
            # desc = self.window.edit_desc_input.text().strip()
            # self.songbook[selected_index]['description_filename'] = desc if desc else None
            self._populate_songbook_list()
            self._load_current_song() # Update perform view if current song was edited
            self._set_songbook_modified()

    def _move_song_up(self):
        selected_index = self.window.songbook_list_widget.currentRow()
        if selected_index > 0:
            self.songbook.move_song(selected_index, selected_index - 1)
            #self.songbook[selected_index], self.songbook[selected_index - 1] = self.songbook[selected_index - 1], self.songbook[selected_index]
            self._populate_songbook_list()
            self.window.songbook_list_widget.setCurrentRow(selected_index - 1)
            self._set_songbook_modified()

    def _move_song_down(self):
        selected_index = self.window.songbook_list_widget.currentRow()
        if 0 <= selected_index < self.songbook.song_count() - 1:
            self.songbook.move_song(selected_index, selected_index + 1)
            #self.songbook[selected_index], self.songbook[selected_index + 1] = self.songbook[selected_index + 1], self.songbook[selected_index]
            self._populate_songbook_list() 
            self.window.songbook_list_widget.setCurrentRow(selected_index + 1)
            self._set_songbook_modified()

    def _prompt_save_on_tab_change(self, index):
        if self.songbook_modified and index == self.window.tabs.indexOf(self.window.perform_tab):
            reply = self._prompt_save()
            if reply == QMessageBox.Cancel:
                self.window.tabs.setCurrentIndex(self.window.tabs.indexOf(self.window.manage_tab)) # Stay on Manage tab

    def _prompt_save(self):
        reply = QMessageBox.question(self.window, "Save Changes", "Do you want to save changes to the songbook?",
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
        self.window._show_songbook_overview(self.songbook)
        # self.pdf_label.hide()
        # self.description_display.show()
        # overview_text = "Planned Performance:\n"
        # for i, song in enumerate(self.songbook):
        #     overview_text += f"{i + 1}. {song['title']}\n"
        # self.description_display.setText(overview_text)
        # self.setWindowTitle("MusicViewer - Songbook Overview")
        # self.song_title_label.setText("Songbook Overview")
        # self.current_page_index_within_song = -2 # Ensure it's set to overview state


    def _clear_performance_view(self):
        self.window._clear_performance_view()
        # self.song_title_label.clear()
        # self.pdf_label.clear()
        # self.description_display.clear()
        # self.pdf_document = None
        # self.current_page_index_within_song = -1

    def _update_status_bar(self):
        total_songs = self.songbook.song_count()
        current_song = self.songbook.songs[self.current_song_index] if self.songbook else {"title": "No Songs"}
        current_song_title = current_song.title
        current_pdf_pages = len(self.pdf_document) if self.pdf_document else 0
        current_display_page = self.current_page_index_within_song + 1 if self.current_page_index_within_song != -1 else "Desc"

        status_text = f"Song: {self.current_song_index + 1}/{total_songs} ({current_song_title}) | Page: {current_display_page}/{current_pdf_pages}"
        self.window.statusbar.showMessage(status_text, 0)  # Use showMessage with a timeout of 0 (persistent)

    def _load_description(self):
        current_song = self.songbook.songs[self.current_song_index]
        description_filename = current_song.description_filename
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
        if 0 <= self.current_song_index < len(self.songbook.songs):
            current_song = self.songbook.songs[self.current_song_index]
            self.window.setWindowTitle(f"MusicViewer - Performing: {current_song.title}")
            self.window.song_title_label.setText(current_song.title)
            try:
                self.pdf_document = fitz.open(current_song.pdf_filename)
                self.current_page_index_within_song = -1  # Start with description
            except Exception as e:
                self.window.pdf_label.setText(f"Error loading PDF: {current_song.pdf_filename} - {e}")
                self.pdf_document = None
                self.current_page_index_within_song = -1
            self._load_description()
            self._show_content()
        else:
            self.window.song_title_label.setText("End of Songbook")
            self.window.pdf_label.clear()
            self.pdf_document = None
            self.window.description_display.clear()
            self.current_page_index_within_song = -1
        self._update_status_bar()

    def _show_first_pdf_page_scaled(self):
        if self.pdf_document:
            self.current_page_index_within_song = 0
            self._show_content()

    def _show_content(self):
        if self.current_page_index_within_song == -1:
            self.window.pdf_label.hide()
            self.window.description_display.show()
            self.window.description_display.setText(self.description_text_content)
        elif self.pdf_document:
            self.window.pdf_label.show()
            self.window.description_display.hide()
            if 0 <= self.current_page_index_within_song < len(self.pdf_document):
                page = self.pdf_document.load_page(self.current_page_index_within_song)
                pix = page.get_pixmap()
                img = QImage(
                    pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888
                )
                pdf_pixmap = QPixmap.fromImage(img)

                label_size = self.window.pdf_label.size()
                scaled_pixmap = pdf_pixmap.scaled(
                    label_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.window.pdf_label.setPixmap(scaled_pixmap)
            else:
                self.window.pdf_label.setText("End of PDF")
        else:
            self.window.pdf_label.setText("No PDF loaded.")
            self.window.description_display.clear()
        self._update_status_bar()


    def resizeEvent(self, event):
        if self.current_page_index_within_song == -2:
            self._show_songbook_overview()
        elif self.pdf_document and self.current_page_index_within_song != -1:
            self._show_content()
        super().resizeEvent(event)

    # def keyPressEvent(self, event):

    def handle_PageDown_event(self, event):
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

        self._update_status_bar()
            
    def handle_PageUp_event(self, event):
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
        
        self._update_status_bar()
        
        # elif event.key() == Qt.Key_Left:
        #     if self.current_page_index_within_song > 0:
        #         self.current_page_index_within_song -= 1
        #         self._show_content()
        # elif event.key() == Qt.Key_Right:
        #     if self.pdf_document and self.current_page_index_within_song < len(self.pdf_document) - 1:
        #         self.current_page_index_within_song += 1
        #         self._show_content()
        # self._update_status_bar()
        # super().keyPressEvent(event)

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
            self.window.song_title_label.setText("First Song")
            self.pdf_document = None
            self.window.description_display.clear()
            self.window.pdf_label.clear()
            self.current_song_index = -1 
            self.current_page_index_within_song = -1
        self._update_status_bar()

    def _next_song(self):
        if self.current_song_index < self.songbook.song_count() - 1:
            self.current_song_index += 1
            self.current_page_index_within_song = -1 # Reset to description on next song
            self._load_current_song()
        else:
            self.window.song_title_label.setText("Last Song")
            self.pdf_document = None
            self.window.description_display.clear()
            self.window.pdf_label.clear()
            self.current_page_index_within_song = -1
        self._update_status_bar()

# FILE DIALOG METHODS

##  File I/O operations
    def _save_songbook_to_file(self):
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self.window, "Save Songbook", "", "JSON Files (*.json);;All Files (*)", options=options)
            if file_name:
                if not file_name.endswith(".json"):
                    file_name += ".json"
                try:
                    self.songbook.save(file_name)
                    # with open(file_name, 'w') as f:
                    #     json.dump(self.songs, f, indent=4)
                    self.window.statusbar.showMessage(f"Songbook saved to {file_name}", 5000)
                except Exception as e:
                    QMessageBox.critical(self.window, "Error Saving Songbook", f"An error occurred while saving the songbook: {e}")

    def _load_songbook_from_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Load Songbook", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                self.songbook.load(file_name)
                # with open(file_name, 'r') as f:
                #     self.songs = json.load(f)
                self._populate_songbook_list()
                if self.songbook:
                    self._load_current_song()
                else:
                    self._clear_performance_view()
                self.window.statusbar.showMessage(f"Songbook loaded from {file_name}", 5000)
            except Exception as e:
                QMessageBox.critical(self.window, "Error Loading Songbook", f"An error occurred while loading the songbook: {e}")

    def _reload_songbook(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Reload Songbook", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                self.songbook.load(file_name)
                # with open(file_name, 'r') as f:
                #     self.songs = json.load(f)
                self._populate_songbook_list()
                if self.songbook:
                    self._load_current_song()
                else:
                    self._clear_performance_view()
                self.window.statusbar.showMessage(f"Songbook reloaded from {file_name}", 5000)
                self.songbook_modified = False # Reset modified flag after reload
            except Exception as e:
                QMessageBox.critical(self.window, "Error Reloading Songbook", f"An error occurred while reloading the songbook: {e}")

