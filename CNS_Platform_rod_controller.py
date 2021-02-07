
import CNS_Send_UDP
import CNS_Platform_PARA as PARA


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import sys
import json
import numpy as np

from CNS_Platform_Base import BoardUI_Base


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

        # 온도 그래프
        self.rod_temp = plt.figure(figsize=(20, 18), tight_layout = {'pad': 1})
        self.rod_cond_ax = self.rod_cond.add_subplot(111)
        self.rod_cond_canv = FigureCanvasQTAgg(self.rod_cond)
        self.Trend_ui.Rod_his_cond.addWidget(self.rod_cond_canv)
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


class RodPosBar(QWidget):
    def __init__(self, init_rod_pos):
        super(RodPosBar, self).__init__()
        self.setFixedHeight(228 + 30)
        self.setFixedWidth(50)
        # Main window
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.rod_pos = init_rod_pos

        self.indicator_label = QLabel(text=f'{init_rod_pos}')
        self.indicator_label.setFixedHeight(30)
        self.indicator_label.setFrameShape(QFrame.Box)
        self.indicator_label.setLineWidth(2)
        self.indicator_label.setStyleSheet('font: 9pt "HY헤드라인M"; background-color: rgb(255, 255, 255);')
        self.indicator_label.setAlignment(Qt.AlignCenter)
        #
        self.rod_indicator_label_b = QLabel()
        self.rod_indicator_label_b.setFixedHeight(self.rod_pos)
        self.rod_indicator_label_b.setStyleSheet('background-color: rgb(0, 22, 147);')
        self.rod_indicator_label_b.setFrameShape(QFrame.Box)
        self.rod_indicator_label_b.setLineWidth(2)

        self.rod_indicator_label_w = QLabel()
        # self.rod_indicator_label_w.setFixedHeight(self.rod_pos)
        self.rod_indicator_label_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rod_indicator_label_w.setStyleSheet('background-color: rgb(255, 255, 255);')
        self.rod_indicator_label_w.setFrameShape(QFrame.Box)
        self.rod_indicator_label_w.setLineWidth(2)
        #
        self.main_layout.addWidget(self.indicator_label)
        self.main_layout.addWidget(self.rod_indicator_label_b)
        self.main_layout.addWidget(self.rod_indicator_label_w)

    def update(self, rod_pos):
        super(RodPosBar, self).update()
        #
        self.indicator_label.setText(str(rod_pos))
        self.rod_indicator_label_b.setFixedHeight(rod_pos)
        self.rod_indicator_label_w.setFixedHeight(228 - rod_pos)

    def keyPressEvent(self, a) -> None:
        if a.key() == Qt.Key_Up:
            if self.rod_pos != 228:
                self.rod_pos += 1
        elif a.key() == Qt.Key_Down:
            if self.rod_pos != 0:
                self.rod_pos -= 1

        self.update(rod_pos=self.rod_pos)


class BoardUI(BoardUI_Base):
    def __init__(self):
        super(BoardUI, self).__init__(title='Autonomous Power Increase Module',
                                      WindowId='RC')

        # 요소 선언 -----------------------------------------------------------------------------------------------------
        # 1] Title
        main_layout_label = QLabel(text="Autonomous Power Increase Module")
        main_layout_label.setFixedHeight(30)
        main_layout_label.setStyleSheet("background-color: rgb(178, 206, 240);"
                                        "border-style: outset;"
                                        "border-width: 2px;"
                                        "border-color: black;"
                                        "font: bold 14px;")
        main_layout_label.setAlignment(Qt.AlignCenter)
        # 2] Top/Bottom layout
        # 2.1] Top -----------------------------------------------------------------------------------------------------
        main_lay_top_lay = QHBoxLayout()
        main_lay_top_lay.setContentsMargins(1, 1, 1, 1)
        main_lay_top_lay.setSpacing(2)
        # 2.1.1] Top 그래프
        main_lay_top_lay_gp_wid = QWidget()
        main_lay_top_lay_gp_wid_lay = QHBoxLayout()
        main_lay_top_lay_gp_wid_lay.setContentsMargins(1, 1, 1, 1)
        main_lay_top_lay_gp_wid_lay.setSpacing(0)
        self.top_fig, self.top_axs, self.top_canvas = BoardUI_Base.draw_fig()  # tight=True)
        main_lay_top_lay_gp_wid_lay.addWidget(self.top_canvas)
        main_lay_top_lay_gp_wid.setLayout(main_lay_top_lay_gp_wid_lay)

        # 2.1.2] Rod
        main_lay_top_lay_rod_lay_title = QLabel(text="Rod Position")
        main_lay_top_lay_rod_lay_title.setFixedHeight(25)
        main_lay_top_lay_rod_lay_title.setStyleSheet("background-color: rgb(178, 206, 240);"
                                                     "border-style: outset;"
                                                     "border-width: 2px;"
                                                     "border-color: black;"
                                                     "font: bold 12px;")
        main_lay_top_lay_rod_lay_title.setAlignment(Qt.AlignCenter)

        main_lay_top_lay_rod_lay = QHBoxLayout()
        self.Abank = RodPosBar(0)
        self.Bbank = RodPosBar(0)
        self.Cbank = RodPosBar(0)
        self.Dbank = RodPosBar(0)
        main_lay_top_lay_rod_lay.addWidget(self.Abank)
        main_lay_top_lay_rod_lay.addWidget(self.Bbank)
        main_lay_top_lay_rod_lay.addWidget(self.Cbank)
        main_lay_top_lay_rod_lay.addWidget(self.Dbank)

        main_lay_top_lay_rod = QVBoxLayout()
        main_lay_top_lay_rod.addWidget(main_lay_top_lay_rod_lay_title)
        main_lay_top_lay_rod.addLayout(main_lay_top_lay_rod_lay)
        # 2.1.3 ] End Pack
        main_lay_top_lay_gp_wid.setFixedHeight(228 + 30 + 30)
        main_lay_top_lay.addLayout(main_lay_top_lay_rod)
        main_lay_top_lay.addWidget(main_lay_top_lay_gp_wid)

        # 2.2] Bottom --------------------------------------------------------------------------------------------------
        main_lay_bottom_lay = QHBoxLayout()
        main_lay_bottom_lay.setContentsMargins(1, 1, 1, 1)
        main_lay_bottom_lay.setSpacing(1)

        # 2.2.1] Bottom 그래프


        self.bottom_fig, self.bottom_axs, self.bottom_canvas = BoardUI_Base.draw_fig()  # tight=True)
        main_lay_bottom_lay.addWidget(self.bottom_canvas)

        # self.update_3d_fig(self.axs[0]) <- Test용
        # --------------------------------------------------------------------------------------------------------------
        if True:
            # add widget
            self.main_layout.addWidget(main_layout_label)
            self.main_layout.addLayout(main_lay_top_lay)
            self.main_layout.addLayout(main_lay_bottom_lay)


class RCBoardUI(BoardUI):
    def __init__(self):
        super(RCBoardUI, self).__init__()
        self.show()

    def update(self, save_mem, local_mem):
        # TODO ...
        pass

if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI()
    # window = RodPosBar(0)
    window.show()
    app.exec_()