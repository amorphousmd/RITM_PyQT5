import argparse
import multiprocessing as mp
import time
import cv2
from PIL import Image, ImageDraw, ImageQt, ImageTk
import numpy as np
import io

import tkinter as tk
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtCore import Qt

import torch
from isegm.utils import exp
from isegm.inference import utils
from interactive_demo.app import InteractiveDemoApp


def main():
    args, cfg = parse_args()

    torch.backends.cudnn.deterministic = True
    checkpoint_path = utils.find_checkpoint(cfg.INTERACTIVE_MODELS_PATH, args.checkpoint)
    model = utils.load_is_model(checkpoint_path, args.device, cpu_dist_maps=True)

    root = tk.Tk()
    root.minsize(960, 480)
    app = InteractiveDemoApp(root, args, model)

    root.deiconify()

    # start a separate process for the PyQt GUI
    parent_conn, child_conn = mp.Pipe()
    p = mp.Process(target=start_pyqt_gui, args=(child_conn,))
    p.start()

    while True:
        # check if there is any message from the PyQt GUI
        if parent_conn.poll():
            msg = parent_conn.recv()
            if msg[0] == 'load_button_clicked':
                # invoke the button in the tkinter GUI
                # root.withdraw()
                app.menubar.children['!focusbutton'].invoke()
                img = get_canvas_image(app)
                # extract the image from the canvas
                parent_conn.send(img)
                # send the image to PyQt GUI

            if msg[0] == 'canvas_clicked':
                if msg[3]:
                    simulate_canvas_click(app, True, x=msg[1], y=msg[2])
                else:
                    simulate_canvas_click(app, False, x=msg[1], y=msg[2])
                img = get_canvas_image(app)
                # extract the image from the canvas
                parent_conn.send(img)
                # send the image to PyQt GUI

            if msg[0] == 'save_button_clicked':
                # invoke the button in the tkinter GUI
                app.menubar.children['!focusbutton2'].invoke()

            if msg[0] == 'undo_button_clicked':
                # invoke the button in the tkinter GUI
                button_name = ".!interactivedemoapp.!focuslabelframe3.!focuslabelframe.!focusbutton2"
                app.clicks_options_frame.nametowidget(button_name).invoke()
                img = get_canvas_image(app)
                # extract the image from the canvas
                parent_conn.send(img)
                # send the image to PyQt GUI

            if msg[0] == 'reset_button_clicked':
                button_name = ".!interactivedemoapp.!focuslabelframe3.!focuslabelframe.!focusbutton3"
                app.clicks_options_frame.nametowidget(button_name).invoke()
                img = get_canvas_image(app)
                # extract the image from the canvas
                parent_conn.send(img)
                # send the image to PyQt GUI

            if msg[0] == 'done_button_clicked':
                button_name = ".!interactivedemoapp.!focuslabelframe3.!focuslabelframe.!focusbutton"
                app.clicks_options_frame.nametowidget(button_name).invoke()
                img = get_canvas_image(app)
                # extract the image from the canvas
                parent_conn.send(img)
                # send the image to PyQt GUI

        # update the tkinter GUI
        root.update()

        # sleep for a short time to avoid high CPU usage
        time.sleep(0.01)


def start_pyqt_gui(conn):
    app = QApplication([])
    window = QMainWindow()
    window.setWindowTitle('PyQt GUI')
    window.setGeometry(0, 0, 740, 580)

    label = QLabel(window)
    label.setGeometry(50, 50, 640, 480)
    label.setStyleSheet("background-color: black;")
    label.mousePressEvent = lambda event: handle_label_click(event, conn, label)

    load_button = QPushButton('Load', window)
    load_button.clicked.connect(lambda: load_image(conn, label))
    load_button.move(50, 10)

    undo_button = QPushButton('Undo', window)
    undo_button.clicked.connect(lambda: undo_click(conn, label))
    undo_button.move(184, 10)

    done_button = QPushButton('Done', window)
    done_button.clicked.connect(lambda: finish_image(conn, label))
    done_button.move(318, 10)

    reset_button = QPushButton('Reset', window)
    reset_button.clicked.connect(lambda: reset_clicks(conn, label))
    reset_button.move(452, 10)

    save_button = QPushButton('Save', window)
    save_button.clicked.connect(lambda: conn.send(('save_button_clicked', 0)))
    save_button.move(586, 10)

    window.show()
    app.exec_()


def load_image(conn, label):
    conn.send(('load_button_clicked', 0))
    while True:
        if conn.poll():
            img = conn.recv()
            break
    data = Image.fromarray(img)
    data.save('image.png')
    temp = cv2.imread('image.png')
    temp = cv2.cvtColor(temp, cv2.COLOR_RGB2BGR)
    cv2.imwrite('image.png', temp)
    pixmap = QPixmap('image.png').scaled(640, 480)
    label.setPixmap(pixmap)

