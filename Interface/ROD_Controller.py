import matplotlib.pyplot as plt
from Interface.Trend_window import Ui_Dialog as Trend_ui
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class sub_tren_window(QDialog):

    def __init__(self, mem):
        super().__init__()
        self.mem = mem

        self.Trend_ui = Trend_ui()
        self.Trend_ui.setupUi(self)
        # ===============================================================
        # rod gp
        self.draw_rod_his_gp()

        # self.Trend_ui.listWidget.addItem('[00:00:01]\tLCO 1.1.1')
        #  ==============================================================
        self.Trend_ui.listWidget.addItem('RCS_DNBR_1')
        self.Trend_ui.listWidget.addItem('RCS_DNBR_2')
        #  ==============================================================

        timer = QtCore.QTimer(self)
        for _ in [self.update_window, self.update_rod_his_gp]:
            timer.timeout.connect(_)
        timer.start(500)

        self.Trend_ui.listWidget.itemClicked.connect(self.print_out)
        # self.Trend_ui.listWidget.itemClicked(self.print_out)

        self.show()

    def update_window(self):
        self.Trend_ui.Test_label.setText('{:0.2f}'.format(self.mem['ZINST58']['V']))
        self.Trend_ui.Rod_1.setGeometry(30, 100, 41, abs(self.mem['KBCDO10']['V'] - 228))
        self.Trend_ui.Rod_2.setGeometry(90, 100, 41, abs(self.mem['KBCDO9']['V'] - 228))
        self.Trend_ui.Rod_3.setGeometry(150, 100, 41, abs(self.mem['KBCDO8']['V'] - 228))
        self.Trend_ui.Rod_4.setGeometry(210, 100, 41, abs(self.mem['KBCDO7']['V'] - 228))
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



    def print_out(self, item):
        # LCO_name = item.text().split('\t')[1]
        # if LCO_name == 'LCO 1.1.1':
        #     content = 'LCO 1.1.1\n불만족 조건: 가압기 압력이 150km/cm^2 이 되면 안됨.\n 현재 가압기 압력 상태:{}'.format(self.mem['ZINST58']['V'])
        #     QMessageBox.information(self, "LCO 정보", content)

        self.r = 30

        if item.text() == 'RCS_DNBR_1':
            QMessageBox.information(self, "LCO 정보", self.RCS_DNBR_Parameter_1())
        elif item.text() == 'RCS_DNBR_2':
            QMessageBox.information(self, "LCO 정보", self.RCS_DNBR_Parameter_2())

    def RCS_DNBR_Parameter_1(self):
        return str(self.r)

    def RCS_DNBR_Parameter_2(self):
        if self.mem['ZINST58']['V'] > 155:
            return str('불만족 {} {}'.format(self.r, self.mem['ZINST58']['V']))
        elif self.mem['ZINST58']['V'] < 154:
            return str('만족 {} {}'.format(self.r, self.mem['ZINST58']['V']))
