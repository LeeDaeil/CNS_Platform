import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QPushButton
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import sys

from Interface.CNS_Platform_signal_validation_interface import Ui_Form


class DisPushButton(QPushButton):
    def __init__(self, para='', cpara='', label='', orgin_val=0, predcit_val=0, threshold=0, scaled_=0, min_=0, parent=None):
        super(DisPushButton, self).__init__(parent)
        self.para = para
        self.cpara = cpara
        self.label = label
        self.orgin_val = orgin_val
        self.predcit_val = predcit_val
        self.threshold = threshold
        self.scaled_ = scaled_
        self.min_ = min_
        self.setText(f"{self.para}\t\t\t\t[{self.orgin_val}:{self.predcit_val}]\n{self.label}")
        self.setStyleSheet('text-align:left;')

    def update_label(self, orgin_val, predcit_val):
        self.orgin_val = (orgin_val * self.scaled_) + self.min_
        self.predcit_val = (predcit_val * self.scaled_) + self.min_
        self.setText(f"{self.para}\t\t\t\t[{self.orgin_val}:{self.predcit_val}]\n{self.label}")

        if (self.predcit_val - self.orgin_val) ** 2 > self.threshold:
            self.setStyleSheet('text-align:left; background-color: rgb(255, 46, 46); color: rgb(255, 255, 255);')
        else:
            self.setStyleSheet('text-align:left; background-color: rgb(222, 222, 222); color: rgb(0, 0, 0);')


