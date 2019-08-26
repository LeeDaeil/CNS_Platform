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
        try:
            if self.auto_mem['Abnormal_Dig_result']['Result'][-1][0] < 0.9:
                self.EDM_ui.label_4.setText('23-01(1차측 누설)')
        except Exception as e:
            pass
            #print(self, e)

    def draw_dig_his_gp(self):
        # 위 그래프
        self.dig_fig = plt.figure(figsize=(15, 15))

        self.gs = self.dig_fig.add_gridspec(1, 1)
        self.dig_ax = [self.dig_fig.add_subplot(self.gs[:, :])]
        self.dig_canv = FigureCanvasQTAgg(self.dig_fig)
        self.EDM_ui.horizontalLayout.addWidget(self.dig_canv)

    def update_dig_his_gp(self):
        [ax.clear() for ax in self.dig_ax]
        self.dig_ax[0].plot(self.auto_mem['Abnormal_Dig_result']['Result'])
        self.dig_ax[0].legend(['Normal', 'ab_21-01', 'ab_21-02', 'ab_20-01', 'ab_20-04', 'ab_15-07', 'ab_15-08', 'ab_63-04',
                               'ab_63-02', 'ab_63-03', 'ab_21-12', 'ab-19-02', 'ab_21-11', 'ab_23-03', 'ab_80-02', 'ab_60-02',
                               'ab_59-02', 'ab_23-01', 'ab_23-06', 'ab_59-01', 'ab_64-03'], loc=7)
        self.dig_ax[0].grid()
        # for _ in range(0, len(self.dig_fig)):
        #     self.dig_ax[_].plot([out[_] for out in self.auto_mem['Abnormal_Dig_result']['Result']])
        #     self.dig_ax[_].grid()
        self.dig_canv.draw()

