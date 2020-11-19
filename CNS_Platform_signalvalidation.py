import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QPushButton, QVBoxLayout
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
        # self.setText(f"{self.para}\t\t\t\t[{self.orgin_val}:{self.predcit_val}]\n{self.label}")
        self.setText(f"{self.label}")
        self.setStyleSheet('text-align:left;')

    def update_label(self, orgin_val, predcit_val):
        self.orgin_val = (orgin_val * self.scaled_) + self.min_
        self.predcit_val = (predcit_val * self.scaled_) + self.min_
        # self.setText(f"{self.para}\t\t\t\t[{self.orgin_val}:{self.predcit_val}]\n{self.label}")
        self.setText(f"{self.label}")

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
        self._init_gp_canv()
        # ===============================================================
        timer = QtCore.QTimer(self)
        for _ in [self._update_window]:
            timer.timeout.connect(_)
        timer.start(600)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)

        self.setGeometry(875, 496, 938, 517)

        self.show()

# ======================= _init =================================================
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

        self.db_min = [0.7907880214773746, 0.0, 0.0, 0.0, 74.36228989763885, 0.15007924799392564, 0.0,
                       -0.025655161347620234, -0.025755194704746322, 0.8574499315363537, 62.522021623481045,
                       78.44883128135515, 25.69968913063228, 96.90045848404975, 133.94795247238773, 118.54704985242475,
                       0.0, 0.0, 15.023461541962094, 0.0, 0.0, 0.0, 7.47084807422724, 7.5367613769581245,
                       33.66180619735684, 35.75302372065697]
        self.db_max = [102.88566584259075, 629.9154690942836, 713.3930491450711, 651.7105497407289, 265.5858454569744,
                       115.13002965768129, 622.0463876435214, 622.6989390752461, 612.4840226548157, 85.35325909456378,
                       329.67038285226295, 339.7979026152628, 341.9907304565078, 340.14224664059833, 408.0859231428463,
                       373.1557720765887, 6.600229668324357, 66.41561737835107, 182.338821318991, 125.57489246742367,
                       121.98577760457154, 120.52066982515773, 103.24536154247119, 104.3068944045294, 84.9565782078394,
                       85.99186478962858]

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
        self._para_info = {}

        for i in range(len(self._want_para)):
            self._want_para[i]['Thre'] = self.threshold[i]
            self._want_para[i]['scaled_'] = self.scaled_[i]
            self._want_para[i]['min_'] = self.min_[i]

            self._para_info[self._want_para[i]['para']] = {}
            self._para_info[self._want_para[i]['para']]['db_min'] = self.db_min[i]
            self._para_info[self._want_para[i]['para']]['db_max'] = self.db_max[i]
            self._para_info[self._want_para[i]['para']]['Thre'] = self.threshold[i]
            self._para_info[self._want_para[i]['para']]['scaled_'] = self.scaled_[i]
            self._para_info[self._want_para[i]['para']]['min_'] = self.min_[i]
            self._para_info[self._want_para[i]['para']]['label'] = self._want_para[i]['label']

        self._want_see_gp_para = self._want_para[0]['para']

    def _init_add_button(self):
        nub = 0
        for i in range(100):
            if nub >= len(self._want_para):
                self.Trend_ui._area_para.setMaximumHeight(24 * i) # 1라인
                # self.Trend_ui._area_para.setMaximumHeight(35 * i) # 2라인
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

    def _init_gp_canv(self):
        self.canv_left = plt.figure(tight_layout={'pad': 1})
        self.canv_left_ax = self.canv_left.add_subplot(111)
        self.canv_left_canv = FigureCanvasQTAgg(self.canv_left)

        self.canv_left_vl = QtWidgets.QVBoxLayout(self.Trend_ui._area_graph_para)
        self.canv_left_vl.setContentsMargins(0, 0, 0, 0)
        self.canv_left_vl.addWidget(self.canv_left_canv)

        self.canv_right = plt.figure(tight_layout={'pad': 1})
        self.canv_right_ax = self.canv_right.add_subplot(111)
        self.canv_right_canv = FigureCanvasQTAgg(self.canv_right)

        self.canv_right_vl = QtWidgets.QVBoxLayout(self.Trend_ui._area_graph_thre)
        self.canv_right_vl.setContentsMargins(0, 0, 0, 0)
        self.canv_right_vl.addWidget(self.canv_right_canv)

        self.draw_ax_list = [self.canv_left_ax, self.canv_right_ax]
        self.draw_gp_list = [self.canv_left_canv, self.canv_right_canv]
        pass

# ======================= _call =================================================
    def _call_print(self, para, label, thre):
        self._want_see_gp_para = para

# ======================= _update ===============================================
    def _update_window(self):
        get_last_nub = len(self.mem['cINIT']) - 1
        if get_last_nub != -1:
            # 인디케이터 업데이트
            for child in self.Trend_ui._area_para.children():
                if child.isWidgetType():    # True 는 버튼
                    child.update_label(orgin_val=self.mem[child.para][get_last_nub * 5],                # TODO 시간 바뀌면 죽음...
                                       predcit_val=self.mem[child.cpara][get_last_nub * 5])
            # 그래프 업데이트
            self._update_window_gp()
        pass

    def _update_window_gp(self):
        [_.clear() for _ in self.draw_ax_list]
        # -------------------------------------------------------------------------

        get_para = self.mem[self._want_see_gp_para]                 # {'0': .., '1': ..}
        get_cpara = self.mem[f"c{self._want_see_gp_para}"]          # {'0': .., '1': ..}
        get_para = [get_para[i*5] for i in range(len(get_para))]                             # TODO 시간 바뀌면 죽음...
        get_cpara = [get_cpara[i*5] for i in range(len(get_cpara))]


        self.canv_left_ax.set_title({self._para_info[self._want_see_gp_para]['label']})
        self.canv_left_ax.plot(get_para[1:], label=f"Original Val")
        self.canv_left_ax.plot(get_cpara[1:], label=f"Prediction Val")
        self.canv_left_ax.set_ylim(self._para_info[self._want_see_gp_para]['db_min'] * 1.10,
                                   self._para_info[self._want_see_gp_para]['db_max'] * 1.10)


        get_para_trans = [get_para_ * self._para_info[self._want_see_gp_para]['scaled_'] +
                          self._para_info[self._want_see_gp_para]['min_'] for get_para_ in get_para]
        get_cpara_trans = [get_cpara_ * self._para_info[self._want_see_gp_para]['scaled_'] +
                           self._para_info[self._want_see_gp_para]['min_'] for get_cpara_ in get_cpara]

        dev = [(c-p) ** 2 for c, p in zip(get_cpara_trans, get_para_trans)]
        thr = [self._para_info[self._want_see_gp_para]['Thre'] for _ in dev]

        self.canv_right_ax.set_title({self._para_info[self._want_see_gp_para]['label']})
        self.canv_right_ax.plot(dev[1:], label=f"Reconstruction Error")
        self.canv_right_ax.plot(thr[1:], label=f"Threshold")

        # -------------------------------------------------------------------------
        [_.grid() for _ in self.draw_ax_list]
        [_.legend(loc='upper right', fontsize=9) for _ in self.draw_ax_list]
        # -------------------------------------------------------------------------
        [_.draw() for _ in self.draw_gp_list]
        pass

    # def changeEvent(self, a0) -> None:
    #     print(self.geometry())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CNSSignalValidation(mem=None)
    sys.exit(app.exec_())