import matplotlib.pyplot as plt
from Interface.Trend_window import Ui_Dialog as Rod_UI
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import sys
import CNS_Send_UDP

class sub_tren_window(QDialog):
    def __init__(self, mem=None):
        super().__init__()
        # ===============================================================
        # 메모리 호출 부분 없으면 Test
        if mem != None:
            self.mem = mem
        else:
            print('TEST_interface')
        # ===============================================================
        # CNS 정보 읽기
        with open('pro.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t') # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_UDP.CNS_Send_Signal(self.cns_ip, int(self.cns_port))
        # ===============================================================
        self.Trend_ui = Rod_UI()
        self.Trend_ui.setupUi(self)
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
        timer.start(500)

        self.show()

    def rod_up(self):
        self.CNS_udp._send_control_signal(['KSWO33', 'KSWO32'], [1, 0])

    def rod_down(self):
        self.CNS_udp._send_control_signal(['KSWO33', 'KSWO32'], [0, 1])

    def update_window(self):
        self.Trend_ui.Rod_1.setGeometry(10, 80, 41, abs(self.mem['KBCDO10']['V'] - 228))
        self.Trend_ui.Rod_2.setGeometry(70, 80, 41, abs(self.mem['KBCDO9']['V'] - 228))
        self.Trend_ui.Rod_3.setGeometry(130, 80, 41, abs(self.mem['KBCDO8']['V'] - 228))
        self.Trend_ui.Rod_4.setGeometry(190, 80, 41, abs(self.mem['KBCDO7']['V'] - 228))
        self.Trend_ui.Dis_Rod_4.setText(str(self.mem['KBCDO7']['V']))
        self.Trend_ui.Dis_Rod_3.setText(str(self.mem['KBCDO8']['V']))
        self.Trend_ui.Dis_Rod_2.setText(str(self.mem['KBCDO9']['V']))
        self.Trend_ui.Dis_Rod_1.setText(str(self.mem['KBCDO10']['V']))

    def draw_rod_his_gp(self):
        self.rod_fig = plt.figure()
        self.rod_ax = self.rod_fig.add_subplot(111)
        self.rod_canvas = FigureCanvasQTAgg(self.rod_fig)
        self.Trend_ui.Rod_his.addWidget(self.rod_canvas)

    def update_rod_his_gp(self):
        self.rod_ax.clear()
        temp = []
        for _ in range(len(self.mem['KSWO33']['L'])):
            if self.mem['KSWO33']['L'][_] == 0 and self.mem['KSWO32']['L'][_] == 0:
                temp.append(0)
            elif self.mem['KSWO33']['L'][_] == 1 and self.mem['KSWO32']['L'][_] == 0:
                temp.append(1)
            elif self.mem['KSWO33']['L'][_] == 0 and self.mem['KSWO32']['L'][_] == 1:
                temp.append(-1)
        self.rod_ax.plot(temp)
        self.rod_ax.set_ylim(-1.2, 1.2)
        self.rod_ax.set_xlim(len(self.mem['KSWO33']['L']) - 100, len(self.mem['KSWO33']['L']))
        self.rod_ax.set_yticks([-1, 0, 1])
        self.rod_ax.set_yticklabels(['Down', 'Stay', 'UP'])
        self.rod_ax.grid()
        self.rod_canvas.draw()
