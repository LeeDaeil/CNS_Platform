import matplotlib.pyplot as plt
from Interface.CNS_Platform_rod_controller_interface import Ui_Dialog as Rod_UI
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import sys
import CNS_Send_UDP


class rod_controller_interface(QDialog):
    def __init__(self, mem=None, trig_mem=None):
        super().__init__()
        # ===============================================================
        # 메모리 호출 부분 없으면 Test
        if mem != None:
            self.mem = mem
            self.trig_mem = trig_mem
        else:
            print('TEST_interface')
        # ===============================================================
        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t') # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_UDP.CNS_Send_Signal(self.cns_ip, int(self.cns_port))
        # ===============================================================
        self.Trend_ui = Rod_UI()
        self.Trend_ui.setupUi(self)
        self.show()
        # ===============================================================
        # rod gp
        self.draw_rod_his_gp()
        # ===============================================================
        # rod control
        self.Trend_ui.rodup.clicked.connect(self.rod_up)
        self.Trend_ui.roddown.clicked.connect(self.rod_down)
        # ===============================================================

        timer = QtCore.QTimer(self)
        for _ in [self.update_window, self.update_rod_his_gp]:
            timer.timeout.connect(_)
        timer.start(600)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def rod_up(self):
        self.CNS_udp._send_control_signal(['KSWO33', 'KSWO32'], [1, 0])

    def rod_down(self):
        self.CNS_udp._send_control_signal(['KSWO33', 'KSWO32'], [0, 1])

    def update_window(self):
        self.Trend_ui.Rod_1.setGeometry(10, 70, 41, abs(self.mem['KBCDO10']['V'] - 228))
        self.Trend_ui.Rod_2.setGeometry(70, 70, 41, abs(self.mem['KBCDO9']['V'] - 228))
        self.Trend_ui.Rod_3.setGeometry(130, 70, 41, abs(self.mem['KBCDO8']['V'] - 228))
        self.Trend_ui.Rod_4.setGeometry(190, 70, 41, abs(self.mem['KBCDO7']['V'] - 228))
        self.Trend_ui.Dis_Rod_4.setText(str(self.mem['KBCDO7']['V']))
        self.Trend_ui.Dis_Rod_3.setText(str(self.mem['KBCDO8']['V']))
        self.Trend_ui.Dis_Rod_2.setText(str(self.mem['KBCDO9']['V']))
        self.Trend_ui.Dis_Rod_1.setText(str(self.mem['KBCDO10']['V']))

        # 아래 자율/수동 패널
        if self.trig_mem['Auto'] == True:
            self.Trend_ui.label_5.setStyleSheet('background-color: rgb(255, 144, 146);'
                                                'border-style: outset;'
                                                'border-width: 0.5px;'
                                                'border-color: black;'
                                                'font: bold 14px;')
            self.Trend_ui.label_3.setStyleSheet('background-color: rgb(255, 255, 255);'
                                                'border-style: outset;'
                                                'border-width: 0.5px;'
                                                'border-color: black;'
                                                'font: bold 14px;')
        else:
            self.Trend_ui.label_5.setStyleSheet('background-color: rgb(255, 255, 255);'
                                                'border-style: outset;'
                                                'border-width: 0.5px;'
                                                'border-color: black;'
                                                'font: bold 14px;')
            self.Trend_ui.label_3.setStyleSheet('background-color: rgb(255, 144, 146);'
                                                'border-style: outset;'
                                                'border-width: 0.5px;'
                                                'border-color: black;'
                                                'font: bold 14px;')

    def draw_rod_his_gp(self):
        # 위 그래프
        self.rod_cond = plt.figure()
        self.rod_cond_ax = self.rod_cond.add_subplot(111)
        self.rod_cond_canv = FigureCanvasQTAgg(self.rod_cond)
        self.Trend_ui.Rod_his_cond.addWidget(self.rod_cond_canv)

        # 아래 제어신호
        self.rod_fig = plt.figure()
        self.rod_ax = self.rod_fig.add_subplot(111)
        self.rod_canvas = FigureCanvasQTAgg(self.rod_fig)
        self.Trend_ui.Rod_his.addWidget(self.rod_canvas)

    def update_rod_his_gp(self):
        try:
            self.rod_ax.clear()
            temp = []
            cns_time = []
            for _ in range(len(self.mem['KSWO33']['D'])):
                if self.mem['KSWO33']['D'][_] == 0 and self.mem['KSWO32']['D'][_] == 0:
                    temp.append(0)
                    cns_time.append(self.mem['KCNTOMS']['D'][_] / 5)
                elif self.mem['KSWO33']['D'][_] == 1 and self.mem['KSWO32']['D'][_] == 0:
                    temp.append(1)
                    cns_time.append(self.mem['KCNTOMS']['D'][_] / 5)
                elif self.mem['KSWO33']['D'][_] == 0 and self.mem['KSWO32']['D'][_] == 1:
                    temp.append(-1)
                    cns_time.append(self.mem['KCNTOMS']['D'][_] / 5)
            self.rod_ax.plot(cns_time, temp)
            self.rod_ax.set_ylim(-1.2, 1.2)
            # self.rod_ax.set_xlim(0, 50)
            self.rod_ax.set_yticks([-1, 0, 1])
            self.rod_ax.set_yticklabels(['Down', 'Stay', 'UP'])
            self.rod_ax.grid()
            self.rod_canvas.draw()

            # 여기서 알아서 계산해야 할 듯!
            ##
            # self.rod_cond_ax.clear()
            # rod_cond_time = self.auto_mem['Start_up_operation_his']['time']
            # self.rod_cond_ax.plot(rod_cond_time, self.auto_mem['Start_up_operation_his']['power'])
            # self.rod_cond_ax.plot(rod_cond_time, self.auto_mem['Start_up_operation_his']['up_cond'])
            # self.rod_cond_ax.plot(rod_cond_time, self.auto_mem['Start_up_operation_his']['low_cond'])
            # self.rod_cond_ax.grid()

            self.rod_cond_canv.draw()
        except Exception as e:
            print(self, e)