class CNSSignalValidation(QDialog):
    def __init__(self, mem=None):
        super().__init__()
        # ===============================================================
        # 메모리 호출 부분 없으면 Test
        if mem != None:
            self.mem = mem
        else:
            print('TEST_interface')
        # ===============================================================
        self.Trend_ui = Ui_Form()
        self.Trend_ui.setupUi(self)
        # ===============================================================
        self._init_want_see_para()
        self._init_add_button()
        # ===============================================================
        timer = QtCore.QTimer(self)
        for _ in [self._update_button_label]: #, self.update_pzr_his_gp]:
            timer.timeout.connect(_)
        timer.start(600)

        # print(self.Trend_ui._area_para.setMaximumHeight(100))

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def _init_want_see_para(self):
        self.threshold = [0.011581499203325669, 0.009462367390260244, 0.008903015480589159, 0.009594334339569006,
                          0.031215020667924767, 0.010818916559719643, 0.01049919201077266, 0.01062811011351488,
                          0.010651478620771508, 0.011562519033165936, 0.035823854381993835, 0.039710045714257534,
                          0.033809111781334084, 0.04924519916104178, 0.04715594067619352, 0.042831757003614385,
                          0.008778805078996987, 0.014718878351330346, 0.02059897081470507, 0.027989265704257082,
                          0.0274660154968856, 0.025115614397052698, 0.03167101131485395, 0.02955934155605648,
                          0.06220589578881775, 0.05572199208638379]
        self.scaled_ = [0.009794810683373954, 0.0015875145937245168, 0.0014017518129709815, 0.0015344235265146954,
                         0.005229481258597902, 0.008697168475346179, 0.0016075971500907969, 0.0016058463231662034,
                         0.0016326269982349195, 0.011834906487144062, 0.0037432383840962993, 0.0038263001850210097,
                         0.0031616450336628328, 0.00411113570401977, 0.0036477982147248788, 0.003927595218515628,
                         0.15150987923938053, 0.01505669960580629, 0.005976737589021353, 0.007963375324087318,
                         0.008197676972159777, 0.008297331913693513, 0.01044119112473039, 0.010333766924915612,
                         0.019495164142568775, 0.01990491776327256]
        self.min_ = [-0.00774561896105074, 0.0, 0.0, 0.0, -0.38887620136612644, -0.0013052645044564313, 0.0,
                      4.119824652031165e-05, 4.204862621976588e-05, -0.010147839757140825, -0.23403483119231308,
                      -0.3001687776465312, -0.08125329450654223, -0.39837093460966233, -0.4886151018948289,
                      -0.46560482616951726, 0.0, 0.0, -0.08979128731506154, 0.0, 0.0, 0.0,
                     -0.07800455260683058, -0.07788313543819131, -0.6562424371528104, -0.7116609969480101]

        self._want_para = {
                            0:{'para': 'ZINST103', 'label':	'FEEDWATER PUMP OUTLET PRESS'},
                            1:{'para': 'WFWLN1', 'label':	'FEEDWATER LINE #1 FLOW (KG-SEC).'},
                            2:{'para': 'WFWLN2', 'label':	'FEEDWATER LINE #2 FLOW (KG-SEC).'},
                            3:{'para': 'WFWLN3', 'label':	'FEEDWATER LINE #3 FLOW (KG-SEC).'},
                            4:{'para': 'ZINST100', 'label':	'FEEDWATER TEMP'},
                            5:{'para': 'ZINST101', 'label':	'MAIN STEAM FLOW'},
                            6:{'para': 'ZINST85', 'label':	'STEAM LINE 3 FLOW'},
                            7:{'para': 'ZINST86', 'label':	'STEAM LINE 2 FLOW'},
                            8:{'para': 'ZINST87', 'label':	'STEAM LINE 1 FLOW'},
                            9:{'para': 'ZINST99', 'label':	'MAIN STEAM HEADER PRESSURE'},
                            10:{'para': 'UCHGUT', 'label':	'CHARGING LINE OUTLET TEMPERATURE'},
                            11:{'para': 'UCOLEG1', 'label':	'LOOP #1 COLDLEG TEMPERATURE.'},
                            12:{'para': 'UCOLEG2', 'label':	'LOOP #2 COLDLEG TEMPERATURE.'},
                            13:{'para': 'UCOLEG3', 'label':	'LOOP #3 COLDLEG TEMPERATURE.'},
                            14:{'para': 'UPRZ', 'label':	'PRZ TEMPERATURE.'},
                            15:{'para': 'UUPPPL', 'label':	'CORE OUTLET TEMPERATURE.'},
                            16:{'para': 'WNETLD', 'label':	'NET LETDOWN FLOW.'},
                            17:{'para': 'ZINST63', 'label':	'PRZ LEVEL'},
                            18:{'para': 'ZINST65', 'label':	'PRZ PRESSURE(WIDE RANGE)'},
                            19:{'para': 'ZINST79', 'label':	'LOOP 3 FLOW'},
                            20:{'para': 'ZINST80', 'label':	'LOOP 2 FLOW'},
                            21:{'para': 'ZINST81', 'label':	'LOOP 1 FLOW'},
                            22:{'para': 'ZINST70', 'label':	'SG 3 LEVEL(WIDE)'},
                            23:{'para': 'ZINST72', 'label':	'SG 1 LEVEL(WIDE)'},
                            24:{'para': 'ZINST73', 'label':	'SG 3 PRESSURE'},
                            25:{'para': 'ZINST75', 'label':	'SG 1 PRESSURE'},
        }

        for i in range(len(self._want_para)):
            self._want_para[i]['Thre'] = self.threshold[i]
            self._want_para[i]['scaled_'] = self.scaled_[i]
            self._want_para[i]['min_'] = self.min_[i]

    def _init_add_button(self):
        nub = 0
        for i in range(100):
            if nub >= len(self._want_para):
                # self.Trend_ui._area_para.setMaximumHeight(24 * i)
                self.Trend_ui._area_para.setMaximumHeight(35 * i)
                break
            for j in range(4):
                if nub < len(self._want_para):
                    botton = DisPushButton(para=self._want_para[nub]['para'],
                                           cpara=f"c{self._want_para[nub]['para']}",
                                           label=self._want_para[nub]['label'],
                                           orgin_val=0,
                                           predcit_val=0,
                                           threshold=self._want_para[nub]['Thre'],
                                           scaled_=self._want_para[nub]['scaled_'],
                                           min_=self._want_para[nub]['min_'],
                                           parent=self)

                    botton.clicked.connect(partial(self._call_print,
                                                   para=self._want_para[nub]['para'],
                                                   label=self._want_para[nub]['label'],
                                                   thre=self._want_para[nub]['Thre'],))
                    self.Trend_ui._area_para_grid.addWidget(botton, i, j)
                    nub += 1
                else:
                    break
        pass

    def _call_print(self, para, label, thre):
        print(para, label, thre)

    def _update_button_label(self):
        get_last_nub = len(self.mem['cINIT']) - 1
        if get_last_nub != -1:
            for child in self.Trend_ui._area_para.children():
                if child.isWidgetType():    # True 는 버튼
                    child.update_label(orgin_val=self.mem[child.para][get_last_nub * 5],
                                       predcit_val=self.mem[child.cpara][get_last_nub * 5])
        pass

    # def _update_window(self):
    #     try:
    #         self.Trend_ui.D_1.setText('%3.2f kg/cm^2' % self.mem['ZINST58']['V'])
    #         self.Trend_ui.D_2.setText('{} %'.format(self.mem['ZINST63']['V']))
    #         self.Trend_ui.D_3.setText('%3.2f' % (self.mem['UPRZ']['V']) + ' ℃')
    #     except Exception as e:
    #         print(self, e)
    #     pass
    #
    # def draw_pzr_his_gp(self):
    #     # 위 그래프
    #     self.pzr_press = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
    #     self.pzr_press_ax = self.pzr_press.add_subplot(111)
    #     self.pzr_press_canv = FigureCanvasQTAgg(self.pzr_press)
    #     self.Trend_ui.PZR_his_pr.addWidget(self.pzr_press_canv)
    #
    #     self.pzr_level = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
    #     self.pzr_level_ax = self.pzr_level.add_subplot(111)
    #     self.pzr_level_canv = FigureCanvasQTAgg(self.pzr_level)
    #     self.Trend_ui.PZR_his_lv.addWidget(self.pzr_level_canv)
    #
    #     self.pzr_temp = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
    #     self.pzr_temp_ax = self.pzr_temp.add_subplot(111)
    #     self.pzr_temp_canv = FigureCanvasQTAgg(self.pzr_temp)
    #     self.Trend_ui.PZR_his_temp.addWidget(self.pzr_temp_canv)
    #
    #     self.pzr_valve = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
    #     self.pzr_valve_ax = self.pzr_valve.add_subplot(111)
    #     self.pzr_valve_canv = FigureCanvasQTAgg(self.pzr_valve)
    #     self.Trend_ui.PZR_his_valve.addWidget(self.pzr_valve_canv)
    #
    #     self.pzr_valve_2 = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
    #     self.pzr_valve_2_ax = self.pzr_valve_2.add_subplot(111)
    #     self.pzr_valve_2_canv = FigureCanvasQTAgg(self.pzr_valve_2)
    #     self.Trend_ui.PZR_his_valve_2.addWidget(self.pzr_valve_2_canv)
    #
    #     self.clean_gp_list = [self.pzr_press_ax, self.pzr_level_ax, self.pzr_temp_ax,
    #                           self.pzr_valve_ax, self.pzr_valve_2_ax]
    #     self.draw_gp_list = [self.pzr_press_canv, self.pzr_level_canv, self.pzr_temp_canv,
    #                          self.pzr_valve_canv, self.pzr_valve_2_canv]
    #
    # def update_pzr_his_gp(self):
    #     try:
    #         [_.clear() for _ in self.clean_gp_list]
    #
    #         self.pzr_press_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_pre'])
    #         self.pzr_press_ax.legend(['PZR Pressure', 'High limit', 'Low limit'], fontsize=7, loc=2)
    #         self.pzr_press_ax.set_yticks([20, 25, 30])
    #         self.pzr_press_ax.set_yticklabels(['20\nkg/cm^2', '25\nkg/cm^2', '30\nkg/cm^2'], fontsize=7)
    #         self.pzr_press_ax.grid()
    #
    #         self.pzr_level_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_lv'])
    #         self.pzr_level_ax.legend(['Pressurizer Level'], fontsize=7, loc=2)
    #         self.pzr_level_ax.set_yticks([0, 100])
    #         self.pzr_level_ax.set_yticklabels(['0%', '100%'], fontsize=7)
    #         self.pzr_level_ax.set_ylim(-5, 105)
    #         self.pzr_level_ax.grid()
    #
    #         self.pzr_temp_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_temp'])
    #         self.pzr_temp_ax.legend(['Pressurizer Temperature'], fontsize=7, loc=2)
    #         self.pzr_temp_ax.set_yticks([60, 80, 100, 120, 140, 160, 180, 200])
    #         self.pzr_temp_ax.set_yticklabels(['60℃', '80℃', '100℃', '120℃', '140℃', '160℃', '180℃', '200℃'], fontsize=7)
    #         self.pzr_temp_ax.set_ylim(50, 210)
    #         self.pzr_temp_ax.grid()
    #
    #         self.pzr_valve_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_val'])
    #         self.pzr_valve_ax.legend(['FV-122', 'HV-142'], fontsize=7, loc=2)
    #         self.pzr_valve_ax.set_yticks([0, 1])
    #         self.pzr_valve_ax.set_yticklabels(['0%', '100%'], fontsize=7)
    #         self.pzr_valve_ax.set_ylim(-0.2, 1.2)
    #         self.pzr_valve_ax.grid()
    #
    #         self.pzr_valve_2_ax.plot(self.trig_mem['PZR_His']['X'], self.trig_mem['PZR_His']['Y_het'])
    #         self.pzr_valve_2_ax.legend(['Backup', 'Proportional'], fontsize=7, loc=2)
    #         self.pzr_valve_2_ax.set_yticks([0, 1])
    #         self.pzr_valve_2_ax.set_yticklabels(['Off', 'On'], fontsize=7)
    #         self.pzr_valve_2_ax.set_ylim(-0.2, 1.2)
    #         self.pzr_valve_2_ax.grid()
    #         [_.draw() for _ in self.draw_gp_list]
    #
    #     except Exception as e:
    #         print(self, e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CNSSignalValidation(mem=None)
    sys.exit(app.exec_())