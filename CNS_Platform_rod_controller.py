
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

@ticker.FuncFormatter
def major_formatter_time(time, pos):
    time = int(time/300)
    return f"{time}[Min]"

@ticker.FuncFormatter
def major_formatter_reactor_power(power, pos):
    return f"{power*100:.1f}[%]"

@ticker.FuncFormatter
def major_formatter_temp(temp, pos):
    return f"{int(temp)}[℃]"

@ticker.FuncFormatter
def major_formatter_mwe(Mwe, pos):
    return f"{int(Mwe)}[MWe]"

@ticker.FuncFormatter
def major_formatter_ppm(ppm, pos):
    return f"{int(ppm)}[PPM]"

@ticker.FuncFormatter
def major_formatter_liter(l, pos):
    return f"{int(l)}[L]"


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

        self.indicator_label = QLabel(text=f'{228 - init_rod_pos}')
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
        self.indicator_label.setText(str(228 - rod_pos))
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

        self.top_fig = plt.Figure(tight_layout=True)

        gs = GridSpec(1, 1, figure=self.top_fig)
        self.top_axs = [
            self.top_fig.add_subplot(gs[:, :])
        ]
        self.top_fig.canvas.draw()
        self.top_canvas = FigureCanvasQTAgg(self.top_fig)

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

        self.bottom_fig = plt.Figure(tight_layout=True)

        gs = GridSpec(3, 2, figure=self.bottom_fig)
        self.bottom_axs = [
            self.bottom_fig.add_subplot(gs[0:2, 0]),
            self.bottom_fig.add_subplot(gs[0:2, 1]),
            self.bottom_fig.add_subplot(gs[2, 0]),
            self.bottom_fig.add_subplot(gs[2, 1]),
        ]
        self.bottom_fig.canvas.draw()
        self.bottom_canvas = FigureCanvasQTAgg(self.bottom_fig)

        main_lay_bottom_lay.addWidget(self.bottom_canvas)

        # self.update_3d_fig(self.axs[0]) <- Test용
        # --------------------------------------------------------------------------------------------------------------
        if True:
            # add widget
            self.main_layout.addWidget(main_layout_label)
            self.main_layout.addLayout(main_lay_top_lay)
            self.main_layout.addLayout(main_lay_bottom_lay)

        # test yaxis
        self.set_yaxis()

    def set_yaxis(self):
        self.top_axs[0].xaxis.set_major_formatter(major_formatter_time)
        self.bottom_axs[0].xaxis.set_major_formatter(major_formatter_time)
        self.bottom_axs[1].xaxis.set_major_formatter(major_formatter_time)
        self.bottom_axs[2].xaxis.set_major_formatter(major_formatter_time)
        self.bottom_axs[3].xaxis.set_major_formatter(major_formatter_time)

        self.top_axs[0].yaxis.set_major_formatter(major_formatter_reactor_power)
        self.bottom_axs[0].yaxis.set_major_formatter(major_formatter_temp)
        self.bottom_axs[1].yaxis.set_major_formatter(major_formatter_mwe)
        self.bottom_axs[2].yaxis.set_major_formatter(major_formatter_ppm)
        self.bottom_axs[3].yaxis.set_major_formatter(major_formatter_liter)


