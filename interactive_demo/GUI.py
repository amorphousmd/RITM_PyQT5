import argparse
import multiprocessing as mp
import tkinter as tk
import time

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

        # update the tkinter GUI
        root.update()

        # sleep for a short time to avoid high CPU usage
        time.sleep(0.01)


def start_pyqt_gui(conn):
    # create a simple PyQt GUI with a button
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle('PyQt GUI')

    button = QPushButton('Click me', window)
    button.clicked.connect(lambda: conn.send('button_clicked'))

    window.show()

    sys.exit(app.exec_())


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


if __name__ == '__main__':
    main()
