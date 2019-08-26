import matplotlib.pyplot as plt
from Interface.A_Event_Diagnosis_Module import Ui_Dialog as EDM_UI
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import sys
import CNS_Send_UDP

class sub_event_window(QDialog):
    def __init__(self, mem=None, auto_mem = None, strage_mem=None):
        super().__init__()
        # ===============================================================
        # 메모리 호출 부분 없으면 Test
        if mem != None:
            self.mem = mem
            self.auto_mem = auto_mem
            self.strage_mem = strage_mem
        else:
            print('TEST_interface')\

        self.init_UI()
        self.show()

    def init_UI(self):
        ##
        self.EDM_ui =EDM_UI()
        self.EDM_ui.setupUi(self)
        # ===============================================================
        # draw dig
        self.draw_dig_his_gp()

        timer = QtCore.QTimer(self)
        for _ in [self.update_window, self.update_dig_his_gp]:
            timer.timeout.connect(_)
        timer.start(500)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)

    def update_window(self):
        # 비정상 확률 등 라벨을 여기에 표기
        pass

    def draw_dig_his_gp(self):
        # 위 그래프
        self.dig_fig = plt.figure()
        self.dig_fig_ax = self.dig_fig.add_subplot(111)
        self.dig_canv = FigureCanvasQTAgg(self.dig_fig)
        self.EDM_ui.horizontalLayout.addWidget(self.dig_canv)

    def update_dig_his_gp(self):
        self.dig_fig_ax.clear()
        self.dig_fig_ax.plot(self.auto_mem['Abnormal_Dig_result']['Result'])
        self.dig_fig_ax.grid()
        self.dig_canv.draw()

