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
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MusicViewer - Perform Songbook")
        self.songbook = [
            {"title": "Song 1", "pdf_filename": "song1.pdf", "description_filename": "song1_desc.txt"},
            {"title": "Song 2", "pdf_filename": "song2.pdf", "description_filename": "song2_desc.txt"},
            {"title": "Another Song", "pdf_filename": "song3.pdf", "description_filename": None},
            {"title": "Yet Another Tune", "pdf_filename": "song4.pdf", "description_filename": "tune4_info.txt"},
            {"title": "Final Song", "pdf_filename": "song5.pdf", "description_filename": "final_notes.txt"},
        ]
        self.current_song_index = 0
        self.pdf_document = None
        self.current_page_index_within_song = -1 # -1: description, >= 0: PDF page
        self.description_text_content = ""

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setFocusPolicy(Qt.StrongFocus)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.song_title_label = QLabel()
        self.song_title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.song_title_label)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pdf_label.setMinimumSize(1, 1)
        self.content_layout.addWidget(self.pdf_label)
        self.description_display = QTextEdit()
        self.description_display.setReadOnly(True)
        self.content_layout.addWidget(self.description_display)
        self.main_layout.addWidget(self.content_area, 1)

        self.setMinimumSize(600, 800)

        self.statusbar = QLabel("Ready")
        self.statusbar.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.main_layout.addWidget(self.statusbar)

        self._load_current_song()
        self.show()
        QTimer.singleShot(100, self._show_content)
        self._update_status_bar() # Initial status update

    def _update_status_bar(self):
        total_songs = len(self.songbook)
        current_song = self.songbook[self.current_song_index] if self.songbook else {"title": "No Songs"}
        current_song_title = current_song.get("title", "No Title")
        current_pdf_pages = len(self.pdf_document) if self.pdf_document else 0
        current_display_page = self.current_page_index_within_song + 1 if self.current_page_index_within_song != -1 else "Desc"

        status_text = f"Song: {self.current_song_index + 1}/{total_songs} ({current_song_title}) | Page: {current_display_page}/{current_pdf_pages}"
        self.statusbar.setText(status_text)

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
        if self.pdf_document and self.current_page_index_within_song != -1:
            self._show_content()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            if self.current_page_index_within_song == -1:
                self.current_page_index_within_song = 0
                self._show_content()
                if self.pdf_document and len(self.pdf_document) > 1:
                    QTimer.singleShot(0, self._force_scale_page_two)
            elif self.pdf_document and self.current_page_index_within_song < len(self.pdf_document) - 1:
                self.current_page_index_within_song += 1
                self._show_content()
            else:
                self._next_song()
                return  # Prevent further processing after song change
        elif event.key() == Qt.Key_PageUp:
            if self.current_page_index_within_song > 0:
                self.current_page_index_within_song -= 1
                self._show_content()
            elif self.current_page_index_within_song == 0:
                self.current_page_index_within_song = -1
                self._show_content()
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