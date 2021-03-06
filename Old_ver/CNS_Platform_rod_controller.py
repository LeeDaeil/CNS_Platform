import matplotlib.pyplot as plt
from Interface.CNS_Platform_rod_controller_interface import Ui_Dialog as Rod_UI
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import sys
import CNS_Send_UDP
import CNS_Platform_PARA as PARA
from scipy.signal import savgol_filter

CALL_ALL = True


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

        self.make_up_list, self.boron_list = [], []
        self.make_up_count, self.boron_count = 0, 0


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
        print(self.trig_mem['TEMP_CONT'])
        # PARA.HIS_ALL__CONT['KBCDO10'][self.trig_mem['TEMP_CONT']]
        if CALL_ALL:
            self.Trend_ui.Rod_1.setGeometry(10, 70, 41, abs(PARA.HIS_ALL__CONT['KBCDO10'][self.trig_mem['TEMP_CONT']] - 228))
            self.Trend_ui.Rod_2.setGeometry(70, 70, 41, abs(PARA.HIS_ALL__CONT['KBCDO9'][self.trig_mem['TEMP_CONT']] - 228))
            self.Trend_ui.Rod_3.setGeometry(130, 70, 41, abs(PARA.HIS_ALL__CONT['KBCDO8'][self.trig_mem['TEMP_CONT']] - 228))
            self.Trend_ui.Rod_4.setGeometry(190, 70, 41, abs(PARA.HIS_ALL__CONT['KBCDO7'][self.trig_mem['TEMP_CONT']] - 228))
            self.Trend_ui.Dis_Rod_4.setText(str(PARA.HIS_ALL__CONT['KBCDO7'][self.trig_mem['TEMP_CONT']]))
            self.Trend_ui.Dis_Rod_3.setText(str(PARA.HIS_ALL__CONT['KBCDO8'][self.trig_mem['TEMP_CONT']]))
            self.Trend_ui.Dis_Rod_2.setText(str(PARA.HIS_ALL__CONT['KBCDO9'][self.trig_mem['TEMP_CONT']]))
            self.Trend_ui.Dis_Rod_1.setText(str(PARA.HIS_ALL__CONT['KBCDO10'][self.trig_mem['TEMP_CONT']]))
        else:
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
        self.rod_cond = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.rod_cond_ax = self.rod_cond.add_subplot(111)
        self.rod_cond_canv = FigureCanvasQTAgg(self.rod_cond)
        self.Trend_ui.Rod_his_cond.addWidget(self.rod_cond_canv)

        # 온도 그래프
        self.rod_temp = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.rod_temp_ax = self.rod_temp.add_subplot(111)
        self.rod_temp_canv = FigureCanvasQTAgg(self.rod_temp)
        self.Trend_ui.Rod_his_cond_temp.addWidget(self.rod_temp_canv)

        self.rod_temp_2 = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.rod_temp_ax_2 = self.rod_temp_2.add_subplot(111)
        self.rod_temp_canv_2 = FigureCanvasQTAgg(self.rod_temp_2)
        self.Trend_ui.Rod_his_cond_temp_2.addWidget(self.rod_temp_canv_2)

        # 아래 제어신호
        self.rod_fig = plt.figure(tight_layout = {'pad': 1})
        self.rod_ax = self.rod_fig.add_subplot(111)
        self.rod_canvas = FigureCanvasQTAgg(self.rod_fig)
        self.Trend_ui.Rod_his.addWidget(self.rod_canvas)

        # 아래 제어신호
        self.rod_fig_2 = plt.figure(tight_layout = {'pad': 1})
        self.rod_ax_2 = self.rod_fig_2.add_subplot(111)
        self.rod_canvas_2 = FigureCanvasQTAgg(self.rod_fig_2)
        self.Trend_ui.Rod_his_2.addWidget(self.rod_canvas_2)

    def update_rod_his_gp(self):
        try:
            temp = PARA.HIS_ALL__CONT

            self.rod_cond_ax.clear()
            self.rod_cond_ax.set_title('Reactor power')
            cns_time = temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']]
            power = temp['QPROREL'][0:self.trig_mem['TEMP_CONT']]
            self.rod_cond_ax.plot(cns_time, power, label='Reactor power')

            self.rod_cond_ax.fill_between(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                                          temp['UP_D'][0:self.trig_mem['TEMP_CONT']],
                                          temp['DOWN_D'][0:self.trig_mem['TEMP_CONT']], color='gray', alpha=0.5,
                                          label='Boundary')
            self.rod_cond_ax.plot(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                                  temp['UP_D'][0:self.trig_mem['TEMP_CONT']], color='gray', lw=1, linestyle='--', label='')
            self.rod_cond_ax.plot(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                                  temp['DOWN_D'][0:self.trig_mem['TEMP_CONT']], color='gray', lw=1, linestyle='--', label='')
            self.rod_cond_ax.legend(fontsize=10, loc=0)
            self.rod_cond_canv.draw()

            self.rod_temp_ax.clear()
            self.rod_temp_ax.set_title('Temperature')
            start_point = 725

            if self.trig_mem['TEMP_CONT'] > 725:
                self.rod_temp_ax.fill_between(temp['KCNTOMS'][start_point:self.trig_mem['TEMP_CONT']],
                                 temp['UAVLEGS'][start_point:self.trig_mem['TEMP_CONT']] + 1.3,
                                 temp['UAVLEGS'][start_point:self.trig_mem['TEMP_CONT']] - 1.3, color='gray', alpha=0.5,
                                 label='Boundary')

                self.rod_temp_ax.plot(temp['KCNTOMS'][start_point:self.trig_mem['TEMP_CONT']],
                                      temp['UAVLEGS'][start_point:self.trig_mem['TEMP_CONT']] + 1.3, color='gray', lw=1,
                                      linestyle='--', label='')
                self.rod_temp_ax.plot(temp['KCNTOMS'][start_point:self.trig_mem['TEMP_CONT']],
                                      temp['UAVLEGS'][start_point:self.trig_mem['TEMP_CONT']] - 1.3, color='gray', lw=1,
                                      linestyle='--', label='')
                self.rod_temp_ax.plot(temp['KCNTOMS'][start_point:self.trig_mem['TEMP_CONT']],
                                      temp['UAVLEGS'][start_point:self.trig_mem['TEMP_CONT']], color='black', lw=1,
                                      linestyle='--',
                                      label='Reference Temperature')

            self.rod_temp_ax.plot(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                                  temp['UAVLEGM'][0:self.trig_mem['TEMP_CONT']],
                                  color='black', label='Average Temperature')
            self.rod_temp_ax.legend(fontsize=10, loc=0)
            self.rod_temp_canv.draw()

            self.rod_temp_ax_2.clear()
            self.rod_temp_ax_2.set_title('Electric Power')
            self.rod_temp_ax_2.plot(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                                    temp['KBCDO20'][0:self.trig_mem['TEMP_CONT']],
                                    color='gray', linestyle='--', label='Load Set-point [MWe]')
            self.rod_temp_ax_2.plot(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                                    temp['KBCDO21'][0:self.trig_mem['TEMP_CONT']],
                                    color='gray', linestyle='-', label='Load Rate [MWe]')
            self.rod_temp_ax_2.plot(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                                    temp['KBCDO22'][0:self.trig_mem['TEMP_CONT']],
                                    color='black', label='Electric Power [MWe]')
            self.rod_temp_ax_2.legend(fontsize=10, loc=0)
            self.rod_temp_canv_2.draw()

            self.rod_ax.clear()
            self.rod_ax.set_title('Boron concentration')
            self.rod_ax.plot(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']],
                             temp['KBCDO16'][0:self.trig_mem['TEMP_CONT']],
                             color='black', label='Boron concentration [PPM]')
            self.rod_canvas.draw()

            self.rod_ax_2.clear()
            self.rod_ax_2.set_title('Injected boron / make-up')

            self.rod_ax_2.step(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']], temp['BOR'][0:self.trig_mem['TEMP_CONT']],
                               label='Injected boron mass', color='blue')
            self.rod_ax_2.step(temp['KCNTOMS'][0:self.trig_mem['TEMP_CONT']], temp['MAKE_UP'][0:self.trig_mem['TEMP_CONT']],
                               label='Injected make-up water mass', color='black')
            # self.rod_ax_2.set_ylabel('Accumulated mass [L]')
            self.rod_ax_2.legend(fontsize=10, loc=0)
            self.rod_canvas_2.draw()



            # self.rod_ax.clear()
            # self.rod_ax.set_title('Rod Control Signal')
            # temp = []
            # cns_time = []
            # for _ in range(len(self.mem['KSWO33']['D'])):
            #     if self.mem['KSWO33']['D'][_] == 0 and self.mem['KSWO32']['D'][_] == 0:
            #         temp.append(0)
            #         cns_time.append(self.mem['KCNTOMS']['D'][_])
            #     elif self.mem['KSWO33']['D'][_] == 1 and self.mem['KSWO32']['D'][_] == 0:
            #         temp.append(1)
            #         cns_time.append(self.mem['KCNTOMS']['D'][_])
            #     elif self.mem['KSWO33']['D'][_] == 0 and self.mem['KSWO32']['D'][_] == 1:
            #         temp.append(-1)
            #         cns_time.append(self.mem['KCNTOMS']['D'][_])
            # self.rod_ax.plot(cns_time, temp)
            # self.rod_ax.set_ylim(-1.2, 1.2)
            # # self.rod_ax.set_xlim(0, 50)
            # self.rod_ax.set_yticks([-1, 0, 1])
            # self.rod_ax.set_yticklabels(['Down', 'Stay', 'UP'])
            # self.rod_ax.grid()
            # self.rod_canvas.draw()

            # 원자로 출력 및 온도 분포 획득 Module_ROD로 부터
            #
            # self.rod_cond_ax.clear()
            # self.rod_cond_ax.set_title('Reactor Power')
            # self.rod_cond_ax.plot(self.trig_mem['Rod_His']['X'], self.trig_mem['Rod_His']['Y_pow'])
            # self.rod_cond_ax.grid()
            #
            # self.rod_cond_canv.draw()

            # # 온도 그래프
            # # 'Rod_His': {'X': [], 'Y_avg': [], 'Y_up_dead': [], 'Y_down_dead': [],
            # #             'Y_up_op': [], 'Y_down_op': [], 'Y_ax': []},
            # self.rod_temp_ax.clear()
            # self.rod_temp_ax.set_title('Average/Reference Temperature')
            # self.rod_temp_ax.plot(self.trig_mem['Rod_His']['X'], self.trig_mem['Rod_His']['Y_avg'], color='black')
            # self.rod_temp_ax.plot(self.trig_mem['Rod_His']['X'], self.trig_mem['Rod_His']['Y_up_dead'], color='gray')
            # self.rod_temp_ax.plot(self.trig_mem['Rod_His']['X'], self.trig_mem['Rod_His']['Y_down_dead'], color='gray')
            # self.rod_temp_ax.plot(self.trig_mem['Rod_His']['X'], self.trig_mem['Rod_His']['Y_up_op'], color='red')
            # self.rod_temp_ax.plot(self.trig_mem['Rod_His']['X'], self.trig_mem['Rod_His']['Y_down_op'], color='red')
            # self.rod_temp_ax.grid()
            # self.rod_temp_canv.draw()
            #
            # self.rod_temp_ax_2.clear()
            # self.rod_temp_ax_2.set_title('Axis-offset')
            # self.rod_temp_ax_2.plot(self.trig_mem['Rod_His']['X'], self.trig_mem['Rod_His']['Y_ax'], color='black')
            # self.rod_temp_ax_2.grid()
            # self.rod_temp_canv_2.draw()


        except Exception as e:
            print(self, e)
