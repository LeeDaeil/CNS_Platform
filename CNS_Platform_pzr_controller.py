import matplotlib.pyplot as plt
from Interface.CNS_Platform_PZR_controller_interface import Ui_Form as PZR_UI
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import sys
import CNS_Send_UDP


class pzr_controller_interface(QDialog):
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
        self.Trend_ui = PZR_UI()
        self.Trend_ui.setupUi(self)
        self.show()
        # ===============================================================
        # pzr gp
        self.draw_pzr_his_gp()
        # ===============================================================
        timer = QtCore.QTimer(self)
        for _ in [self.update_window, self.update_pzr_his_gp]:
            timer.timeout.connect(_)
        timer.start(600)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def update_window(self):
        try:
            self.Trend_ui.D_1.setText('%3.2f kg/cm^2' % self.mem['ZINST58']['V'])
            self.Trend_ui.D_2.setText('{} %'.format(self.mem['ZINST63']['V']))
            self.Trend_ui.D_3.setText('%3.2f' % (self.mem['UPRZ']['V']) + ' ℃')
        except Exception as e:
            print(self, e)
        pass

    def draw_pzr_his_gp(self):
        # 위 그래프
        self.pzr_press = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.pzr_press_ax = self.pzr_press.add_subplot(111)
        self.pzr_press_canv = FigureCanvasQTAgg(self.pzr_press)
        self.Trend_ui.PZR_his_pr.addWidget(self.pzr_press_canv)

        self.pzr_level = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.pzr_level_ax = self.pzr_level.add_subplot(111)
        self.pzr_level_canv = FigureCanvasQTAgg(self.pzr_level)
        self.Trend_ui.PZR_his_lv.addWidget(self.pzr_level_canv)

        self.pzr_temp = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.pzr_temp_ax = self.pzr_temp.add_subplot(111)
        self.pzr_temp_canv = FigureCanvasQTAgg(self.pzr_temp)
        self.Trend_ui.PZR_his_temp.addWidget(self.pzr_temp_canv)

        self.pzr_valve = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.pzr_valve_ax = self.pzr_valve.add_subplot(111)
        self.pzr_valve_canv = FigureCanvasQTAgg(self.pzr_valve)
        self.Trend_ui.PZR_his_valve.addWidget(self.pzr_valve_canv)

        self.pzr_valve_2 = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.pzr_valve_2_ax = self.pzr_valve_2.add_subplot(111)
        self.pzr_valve_2_canv = FigureCanvasQTAgg(self.pzr_valve_2)
        self.Trend_ui.PZR_his_valve_2.addWidget(self.pzr_valve_2_canv)

        self.clean_gp_list = [self.pzr_press_ax, self.pzr_level_ax, self.pzr_temp_ax,
                              self.pzr_valve_ax, self.pzr_valve_2_ax]
        self.draw_gp_list = [self.pzr_press_canv, self.pzr_level_canv, self.pzr_temp_canv,
                             self.pzr_valve_canv, self.pzr_valve_2_canv]

    def update_pzr_his_gp(self):
        try:
            [_.clear() for _ in self.clean_gp_list]

            self.pzr_press_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_pre'])
            self.pzr_press_ax.legend(['PZR Pressure', 'High limit', 'Low limit'], fontsize=7, loc=2)
            self.pzr_press_ax.set_yticks([20, 25, 30])
            self.pzr_press_ax.set_yticklabels(['20\nkg/cm^2', '25\nkg/cm^2', '30\nkg/cm^2'], fontsize=7)
            self.pzr_press_ax.grid()

            self.pzr_level_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_lv'])
            self.pzr_level_ax.legend(['Pressurizer Level'], fontsize=7, loc=2)
            self.pzr_level_ax.set_yticks([0, 100])
            self.pzr_level_ax.set_yticklabels(['0%', '100%'], fontsize=7)
            self.pzr_level_ax.set_ylim(-5, 105)
            self.pzr_level_ax.grid()

            self.pzr_temp_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_temp'])
            self.pzr_temp_ax.legend(['Pressurizer Temperature'], fontsize=7, loc=2)
            self.pzr_temp_ax.set_yticks([60, 80, 100, 120, 140, 160, 180, 200])
            self.pzr_temp_ax.set_yticklabels(['60℃', '80℃', '100℃', '120℃', '140℃', '160℃', '180℃', '200℃'], fontsize=7)
            self.pzr_temp_ax.set_ylim(50, 210)
            self.pzr_temp_ax.grid()

            self.pzr_valve_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_val'])
            self.pzr_valve_ax.legend(['FV-122', 'HV-142'], fontsize=7, loc=2)
            self.pzr_valve_ax.set_yticks([0, 1])
            self.pzr_valve_ax.set_yticklabels(['0%', '100%'], fontsize=7)
            self.pzr_valve_ax.set_ylim(-0.2, 1.2)
            self.pzr_valve_ax.grid()

            self.pzr_valve_2_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_het'])
            self.pzr_valve_2_ax.legend(['Backup', 'Proportional'], fontsize=7, loc=2)
            self.pzr_valve_2_ax.set_yticks([0, 1])
            self.pzr_valve_2_ax.set_yticklabels(['Off', 'On'], fontsize=7)
            self.pzr_valve_2_ax.set_ylim(-0.2, 1.2)
            self.pzr_valve_2_ax.grid()
            [_.draw() for _ in self.draw_gp_list]

        except Exception as e:
            print(self, e)