def undo_click(conn, label):
    conn.send(('undo_button_clicked', 0))
    while True:
        if conn.poll():
            img = conn.recv()
            break
    data = Image.fromarray(img)
    data.save('image.png')
    temp = cv2.imread('image.png')
    temp = cv2.cvtColor(temp, cv2.COLOR_RGB2BGR)
    cv2.imwrite('image.png', temp)
    pixmap = QPixmap('image.png').scaled(640, 480)
    label.setPixmap(pixmap)

def reset_clicks(conn, label):
    conn.send(('reset_button_clicked', 0))
    while True:
        if conn.poll():
            img = conn.recv()
            break
    data = Image.fromarray(img)
    data.save('image.png')
    temp = cv2.imread('image.png')
    temp = cv2.cvtColor(temp, cv2.COLOR_RGB2BGR)
    cv2.imwrite('image.png', temp)
    pixmap = QPixmap('image.png').scaled(640, 480)
    label.setPixmap(pixmap)

def finish_image(conn, label):
    conn.send(('done_button_clicked', 0))
    while True:
        if conn.poll():
            img = conn.recv()
            break
    data = Image.fromarray(img)
    data.save('image.png')
    temp = cv2.imread('image.png')
    temp = cv2.cvtColor(temp, cv2.COLOR_RGB2BGR)
    cv2.imwrite('image.png', temp)
    pixmap = QPixmap('image.png').scaled(640, 480)
    label.setPixmap(pixmap)


def handle_label_click(event, conn, label):
    x = event.x()
    y = event.y()
    button = event.button()
    if button ==  Qt.MouseButton.LeftButton:
        print(f"Left click on label at position ({x}, {y})")
        conn.send(('canvas_clicked', int(x / 1.1), int(y / 1.1), 1))
    elif button ==  Qt.MouseButton.RightButton:
        print(f"Right click on label at position ({x}, {y})")
        conn.send(('canvas_clicked', int(x / 1.1), int(y / 1.1), 0))
    while True:
        if conn.poll():
            img = conn.recv()
            break
    data = Image.fromarray(img)
    data.save('image.png')
    temp = cv2.imread('image.png')
    temp = cv2.cvtColor(temp, cv2.COLOR_RGB2BGR)
    cv2.imwrite('image.png', temp)
    pixmap = QPixmap('image.png').scaled(640, 480)
    label.setPixmap(pixmap)


def simulate_canvas_click(app, leftclick, x, y,):
    event = tk.Event()
    event.x = x
    event.y = y
    if leftclick:
        app.canvas.event_generate("<ButtonPress-1>", x=x, y=y, time=0, state=1)
        app.canvas.event_generate("<ButtonRelease-1>", x=x, y=y, time=0, state=0)
    else:
        app.canvas.event_generate("<ButtonPress-3>", x=x, y=y, time=0, state=1)
        app.canvas.event_generate("<ButtonRelease-3>", x=x, y=y, time=0, state=0)


def get_canvas_image(app):
    # canvas_width = int(app.canvas.winfo_width() *1)
    # canvas_height = int(app.canvas.winfo_height() * 1)
    canvas_width = int(435 * 1.34)
    canvas_height = int(325 * 1.34)
    app.canvas.tk.call('tk', 'scaling', 1.0)

    # Draw the contents of the canvas onto the image
    app.canvas.postscript(file='canvas.eps')
    with open('canvas.eps', 'rb') as f:
        img_eps = io.BytesIO(f.read())
    img = Image.open(img_eps)
    img = img.crop((1, 1, canvas_width - 1, canvas_height - 1))

    # Convert the image to a numpy array
    img_array = np.array(img)

    # Convert the color space from BGR to RGB
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

    # Send the image to the PyQt GUI
    return img_array


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--checkpoint', type=str, required=False,
                        help='The path to the checkpoint. '
                             'This can be a relative path (relative to cfg.INTERACTIVE_MODELS_PATH) '
                             'or an absolute path. The file extension can be omitted.'
                        , default='coco_lvis_h18_itermask')

    parser.add_argument('--gpu', type=int, default=0,
                        help='Id of GPU to use.')

    parser.add_argument('--cpu', action='store_true', default=False,
                        help='Use only CPU for inference.')

    parser.add_argument('--limit-longest-size', type=int, default=800,
                        help='If the largest side of an image exceeds this value, '
                             'it is resized so that its largest side is equal to this value.')

    parser.add_argument('--cfg', type=str, default="config.yml",
                        help='The path to the config file.')

    args = parser.parse_args()
    if args.cpu:
        args.device = torch.device('cpu')
    else:
        args.device = torch.device(f'cuda:{args.gpu}')
    cfg = exp.load_config_file(args.cfg, return_edict=True)

    return args, cfg


if __name__ == '__main__':
    main()
