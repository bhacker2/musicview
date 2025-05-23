from PyQt5.QtWidgets import QApplication
from view import PDFViewerWindow
from controller import PDFViewerController

def main():
    app = QApplication([])
    window = PDFViewerWindow()
    controller = PDFViewerController(window)
    window.set_controller(controller)
    window.show()
    app.exec_()



if __name__ == "__main__":
    main()
