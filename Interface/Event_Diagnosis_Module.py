import matplotlib.pyplot as plt
from Interface.A_Event_Diagnosis_Module import Ui_Dialog as EDM_UI
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class sub_event_window(QDialog):
    def __init__(self, mem=None, auto_mem = None, strage_mem=None):
        super().__init__()
        # ===============================================================
        # 메모리 호출 부분 없으면 Test
        if mem != None:
            self.mem = mem
            self.auto_mem = auto_mem
            self.strage_mem = strage_mem
        else:
            print('TEST_interface')

        self.init_UI()
        self.blick = True
        self.show()

    def init_UI(self):
        self.EDM_ui = EDM_UI()
        self.EDM_ui.setupUi(self)
        # ===============================================================
        # draw dig
        self.draw_dig_his_gp()

        timer = QtCore.QTimer(self)
        for _ in [self.update_window, self.update_dig_his_gp]:
            timer.timeout.connect(_)
        timer.start(600)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)

    def update_window(self):
        try:
            if self.auto_mem['Abnormal_Dig_result']['Result'][-1][0] < 0.9:
                self.EDM_ui.label_4.setText('23-01(1차측 누설)')
                if self.blick:
                    self.EDM_ui.label_4.setStyleSheet('background-color: rgb(255, 255, 255); border-style: outset; '
                                                      'border-width: 0.5px; border-color: black;'
                                                      'font: bold 14px;')
                    self.blick = False
                else:
                    self.EDM_ui.label_4.setStyleSheet('background-color: rgb(255, 248, 29); border-style: outset; '
                                                      'border-width: 1.5px; border-color: rgb(255, 243, 61);'
                                                      'font: bold 14px;')
                    self.blick = True
        except Exception as e:
            pass

    def draw_dig_his_gp(self):
        # 위 그래프
        self.dig_fig = plt.figure(figsize=(20, 20))
        self.gs = self.dig_fig.add_gridspec(1, 1)
        self.dig_ax = [self.dig_fig.add_subplot(self.gs[:, :])]
        self.dig_canv = FigureCanvasQTAgg(self.dig_fig)
        self.EDM_ui.horizontalLayout.addWidget(self.dig_canv)

    def update_dig_his_gp(self):
        if self.auto_mem['Abnormal_Dig_result']['Result'] != []:
            self.EDM_ui.a1.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][1]*100))
            self.EDM_ui.a2.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][2]*100))
            self.EDM_ui.a3.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][3]*100))
            self.EDM_ui.a4.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][4]*100))
            self.EDM_ui.a5.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][5]*100))
            self.EDM_ui.a6.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][6]*100))
            self.EDM_ui.a7.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][7]*100))
            self.EDM_ui.a8.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][8]*100))
            self.EDM_ui.a9.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][9]*100))
            self.EDM_ui.a10.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][10]*100))
            self.EDM_ui.a11.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][11]*100))
            self.EDM_ui.a12.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][12]*100))
            self.EDM_ui.a13.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][13]*100))
            self.EDM_ui.a14.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][14]*100))
            self.EDM_ui.a15.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][15]*100))
            self.EDM_ui.a16.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][16]*100))
            self.EDM_ui.a17.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][17]*100))
            self.EDM_ui.a18.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][18]*100))
            self.EDM_ui.a19.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][19]*100))
            self.EDM_ui.a20.setText('{:0.2f}'.format(self.auto_mem['Abnormal_Dig_result']['Result'][-1][20]*100))
        # 그래프 업데이트
        [ax.clear() for ax in self.dig_ax]
        self.dig_ax[0].plot(self.auto_mem['Abnormal_Dig_result']['Result'])
        self.dig_ax[0].legend(['Normal', 'ab_21-01', 'ab_21-02', 'ab_20-01', 'ab_20-04', 'ab_15-07', 'ab_15-08', 'ab_63-04',
                               'ab_63-02', 'ab_63-03', 'ab_21-12', 'ab-19-02', 'ab_21-11', 'ab_23-03', 'ab_80-02', 'ab_60-02',
                               'ab_59-02', 'ab_23-01', 'ab_23-06', 'ab_59-01', 'ab_64-03'], loc=7)
        self.dig_ax[0].grid()
        self.dig_canv.draw()

