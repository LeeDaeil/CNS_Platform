from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import sys
import json
import numpy as np

from CNS_Platform_Base import BoardUI_Base

class AbIndicator(QWidget):
    def __init__(self, text='', prob=0.1, sw=False):
        super(AbIndicator, self).__init__()
        self.setFixedHeight(30)
        self.setFixedWidth(250)

        # Main window
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.label_1 = QLabel(text=text)
        self.label_1.setFrameShape(QFrame.Box)
        self.label_1.setLineWidth(1)
        self.label_1.setAlignment(Qt.AlignCenter)
        self.label_1.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 255, 255);')

        self.label_2 = QLabel(text=f"{prob * 100:3.2f} [%]")
        self.label_2.setFixedWidth(100)
        self.label_2.setFrameShape(QFrame.Box)
        self.label_2.setLineWidth(1)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 255, 255);')

        self.main_layout.addWidget(self.label_1)
        self.main_layout.addWidget(self.label_2)

        self.sw = sw
        self.lap = False
        self.prob = prob

        timer = QTimer(self)
        for _ in [self._blink]:
            timer.timeout.connect(_)
        timer.start(500)

    def _blink(self):
        if self.sw:
            if self.prob > 0.9:
                # Lap
                if self.lap == False:
                    self.label_2.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(144, 0, 0);'
                                               'color: rgb(255, 255, 255);')
                    self.lap = True
                else:
                    self.label_2.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 255, 255);'
                                               'color: rgb(0, 0, 0);')
                    self.lap = False

                # Hight light Box
                self.label_1.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 227, 14);')

            else:
                self.label_2.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 255, 255);'
                                           'color: rgb(0, 0, 0);')
                self.lap = False
                # Hight light Box
                self.label_1.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 255, 255);')

    def update(self, prob) -> None:
        self.prob = prob
        self.label_2.setText(f"{prob * 100:3.2f} [%]")

class BoardUI(BoardUI_Base):
    def __init__(self):
        super(BoardUI, self).__init__(title='Autonomous Abnormal Event',
                                      WindowId='AB')
        # 요소 선언 -----------------------------------------------------------------------------------------------------
        self.Ab1 = AbIndicator('Normal', 1)
        self.Ab2 = AbIndicator('Ab21-01', 0, True)
        self.Ab3 = AbIndicator('Ab21-02', 0, True)
        self.Ab4 = AbIndicator('Ab20-01', 0, True)
        self.Ab5 = AbIndicator('Ab20-04', 0, True)
        self.Ab6 = AbIndicator('Ab15-07', 0, True)
        self.Ab7 = AbIndicator('Ab15-08', 0, True)

        self.Ab8 = AbIndicator('Ab63-04', 0, True)
        self.Ab9 = AbIndicator('Ab63-02', 0, True)
        self.Ab10 = AbIndicator('Ab63-03', 0, True)
        self.Ab11 = AbIndicator('Ab21-12', 0, True)
        self.Ab12 = AbIndicator('Ab19-02', 0, True)
        self.Ab13 = AbIndicator('Ab21-11', 0, True)
        self.Ab14 = AbIndicator('Ab23-03', 0, True)

        self.Ab15 = AbIndicator('Ab80-02', 0, True)
        self.Ab16 = AbIndicator('Ab60-02', 0, True)
        self.Ab17 = AbIndicator('Ab59-02', 0, True)
        self.Ab18 = AbIndicator('Ab23-01', 0, True)
        self.Ab19 = AbIndicator('Ab23-06', 0, True)
        self.Ab20 = AbIndicator('Ab59-01', 0, True)
        self.Ab21 = AbIndicator('Ab64-03', 0, True)

        self.r1_lay = QHBoxLayout()
        self.r1_lay.addWidget(self.Ab1)
        self.r1_lay.addWidget(self.Ab2)
        self.r1_lay.addWidget(self.Ab3)
        self.r1_lay.addWidget(self.Ab4)
        self.r1_lay.addWidget(self.Ab5)
        self.r1_lay.addWidget(self.Ab6)
        self.r1_lay.addWidget(self.Ab7)

        self.r2_lay = QHBoxLayout()
        self.r2_lay.addWidget(self.Ab8)
        self.r2_lay.addWidget(self.Ab9)
        self.r2_lay.addWidget(self.Ab10)
        self.r2_lay.addWidget(self.Ab11)
        self.r2_lay.addWidget(self.Ab12)
        self.r2_lay.addWidget(self.Ab13)
        self.r2_lay.addWidget(self.Ab14)

        self.r3_lay = QHBoxLayout()
        self.r3_lay.addWidget(self.Ab15)
        self.r3_lay.addWidget(self.Ab16)
        self.r3_lay.addWidget(self.Ab17)
        self.r3_lay.addWidget(self.Ab18)
        self.r3_lay.addWidget(self.Ab19)
        self.r3_lay.addWidget(self.Ab20)
        self.r3_lay.addWidget(self.Ab21)

        # --------------------------------------------------------------------------------------------------------------
        if True:
            # add widget
            self.main_layout.addLayout(self.r1_lay)
            self.main_layout.addLayout(self.r2_lay)
            self.main_layout.addLayout(self.r3_lay)
            pass

class ABBoardUI(BoardUI):
    def __init__(self):
        super(ABBoardUI, self).__init__()
        self.show()

    def update(self, logic_mem):
        super(ABBoardUI, self).update()

        if len(logic_mem['AB_DIG']) > 1:
            self.Ab1.update(logic_mem['AB_DIG'][0])
            self.Ab2.update(logic_mem['AB_DIG'][1])
            self.Ab3.update(logic_mem['AB_DIG'][2])
            self.Ab4.update(logic_mem['AB_DIG'][3])
            self.Ab5.update(logic_mem['AB_DIG'][4])
            self.Ab6.update(logic_mem['AB_DIG'][5])
            self.Ab7.update(logic_mem['AB_DIG'][6])
            self.Ab8.update(logic_mem['AB_DIG'][7])
            self.Ab9.update(logic_mem['AB_DIG'][8])
            self.Ab10.update(logic_mem['AB_DIG'][9])
            self.Ab11.update(logic_mem['AB_DIG'][10])
            self.Ab12.update(logic_mem['AB_DIG'][11])
            self.Ab13.update(logic_mem['AB_DIG'][12])
            self.Ab14.update(logic_mem['AB_DIG'][13])
            self.Ab15.update(logic_mem['AB_DIG'][14])
            self.Ab16.update(logic_mem['AB_DIG'][15])
            self.Ab17.update(logic_mem['AB_DIG'][16])
            self.Ab18.update(logic_mem['AB_DIG'][17])
            self.Ab19.update(logic_mem['AB_DIG'][18])
            self.Ab20.update(logic_mem['AB_DIG'][19])
            self.Ab21.update(logic_mem['AB_DIG'][20])
        pass


if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI()
    # window = ABBoardUI()
    window.show()
    app.exec_()