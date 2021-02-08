from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import sys
import json
import numpy as np

from CNS_Platform_Base import BoardUI_Base


class SVIndicator(QWidget):
    def __init__(self, text='', prob=0, sw=False):
        super(SVIndicator, self).__init__()
        self.setFixedHeight(25)
        self.setFixedWidth(300)

        # Main window
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.label_1 = QLabel(text=text)
        self.label_1.setFrameShape(QFrame.Box)
        self.label_1.setLineWidth(1)
        self.label_1.setAlignment(Qt.AlignCenter)
        self.label_1.setStyleSheet('font: 10pt "HY헤드라인M"; background-color: rgb(255, 255, 255);')

        self.main_layout.addWidget(self.label_1)

        self.sw = sw
        self.lap = False
        self.prob = prob

        timer = QTimer(self)
        for _ in [self._blink]:
            timer.timeout.connect(_)
        timer.start(500)

    def _blink(self):
        if self.sw:
            if self.prob == 1:
                # Hight light Box
                self.label_1.setStyleSheet('font: 10pt "HY헤드라인M"; background-color: rgb(255, 227, 14);')
            else:
                # Hight light Box
                self.label_1.setStyleSheet('font: 10pt "HY헤드라인M"; background-color: rgb(255, 255, 255);')

    def update(self, prob) -> None:
        self.prob = prob


class BoardUI(BoardUI_Base):
    def __init__(self):
        super(BoardUI, self).__init__(title='Autonomous Signal Validation',
                                      WindowId='SV')

        self._want_para = {
                           0: {'para': 'ZINST103', 'label':	'FEEDWATER PUMP OUTLET PRESS'},
                           1: {'para': 'WFWLN1', 'label':	'FEEDWATER LINE #1 FLOW (KG-SEC).'},
                           2: {'para': 'WFWLN2', 'label':	'FEEDWATER LINE #2 FLOW (KG-SEC).'},
                           3: {'para': 'WFWLN3', 'label':	'FEEDWATER LINE #3 FLOW (KG-SEC).'},
                           4: {'para': 'ZINST100', 'label':	'FEEDWATER TEMP'},
                           5: {'para': 'ZINST101', 'label':	'MAIN STEAM FLOW'},
                           6: {'para': 'ZINST85', 'label':	'STEAM LINE 3 FLOW'},
                           7: {'para': 'ZINST86', 'label':	'STEAM LINE 2 FLOW'},
                           8: {'para': 'ZINST87', 'label':	'STEAM LINE 1 FLOW'},
                           9: {'para': 'ZINST99', 'label':	'MAIN STEAM HEADER PRESSURE'},
                           10: {'para': 'UCHGUT', 'label':	'CHARGING LINE OUTLET TEMPERATURE'},
                           11: {'para': 'UCOLEG1', 'label':	'LOOP #1 COLDLEG TEMPERATURE.'},
                           12: {'para': 'UCOLEG2', 'label':	'LOOP #2 COLDLEG TEMPERATURE.'},
                           13: {'para': 'UCOLEG3', 'label':	'LOOP #3 COLDLEG TEMPERATURE.'},
                           14: {'para': 'UPRZ', 'label':	'PRZ TEMPERATURE.'},
                           15: {'para': 'UUPPPL', 'label':	'CORE OUTLET TEMPERATURE.'},
                           16: {'para': 'WNETLD', 'label':	'NET LETDOWN FLOW.'},
                           17: {'para': 'ZINST63', 'label':	'PRZ LEVEL'},
                           18: {'para': 'ZINST65', 'label':	'PRZ PRESSURE(WIDE RANGE)'},
                           19: {'para': 'ZINST79', 'label':	'LOOP 3 FLOW'},
                           20: {'para': 'ZINST80', 'label':	'LOOP 2 FLOW'},
                           21: {'para': 'ZINST81', 'label':	'LOOP 1 FLOW'},
                           22: {'para': 'ZINST70', 'label':	'SG 3 LEVEL(WIDE)'},
                           23: {'para': 'ZINST72', 'label':	'SG 1 LEVEL(WIDE)'},
                           24: {'para': 'ZINST73', 'label':	'SG 3 PRESSURE'},
                           25: {'para': 'ZINST75', 'label':	'SG 1 PRESSURE'},

                           26: {'para': '', 'label':	'-'},
                           27: {'para': '', 'label':	'-'},
        }

        # 요소 선언 -----------------------------------------------------------------------------------------------------
        self.SV_List = [SVIndicator(self._want_para[_]['label'], 0, True) for _ in range(len(self._want_para))]

        for i, sv_ in enumerate(self.SV_List):
            if i % 4 == 0:
                r_lay = QHBoxLayout()
                self.main_layout.addLayout(r_lay)
            r_lay.addWidget(sv_)


class SVBoardUI(BoardUI):
    def __init__(self):
        super(SVBoardUI, self).__init__()
        self.show()

    def update(self, logic_mem):
        super(SVBoardUI, self).update()

        if len(logic_mem['SV_RES']) > 1:
            for i, val in enumerate(logic_mem['SV_RES']):
                self.SV_List[i].update(val)     # [1, 0, 0, 0 ... ]


if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI()
    # window = ABBoardUI()
    window.show()
    app.exec_()