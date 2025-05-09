import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class PDFViewer(QMainWindow):
    def __init__(self, pdf_path):
        super().__init__()
        self.setWindowTitle("Simple PDF Viewer")
        self.pdf_path = pdf_path
        self.pdf_document = None
        self.current_page = 0

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setFocusPolicy(Qt.StrongFocus)

        self.main_layout = QVBoxLayout(self.central_widget)  # Use QVBoxLayout

        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.pdf_label)

        self._load_pdf()
        self._display_page(self.current_page)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self._prev_page()
        elif event.key() == Qt.Key_Right:
            self._next_page()
        super().keyPressEvent(event)

    def _load_pdf(self):
        try:
            self.pdf_document = fitz.open(self.pdf_path)
        except Exception as e:
            self.pdf_label.setText(f"Error loading PDF: {e}")

    def _display_page(self, page_num):
        if self.pdf_document:
            if 0 <= page_num < len(self.pdf_document):
                page = self.pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img = QImage(
                    pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888
                )
                self.pdf_label.setPixmap(QPixmap.fromImage(img))
                self.current_page = page_num
            else:
                self.pdf_label.setText("End of PDF")

    def _prev_page(self):
        if self.current_page > 0:
            self._display_page(self.current_page - 1)

    def _next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self._display_page(self.current_page + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Replace 'your_score.pdf' with the actual path to a PDF file in your project
    viewer = PDFViewer("your_score.pdf")
    viewer.showMaximized()
    sys.exit(app.exec_())