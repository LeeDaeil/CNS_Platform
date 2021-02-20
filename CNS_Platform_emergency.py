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
from TOOL.TOOL_PTCurve import PTCureve
from CNS_Platform_Base import BoardUI_Base


@ticker.FuncFormatter
def major_formatter_time(time, pos):
    time = int(time/5)
    return f"{time}[Sec]"


@ticker.FuncFormatter
def major_formatter(x, pos):
    return f"{abs(int(x/5))}"


@ticker.FuncFormatter
def major_formatter_aux(aux, pos):
    return f"{int(aux)}[Kg/sec]"


@ticker.FuncFormatter
def major_formatter_dump(dump, pos):
    return f"{dump/100000:.1f}[kg/cm^2]"


@ticker.FuncFormatter
def major_formatter_val(val, pos):
    return f"{val:.1f}[%]"


class BoardUI(BoardUI_Base):
    def __init__(self):
        super(BoardUI, self).__init__(title='Autonomous Operation Interface',
                                      WindowId='EM')
        # 요소 선언 -----------------------------------------------------------------------------------------------------
        # 1] 그래프
        self.fig = plt.Figure(tight_layout=True)
        gs = GridSpec(8, 1, figure=self.fig)

        self.axs = [
            self.fig.add_subplot(gs[0:4, :], projection='3d'),
            self.fig.add_subplot(gs[4:5, :]),
            self.fig.add_subplot(gs[5:6, :]),
            self.fig.add_subplot(gs[6:7, :]),
            self.fig.add_subplot(gs[7:8, :]),
        ]
        self.fig.canvas.draw()
        self.canvas = FigureCanvasQTAgg(self.fig)

        # self.update_3d_fig(self.axs[0]) <- Test용
        # --------------------------------------------------------------------------------------------------------------
        if True:
            # add widget
            self.main_layout.addWidget(self.canvas)

    def update_3d_fig(self, ax, max_=350,
                      KCNTOMS=[5, 10, 15, 20],
                      CoolingRateSW=[0, 0, 200, 230],
                      UAVLEG2 = [200, 200, 200, 200],
                      ZINST65 = [160, 150, 140, 130],
                      ):
        KCNTOMS_len = len(KCNTOMS)
        # max_len = max_ if max_ > KCNTOMS_len else KCNTOMS_len
        max_len = max_
        inv_KCNTOMS = [- val for val in KCNTOMS]

        Temp = []
        UpPres = []
        BotPres = []
        for _ in range(0, max_len):
            uppres, botpres = PTCureve()._get_pres(_)
            Temp.append([_])
            UpPres.append([uppres])
            BotPres.append([botpres])

        PTX = np.array(Temp)
        BotZ = np.array(BotPres)
        UpZ = np.array(UpPres)
        PTY = np.array([[0] for _ in range(0, max_len)])

        PTX = np.hstack([PTX[:, 0:1], Temp])
        BotZ = np.hstack([BotZ[:, 0:1], BotPres])
        UpZ = np.hstack([UpZ[:, 0:1], UpPres])
        PTY = np.hstack([PTY[:, 0:1], np.array([[inv_KCNTOMS[-1]] for _ in range(0, max_len)])])

        zero = [0 for _ in range(len(KCNTOMS))]

        # Cooling rate 그래프 -------------------------------------------------------------------------------------------
        if True:
            Cooling_Temp, Cooling_Time, Cooling_Zero = [], [], []
            for i, val in enumerate(CoolingRateSW):
                if val != 0:
                    Cooling_Temp.append(val)
                    Cooling_Time.append(inv_KCNTOMS[i])
                    Cooling_Zero.append(0)

            ax.plot3D(Cooling_Temp, Cooling_Time, Cooling_Zero, color='orange', lw=1.5, ls='--')
        # PT 커브 -------------------------------------------------------------------------------------------------------
        if True:
            ax.plot3D([170, 0, 0, 170, 170],
                               [inv_KCNTOMS[-1], inv_KCNTOMS[-1], 0, 0, inv_KCNTOMS[-1]],
                               [29.5, 29.5, 29.5, 29.5, 29.5], color='black', lw=0.5, ls='--')
            ax.plot3D([170, 0, 0, 170, 170],
                               [inv_KCNTOMS[-1], inv_KCNTOMS[-1], 0, 0, inv_KCNTOMS[-1]],
                               [17, 17, 17, 17, 17], color='black', lw=0.5, ls='--')
            ax.plot3D([170, 170], [inv_KCNTOMS[-1], inv_KCNTOMS[-1]],
                               [17, 29.5], color='black', lw=0.5, ls='--')
            ax.plot3D([170, 170], [0, 0], [17, 29.5], color='black', lw=0.5, ls='--')
            ax.plot3D([0, 0], [inv_KCNTOMS[-1], inv_KCNTOMS[-1]], [17, 29.5], color='black', lw=0.5, ls='--')
            ax.plot3D([0, 0], [0, 0], [17, 29.5], color='black', lw=0.5, ls='--')

            ax.plot_surface(PTX, PTY, UpZ, rstride=8, cstride=8, alpha=0.15, color='r')
            ax.plot_surface(PTX, PTY, BotZ, rstride=8, cstride=8, alpha=0.15, color='r')
        # 냉각 감압 그래프 -----------------------------------------------------------------------------------------------
        if True:
            ax.plot3D(UAVLEG2, inv_KCNTOMS, ZINST65, color='blue', lw=1.5)
            # each
            ax.plot3D(UAVLEG2, inv_KCNTOMS, zero, color='black', lw=1, ls='--')  # temp
            ax.plot3D(zero, inv_KCNTOMS, ZINST65, color='black', lw=1, ls='--')  # pres
            ax.plot3D(UAVLEG2, zero, ZINST65, color='black', lw=1, ls='--')  # PT
        # 냉각 감압 그래프 표시기 -----------------------------------------------------------------------------------------
        if True:
            # linewidth or lw: float
            ax.plot3D([UAVLEG2[-1], UAVLEG2[-1]],
                               [inv_KCNTOMS[-1], inv_KCNTOMS[-1]],
                               [0, ZINST65[-1]], color='blue', lw=0.5, ls='--')
            ax.plot3D([0, UAVLEG2[-1]],
                               [inv_KCNTOMS[-1], inv_KCNTOMS[-1]],
                               [ZINST65[-1], ZINST65[-1]], color='blue', lw=0.5, ls='--')
            ax.plot3D([UAVLEG2[-1], UAVLEG2[-1]],
                               [0, inv_KCNTOMS[-1]],
                               [ZINST65[-1], ZINST65[-1]], color='blue', lw=0.5, ls='--')
        # --------------------------------------------------------------------------------------------------------------
        # 절대값 처리

        ax.yaxis.set_major_formatter(major_formatter)
        ax.set_xlabel('Temperature')
        ax.set_ylabel('Time [Sec]')
        ax.set_zlabel('Pressure')
        ax.set_title('PT-Curve')

        ax.set_xlim(0, max_len)
        ax.set_zlim(0, 200)

    def update_fig(self, axs, mem):
        # Aux
        tot_aux = [aux1 * aux1p + aux2 * aux2p + aux3 * aux3p for aux1, aux2, aux3, aux1p, aux2p, aux3p in
                   zip(mem['WAFWS1'], mem['WAFWS2'], mem['WAFWS3'],
                       mem['KLAMPO134'], mem['KLAMPO135'], mem['KLAMPO136'])]
        axs[1].set_ylim(-0.2, 100)
        axs[1].plot(mem['KCNTOMS'], tot_aux, label='Total Aux Feed Water')
        axs[1].legend(fontsize=9, loc=2)

        # Dump
        # axs[2].plot(mem['KCNTOMS'], mem['BHTBY'], label='Dump Valve Position')
        axs[2].plot(mem['KCNTOMS'], mem['PMSS'], label='Dump Valve Set-point')
        # axs[2].set_ylim(-0.2, 1.2)
        axs[2].legend(fontsize=9, loc=2)

        # Spray and Heater
        axs[3].plot(mem['KCNTOMS'], mem['BPRZSP'], label='PZR Spray Position')
        axs[3].plot(mem['KCNTOMS'], mem['QPRZH'], label='PZR Proportional Heater')
        axs[3].plot(mem['KCNTOMS'], mem['KLAMPO118'], label='PZR Back-up Heater')
        axs[3].set_ylim(-0.2, 1.2)
        axs[3].legend(fontsize=9, loc=2)

        # SI Charging
        axs[4].plot(mem['KCNTOMS'], mem['BHV22'], label='SI Valve')
        # axs[4].plot(mem['KCNTOMS'], mem['KLAMPO70'], label='Charging Pump 2')
        axs[4].set_ylim(-0.2, 1.2)
        axs[4].set_yticks([0, 1])
        axs[4].set_yticklabels(['Close', 'Open'])
        axs[4].legend(fontsize=9, loc=2)

        # axs
        axs[1].xaxis.set_major_formatter(major_formatter_time)
        axs[2].xaxis.set_major_formatter(major_formatter_time)
        axs[3].xaxis.set_major_formatter(major_formatter_time)
        axs[4].xaxis.set_major_formatter(major_formatter_time)
        #
        axs[1].yaxis.set_major_formatter(major_formatter_aux)
        axs[2].yaxis.set_major_formatter(major_formatter_dump)
        axs[3].yaxis.set_major_formatter(major_formatter_val)

        pass


class EMBoardUI(BoardUI):
    def __init__(self):
        super(EMBoardUI, self).__init__()
        self.show()

    def update(self, mem):
        super(EMBoardUI, self).update()
        if len(mem['KCNTOMS']) > 2:

            _ = [ax.clear() for ax in self.axs]
            try:
                self.update_3d_fig(self.axs[0],
                                   KCNTOMS=mem['KCNTOMS'],
                                   CoolingRateSW=mem['cCOOLRATE'],
                                   UAVLEG2=mem['UAVLEG2'],
                                   ZINST65=mem['ZINST65']
                                   )

                self.update_fig(self.axs, mem)

                self.canvas.draw()
            except Exception as e:
                print(e)


if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI()
    window.show()
    app.exec_()