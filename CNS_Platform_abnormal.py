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
        self.label_1.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 255, 255);')

        self.label_2 = QLabel(text=f"{prob * 100:3.1f}[%]")
        self.label_2.setFixedWidth(70)
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
        self.Ab_List = []
        self.Ab_dict_label = ['Normal',
                              'Ab21-01\n가압기 압력 채널 고장 (고)',
                              'Ab21-02\n가압기 압력 채널 고장 (저)',
                              'Ab20-01\n가압기 수위 채널 고장 (고)',
                              'Ab20-04\n가압기 수위 채널 고장 (저)',
                              'Ab15-07\n증기발생기 수위 채널 고장 (고)',
                              'Ab15-08\n증기발생기 수위 채널 고장 (저)',
                              'Ab63-04\n제어봉 낙하',
                              'Ab63-02\n제어봉의 계속적인 삽입',
                              'Ab63-03\n제어봉의 계속적인 인출',
                              'Ab21-12\n가압기 PORV 고장 (열림)',
                              'Ab19-02\n가압기 안전 밸브 고장 (열림)',
                              'Ab21-11\n가압기 살수 밸브 고장 (열림)',
                              'Ab23-03\n1차측 RCS 누설 (Leak)',
                              'Ab80-02\n주급수 펌프 2/3 대 정지',
                              'Ab60-02\n재생열 교환기 전단 파열',
                              'Ab59-02\n충전수 유량조절밸브 전단 누설 (Leak)',
                              'Ab23-01\n1차측 CVCS 계통 누설 (Leak)',
                              'Ab23-06\n증기발생기 전열관 누설 (Leak)',
                              'Ab59-01\n충전수 유량조절밸브 후단 누설 (Leak)',
                              'Ab64-03\n주증기관 밸브 고장 (닫힘)',
                              ]
        # Ab indicator 생성
        for label_ in self.Ab_dict_label:
            if label_ == 'Normal':
                self.Ab_List.append(AbIndicator(label_, 1, False))
            else:
                self.Ab_List.append(AbIndicator(label_, 0, True))
        # Ab indicators Layout 에 등록
        for i, Abindicator_ in enumerate(self.Ab_List):
            if i % 3 == 0:
                r_lay = QHBoxLayout()
                self.main_layout.addLayout(r_lay)

            r_lay.addWidget(Abindicator_)


class ABBoardUI(BoardUI):
    def __init__(self):
        super(ABBoardUI, self).__init__()
        self.show()

    def update(self, logic_mem):
        super(ABBoardUI, self).update()

        if len(logic_mem['AB_DIG']) > 1:
            for i, one_abindicicator in enumerate(self.Ab_List):
                one_abindicicator.update(logic_mem['AB_DIG'][i])


if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI()
    # window = ABBoardUI()
    window.show()
    app.exec_()