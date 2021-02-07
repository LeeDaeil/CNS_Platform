import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import sys
import json
import numpy as np


class BoardUI_Base(QWidget):
    """
    Function
    1. 창 이동 및 크기 조정하면 CNS_Platform.ini 파일에 자동 저장됨.
    2. main_window 는 HBoxLayout()
    """
    def __init__(self, title, WindowId):
        super(BoardUI_Base, self).__init__()
        # --------------------------------------------------------------------------------------------------------------
        self.setWindowTitle(title)
        self.WindowId = WindowId
        # --------------------------------------------------------------------------------------------------------------
        pos_info = json.load(open("CNS_Platform.ini"))[self.WindowId]
        self.setGeometry(pos_info['x'], pos_info['y'], pos_info['h'], pos_info['w'])
        # 요소 선언 -----------------------------------------------------------------------------------------------------
        # 1] Main Frame
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def draw_fig(tight=True):
        fig = plt.Figure(tight_layout=True)
        required_row = 1
        required_col = 1
        gs = GridSpec(required_row, required_col, figure=fig)

        axs = [
            fig.add_subplot(gs[:, :], projection='3d'),
        ]
        fig.canvas.draw()
        canvas = FigureCanvasQTAgg(fig)
        return fig, axs, canvas

    def _save_pos_info(self, win_name):
        # Get_current_pos
        pos_info = json.load(open("CNS_Platform.ini"))
        # Get wind pos
        geo = self.geometry().getRect()
        pos_info[win_name] = {'x': geo[0], 'y': geo[1], 'h': geo[2], 'w': geo[3]}
        # Update pos
        json.dump(pos_info, open("CNS_Platform.ini", 'w'))

    def moveEvent(self, a) -> None:
        self._save_pos_info(win_name=self.WindowId)

    def resizeEvent(self, a) -> None:
        self._save_pos_info(win_name=self.WindowId)


if __name__ == '__main__':
    # Board_Tester
    app = QApplication(sys.argv)
    window = BoardUI_Base()
    window.show()
    app.exec_()