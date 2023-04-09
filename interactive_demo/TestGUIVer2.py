import tkinter as tk
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import Qt

class MyGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # create a QVBoxLayout to hold the embedded tkinter window
        layout = QVBoxLayout()

        # create the tkinter window and any necessary widgets
        tk_window = tk.Tk()
        label = tk.Label(tk_window, text="Hello, tkinter!")
        label.pack()

        # get the window ID of the tkinter window
        tk_id = tk_window.winfo_id()

        # create a QWindow and set its window ID to the tkinter ID
        qt_window = QWindow.fromWinId(tk_id)
        qt_window.setFlags(qt_window.flags() | Qt.WindowTransparentForInput | Qt.WindowOverridesSystemGestures)

        # create a QWidget to hold the QWindow object
        embedded_widget = QWidget.createWindowContainer(qt_window)

        # add the QWidget to the layout
        layout.addWidget(embedded_widget)

        # set the layout for the PyQt widget and show the window
        self.setLayout(layout)
        self.show()

if __name__ == '__main__':
    app = QApplication([])
    gui = MyGUI()
    app.exec_()