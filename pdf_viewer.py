import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QSizePolicy,
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

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
        self.current_page = 0

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setFocusPolicy(Qt.StrongFocus)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Remove margins

        self.song_title_label = QLabel()
        self.song_title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.song_title_label)

        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Allow expansion in both directions
        self.main_layout.addWidget(self.pdf_label, 1) # Add stretch factor

        self._load_current_song()
        self._display_page(self.current_page)

    def resizeEvent(self, event):
        if self.pdf_document:
            self._display_page(self.current_page, force_resize=True)
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self._prev_song()
        elif event.key() == Qt.Key_PageDown:
            self._next_song()
        elif event.key() == Qt.Key_Left:
            self._prev_page()
        elif event.key() == Qt.Key_Right:
            self._next_page()
        super().keyPressEvent(event)

    def _load_current_song(self):
        if 0 <= self.current_song_index < len(self.songbook):
            current_song = self.songbook[self.current_song_index]
            self.setWindowTitle(f"MusicViewer - Performing: {current_song['title']}")
            self.song_title_label.setText(current_song['title'])
            try:
                self.pdf_document = fitz.open(current_song['pdf_filename'])
                self.current_page = 0
            except Exception as e:
                self.pdf_label.setText(f"Error loading PDF: {current_song['pdf_filename']} - {e}")
                self.pdf_document = None
            self._display_page(self.current_page)
        else:
            self.song_title_label.setText("End of Songbook")
            self.pdf_label.clear()
            self.pdf_document = None

    def _prev_song(self):
        if self.current_song_index > 0:
            self.current_song_index -= 1
            self._load_current_song()
        else:
            self.song_title_label.setText("First Song")

    def _next_song(self):
        if self.current_song_index < len(self.songbook) - 1:
            self.current_song_index += 1
            self._load_current_song()
        else:
            self.song_title_label.setText("Last Song")

    def _display_page(self, page_num, force_resize=False):
        if self.pdf_document:
            if 0 <= page_num < len(self.pdf_document):
                page = self.pdf_document.load_page(page_num)
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
                self.current_page = page_num
            else:
                self.pdf_label.setText("End of PDF")
        else:
            self.pdf_label.setText("No PDF loaded.")

    def _prev_page(self):
        if self.pdf_document and self.current_page > 0:
            self._display_page(self.current_page - 1)

    def _next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self._display_page(self.current_page + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    #viewer.showMaximized()
    viewer.show()
    sys.exit(app.exec_())