class RCBoardUI(BoardUI):
    def __init__(self):
        super(RCBoardUI, self).__init__()
        self.show()

    def update(self, save_mem, local_mem):
        # TODO <- 나중에 Real Time에서 지우기
        temp_save_mem = {}
        for key in save_mem.keys():
            temp_save_mem[key] = save_mem[key][1:]
        save_mem = temp_save_mem
        try:
            # Rod Pos Update
            self.Abank.update(int(abs(local_mem['KBCDO10']['Val'] - 228)))
            self.Bbank.update(int(abs(local_mem['KBCDO9']['Val'] - 228)))
            self.Cbank.update(int(abs(local_mem['KBCDO8']['Val'] - 228)))
            self.Dbank.update(int(abs(local_mem['KBCDO7']['Val'] - 228)))

            # clear
            for ax in self.top_axs:
                ax.clear()
            for ax in self.bottom_axs:
                ax.clear()

            # Top
            # 1] Reactor Power
            self.top_axs[0].set_title('Reactor power')
            self.top_axs[0].plot(save_mem['KCNTOMS'], save_mem['QPROREL'], label='Reactor power')

            self.top_axs[0].fill_between(save_mem['KCNTOMS'], save_mem['UP_D'], save_mem['DOWN_D'],
                                         color='gray', alpha=0.5, label='Boundary')
            self.top_axs[0].plot(save_mem['KCNTOMS'], save_mem['UP_D'], color='gray', lw=1, linestyle='--')
            self.top_axs[0].plot(save_mem['KCNTOMS'], save_mem['DOWN_D'], color='gray', lw=1, linestyle='--')

            self.top_axs[0].legend(fontsize=10, loc=2)


            # 2] Average Temperature
            self.bottom_axs[0].set_title('Average Temperature')

            UpBound = [_ + 1.3 for _ in save_mem['UAVLEGS']]
            DownBound = [_ - 1.3 for _ in save_mem['UAVLEGS']]
            self.bottom_axs[0].fill_between(save_mem['KCNTOMS'], UpBound, DownBound,
                                          color='gray', alpha=0.5, label='Boundary')

            self.bottom_axs[0].plot(save_mem['KCNTOMS'], UpBound,
                                  color='gray', lw=1, linestyle='--', label='')
            self.bottom_axs[0].plot(save_mem['KCNTOMS'], DownBound,
                                  color='gray', lw=1, linestyle='--', label='')
            self.bottom_axs[0].plot(save_mem['KCNTOMS'], save_mem['UAVLEGS'],
                                  color='black', lw=1, linestyle='--', label='Reference Temperature')

            self.bottom_axs[0].plot(save_mem['KCNTOMS'], save_mem['UAVLEGM'],
                                  color='black', label='Average Temperature')
            self.bottom_axs[0].legend(fontsize=10, loc=2)

            # 3] Electric Power
            self.bottom_axs[1].set_title('Electric Power')
            self.bottom_axs[1].plot(save_mem['KCNTOMS'], save_mem['KBCDO20'],
                                    color='gray', linestyle='--', label='Load Set-point [MWe]')
            self.bottom_axs[1].plot(save_mem['KCNTOMS'], save_mem['KBCDO21'],
                                    color='gray', linestyle='-', label='Load Rate [MWe]')
            self.bottom_axs[1].plot(save_mem['KCNTOMS'], save_mem['KBCDO22'],
                                    color='black', label='Electric Power [MWe]')
            self.bottom_axs[1].legend(fontsize=10, loc=2)

            # 4] Boron Concentration
            self.bottom_axs[2].set_title('Boron Concentration')
            self.bottom_axs[2].plot(save_mem['KCNTOMS'], save_mem['KBCDO16'],
                                    color='black', label='Boron Concentration [PPM]')
            self.bottom_axs[2].legend(fontsize=10, loc=2)

            # 5] Inject Boron / Make-up
            self.bottom_axs[3].set_title('Injected Boron / Make-up')
            self.bottom_axs[3].step(save_mem['KCNTOMS'], save_mem['BOR'], label='Injected boron mass', color='blue')
            self.bottom_axs[3].step(save_mem['KCNTOMS'], save_mem['MAKE_UP'], label='Injected make-up water mass', color='black')
            self.bottom_axs[3].legend(fontsize=10, loc=2)

            # ----------------------------------------------------------------------------------------------------------
            self.set_yaxis()
            self.top_canvas.draw()
            self.bottom_canvas.draw()
        except Exception as f:
            print(f)
        pass

if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI()
    # window = RodPosBar(0)
    window.show()
    app.exec_()