import tkinter as tk
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
import sys

class InteractiveDemoApp(tk.Frame):
    def __init__(self, master, args, model):
        super().__init__(master)
        self.args = args
        self.model = model

        self.menubar = tk.Frame(self, bd=1)
        self.menubar.pack(side=tk.TOP, fill='x')

        button = tk.Button(self.menubar, text='Load image', command=self._load_image_callback)
        button.pack(side=tk.LEFT)

    def _load_image_callback(self):
        print("Load image clicked!")


class MyWindow(QWidget):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        layout = QVBoxLayout(self)
        self.button = QPushButton('Invoke Load image on tkinter GUI')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.invoke_load_image)

    def invoke_load_image(self):
        root = tk.Tk()
        root.minsize(960, 480)
        app = InteractiveDemoApp(root, None, None)
        root.deiconify()
        app.menubar.children['!button'].invoke()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
