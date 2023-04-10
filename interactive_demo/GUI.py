import argparse
import multiprocessing as mp
import tkinter as tk
import time
import cv2
from PIL import Image, ImageDraw, ImageQt, ImageTk
import numpy as np
import io
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton

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
            if msg == 'button_clicked':
                # invoke the button in the tkinter GUI
                app.menubar.children['!focusbutton'].invoke()
                simulate_canvas_click(app, x=200, y=200)
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
    window.setGeometry(0, 0, 800, 600)

    label = QLabel(window)
    label.setGeometry(50, 50, 640, 480)

    button = QPushButton('Click me', window)
    button.clicked.connect(lambda: conn.send('button_clicked'))
    button.move(10, 10)

    window.show()

    while True:
        # check if there is any message from the main process
        if conn.poll():
            img = conn.recv()
            data = Image.fromarray(img)
            ## save the image file as png
            data.save('image.png')
            temp = cv2.imread('image.png')
            temp = cv2.cvtColor(temp, cv2.COLOR_RGB2BGR)
            cv2.imwrite('image.png', temp)
            pixmap = QPixmap('image.png')
            label.setPixmap(pixmap)

        app.processEvents()


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
        args.device =torch.device('cpu')
    else:
        args.device = torch.device(f'cuda:{args.gpu}')
    cfg = exp.load_config_file(args.cfg, return_edict=True)

    return args, cfg

def simulate_canvas_click(app, x, y):
    event = tk.Event()
    event.x = x
    event.y = y
    app.canvas.event_generate("<ButtonPress-1>", x=x, y=y, time=0, state=1)
    app.canvas.event_generate("<ButtonRelease-1>", x=x, y=y, time=0, state=0)


def get_canvas_image(app):
    # Get the position of the canvas relative to the screen

    # Get the size of the canvas
    # canvas_width = int(app.canvas.winfo_width() *1)
    # canvas_height = int(app.canvas.winfo_height() * 1)
    canvas_width = 440
    canvas_height = 330

    # Create a blank image
    img = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))

    # Draw the contents of the canvas onto the image
    img_draw = ImageDraw.Draw(img)
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


if __name__ == '__main__':
    main()
