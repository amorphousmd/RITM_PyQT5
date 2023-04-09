import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog
from PIL import Image, ImageTk

class PyQtCanvas(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.canvas = QtWidgets.QLabel(self)
        self.canvas.setFixedSize(500, 500)
        self.canvas.setStyleSheet("background-color: white;")
        self.layout().addWidget(self.canvas)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.active = False

        self.toggle_button = QtWidgets.QPushButton('Toggle', self)
        self.toggle_button.clicked.connect(self.toggle)
        self.layout().addWidget(self.toggle_button)

        self.load_button = QtWidgets.QPushButton('Load Image', self)
        self.load_button.clicked.connect(self.load_image)
        self.layout().addWidget(self.load_button)

    def toggle(self):
        self.active = not self.active

    def mousePressEvent(self, event):
        if self.active:
            self.start_x = event.x()
            self.start_y = event.y()

    def mouseMoveEvent(self, event):
        if self.active:
            self.end_x = event.x()
            self.end_y = event.y()
            if self.rect:
                self.rect.setParent(None)
            self.rect = QtWidgets.QFrame(self.canvas)
            self.rect.setFrameStyle(QtWidgets.QFrame.Box)
            self.rect.setGeometry(self.start_x, self.start_y, self.end_x - self.start_x, self.end_y - self.start_y)
            self.rect.setStyleSheet("border: 2px solid red;")

    def mouseReleaseEvent(self, event):
        if self.active:
            self.end_x = event.x()
            self.end_y = event.y()

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName()
        if file_path:
            image = Image.open(file_path)
            image = image.resize((500, 500))
            self.image = image
            self.canvas.setPixmap(QtGui.QPixmap.fromImage(
                QtGui.QImage(image.tobytes(), image.size[0], image.size[1], QtGui.QImage.Format_RGB888)))
            self.canvas.mousePressEvent = lambda event: self.canvas_mouse_press_event(event, self.image)
            self.canvas.mouseMoveEvent = lambda event: self.canvas_mouse_move_event(event, self.image)
            self.canvas.mouseReleaseEvent = lambda event: self.canvas_mouse_release_event(event, self.image)

class InteractiveSegmentation(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Interactive Segmentation')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.canvas = PyQtCanvas(self)
        self.layout().addWidget(self.canvas)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = InteractiveSegmentation()
    gui.show()
    sys.exit(app.exec_())
