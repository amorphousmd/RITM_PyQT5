# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TestGUIVer1.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import torch
import argparse

import tkinter as tk
from tkinter import messagebox, filedialog, ttk

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QResizeEvent, QMouseEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import cv2, imutils
from PIL import Image

from interactive_demo.canvas import CanvasImage
from interactive_demo.controller import InteractiveController
from isegm.utils import exp
from isegm.inference import utils


class Ui_Dialog(object):
    def setupUi(self, Dialog, args, model):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1114, 760)
        self.mainLbl = QtWidgets.QLabel(Dialog)
        # self.mainLbl.setGeometry(QtCore.QRect(10, 10, 961, 731))
        self.mainLbl.setText("")
        self.mainLbl.setObjectName("mainLbl")
        self.mainLbl.mousePressEvent = self.get_pos
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(990, 10, 121, 171))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadImageBtn = QtWidgets.QPushButton(self.widget)
        self.loadImageBtn.setObjectName("loadImageBtn")
        self.verticalLayout.addWidget(self.loadImageBtn)
        self.finishBtn = QtWidgets.QPushButton(self.widget)
        self.finishBtn.setObjectName("finishBtn")
        self.verticalLayout.addWidget(self.finishBtn)
        self.undoBtn = QtWidgets.QPushButton(self.widget)
        self.undoBtn.setObjectName("undoBtn")
        self.verticalLayout.addWidget(self.undoBtn)
        self.resetBtn = QtWidgets.QPushButton(self.widget)
        self.resetBtn.setObjectName("resetBtn")
        self.verticalLayout.addWidget(self.resetBtn)

        # Basic Setups
        self.limit_longest_size = 800
        self._init_state()
        self.controller = InteractiveController(model, args.device,
                                                predictor_params={'brs_mode': 'NoBRS'},
                                                update_image_callback=self._update_image)

        self._reset_predictor()
        # Functionalities
        self.loadImageBtn.clicked.connect(self.load_image)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def _init_state(self):
        self.state = {
            'zoomin_params': {
                'use_zoom_in': True,
                'fixed_crop': True,
                'skip_clicks': -1,
                'target_size': 400,
                'expansion_ratio': 1.4
            },

            'predictor_params': {
                'net_clicks_limit': 8
            },
            'brs_mode': 'NoBRS',
            'prob_thresh': 0.5,
            'lbfgs_max_iters': 20,

            'alpha_blend': 0.5,
            'click_radius': 3,
        }

    def _reset_predictor(self, *args, **kwargs):
        brs_mode = 'NoBRS'
        prob_thresh = 0.5
        net_clicks_limit = None

        zoomin_params = None

        predictor_params = {
            'brs_mode': brs_mode,
            'prob_thresh': prob_thresh,
            'zoom_in_params': zoomin_params,
            'predictor_params': {
                'net_clicks_limit': net_clicks_limit,
                'max_size': self.limit_longest_size
            },
            'brs_opt_func_params': {'min_iou_diff': 1e-3},
            'lbfgs_params': {'maxfun': 20}
        }
        self.controller.reset_predictor(predictor_params)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.loadImageBtn.setText(_translate("Dialog", "Load Image"))
        self.finishBtn.setText(_translate("Dialog", "Finish"))
        self.undoBtn.setText(_translate("Dialog", "Undo"))
        self.resetBtn.setText(_translate("Dialog", "Reset"))

    def _update_image(self, reset_canvas=False):
        image = self.controller.get_visualization(alpha_blend=self.state['alpha_blend'].get(),
                                                  click_radius=self.state['click_radius'].get())
        if self.image_on_canvas is None:
            self.image_on_canvas = CanvasImage(self.canvas_frame, self.canvas)
            self.image_on_canvas.register_click_callback(self._click_callback)

        self._set_click_dependent_widgets_state()
        if image is not None:
            self.image_on_canvas.reload_image(Image.fromarray(image), reset_canvas)

    def _click_callback(self, is_positive, x, y):
        self.controller.add_click(x, y, is_positive)

    def resizeEvent(self, event: QResizeEvent):
        self.label.adjustSize()

    def get_pos(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()
            print("Left click at ({}, {})".format(x, y))
            self._click_callback(True, x, y)
        elif event.button() == Qt.RightButton:
            x = event.x()
            y = event.y()
            print("Right click at ({}, {})".format(x, y))
            self._click_callback(False, x, y)

    def load_image(self):
        self.filename = QFileDialog.getOpenFileName(directory="C:/Users/LAPTOP/Desktop/Pics")[0]
        if not self.filename == '':
            self.image = cv2.imread(self.filename)
            self.set_image(self.image)
        else:
            print('No image chosen')

    def set_image(self, image):
        self.tmp = image
        # image = imutils.resize(image, width=1000)
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.mainLbl.setPixmap(QtGui.QPixmap.fromImage(image))
        self.mainLbl.adjustSize()



def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--checkpoint', type=str, required=False,
                        help='The path to the checkpoint. '
                             'This can be a relative path (relative to cfg.INTERACTIVE_MODELS_PATH) '
                             'or an absolute path. The file extension can be omitted.', default='coco_lvis_h18_itermask')

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
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog, args, model)
    Dialog.show()
    sys.exit(app.exec_())
