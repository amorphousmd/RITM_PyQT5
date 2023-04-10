import sys
import tkinter as tk
from tkinter import ttk
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QFrame, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import QSize
import torch
import argparse

from interactive_demo.canvas import CanvasImage
from interactive_demo.controller import InteractiveController
from isegm.utils import exp
from isegm.inference import utils



class TkinterFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.tkroot = tk.Tk()
        self.tkroot.withdraw()
        self.widget = InteractiveDemoApp(self.tkroot, args, model)
        self.widget.pack(side="top", fill="both", expand=True)

        self.tkroot.update()
        width = self.tkroot.winfo_width()
        height = self.tkroot.winfo_height()
        self.setMaximumSize(width, height)

    def closeEvent(self, event):
        self.tkroot.destroy()


class InteractiveDemoApp(ttk.Frame):
    def __init__(self, master, args, model):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)

        self.brs_modes = ['NoBRS', 'RGB-BRS', 'DistMap-BRS', 'f-BRS-A', 'f-BRS-B', 'f-BRS-C']
        self.limit_longest_size = args.limit_longest_size

        self.controller = InteractiveController(model, args.device,
                                                predictor_params={'brs_mode': 'NoBRS'},
                                                update_image_callback=self._update_image)

        self._init_state()
        self._add_menu()
        self._add_canvas()
        self._add_buttons()

        master.bind('<space>', lambda event: self.controller.finish_object())
        master.bind('a', lambda event: self.controller.partially_finish_object())

        self.state['zoomin_params']['skip_clicks'].trace(mode='w', callback=self._reset_predictor)
        self.state['zoomin_params']['target_size'].trace(mode='w', callback=self._reset_predictor)
        self.state['zoomin_params']['expansion_ratio'].trace(mode='w', callback=self._reset_predictor)
        self.state['predictor_params']['net_clicks_limit'].trace(mode='w', callback=self._change_brs_mode)
        self.state['lbfgs_max_iters'].trace(mode='w', callback=self._change_brs_mode)
        self._change_brs_mode()

    def _init_state(self):
        # define state for InteractiveDemoApp
        pass

    def _add_menu(self):
        # add menu to InteractiveDemoApp
        pass

    def _add_canvas(self):
        # add canvas to InteractiveDemoApp
        pass

    def _add_buttons(self):
        # add buttons to InteractiveDemoApp
        pass

    def _update_image(self):
        # update image
        pass

    def _reset_predictor(self, *args):
        # reset predictor
        pass

    def _change_brs_mode(self, *args):
        # change brs mode
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and geometry
        self.setWindowTitle("My PyQt5 Application")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget for the main window
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout for the central widget
        self.central_layout = QVBoxLayout(self.central_widget)

        # Create a tkinter frame to embed the InteractiveDemoApp
        self.tkinter_frame = tk.Frame(self.central_widget)

        # Add the tkinter frame to the central layout
        self.central_layout.addWidget(self.tkinter_frame)

        # Initialize the InteractiveDemoApp
        args = None  # Set your args variable here
        model = None  # Set your model variable here
        self.app = InteractiveDemoApp(self.tkinter_frame, args, model)

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

if __name__ == "__main__":
    args, cfg = parse_args()

    torch.backends.cudnn.deterministic = True
    checkpoint_path = utils.find_checkpoint(cfg.INTERACTIVE_MODELS_PATH, args.checkpoint)
    model = utils.load_is_model(checkpoint_path, args.device, cpu_dist_maps=True)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

