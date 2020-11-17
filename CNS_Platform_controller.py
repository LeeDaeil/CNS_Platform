#
import sys
import multiprocessing
from copy import deepcopy
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer
#
from Interface import CNS_Platform_controller_interface as CNS_controller
# from CNS_Platform_mainwindow import CNS_mw


class InterfaceFun(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem

    def run(self):
        app = QApplication(sys.argv)
        w = MyForm(self.mem)
        sys.exit(app.exec_())


class MyForm(QWidget):
    def __init__(self, mem):
        super().__init__()
        self.mem = mem[0]   # main mem connection
        self.copy_mem_structure = deepcopy(self.mem)
        self.trig_mem = mem[-1]  # main mem connection
        self.copy_trig_mem = deepcopy(self.trig_mem)

        print('Controller UI 호출')
        self.ui = CNS_controller.Ui_Form()
        self.ui.setupUi(self)
        self.ui.Se_SP.setText(self.ui.Cu_SP.text())
        # ---- 초기함수 호출
        # ---- 버튼 명령
        self.ui.Run.clicked.connect(self.run_cns)
        self.ui.Freeze.clicked.connect(self.freeze_cns)
        self.ui.Go_mal.clicked.connect(self.go_mal)
        self.ui.Initial.clicked.connect(self.go_init)
        self.ui.Go_db.clicked.connect(self.go_save)
        self.ui.Apply_Sp.clicked.connect(self.go_speed)
        # self.ui.Show_main_win.clicked.connect(self.show_main_window)
        # ----
        self.ui.Cu_SP.setText(str(self.copy_trig_mem['Speed']))
        self.ui.Se_SP.setText(str(self.copy_trig_mem['Speed']))
        # ---- Qtimer
        timer = QTimer(self)
        for _ in [self._update_test]:
            timer.timeout.connect(_)
        timer.start(600)
        # ----
        self.show()

    def _update_test(self):
        print(self.mem['KCNTOMS'])

    def _update_trig_mem(self):
        for key_val in self.copy_trig_mem.keys():
            self.trig_mem[key_val] = self.copy_trig_mem[key_val]

    def run_cns(self):
        print('CNS 시작')
        self.trig_mem['Run'] = True

    def freeze_cns(self):
        print('CNS 일시정지')
        self.trig_mem['Run'] = False

    def go_mal(self):
        if self.ui.Mal_nub.text() != '' and self.ui.Mal_type.text() != '' and self.ui.Mal_time.text() != '':
            # 1. 입력된 내용 List에 저장
            self.ui.Mal_list.addItem('{}_{}_{}'.format(self.ui.Mal_nub.text(),
                                                       self.ui.Mal_type.text(),
                                                       self.ui.Mal_time.text()))
            # 2. 입력된 내용 Trig mem에 저장
            Mal_index = self.ui.Mal_list.count()
            self.copy_trig_mem['Mal_list'][Mal_index] = {'Mal_nub': int(self.ui.Mal_nub.text()),
                                                         'Mal_opt': int(self.ui.Mal_type.text()),
                                                         'Mal_time': int(self.ui.Mal_time.text()) * 5}
            self.copy_trig_mem['Mal_Call'] = True
            # 3. 입력된 내용 Trig mem update
            self._update_trig_mem()
            # 4. 입력하는 레이블 Clear
            self.ui.Mal_nub.clear()
            self.ui.Mal_type.clear()
            self.ui.Mal_time.clear()
            print('Malfunction 입력 완료')
        else:
            print('Malfunction 입력 실패')

    def go_init(self):
        print('CNS 초기 조건')
        # 1. Mal list clear
        self.ui.Mal_list.clear()
        # 2. Mal trig_mem clear
        self.copy_trig_mem['Mal_list'] = {}     # List Clear
        self.copy_trig_mem['Speed'] = 5         # Speed 5 set-up
        # 3. Controller interface update
        self.ui.Cu_SP.setText(str(self.copy_trig_mem['Speed']))
        self.ui.Se_SP.setText(str(self.copy_trig_mem['Speed']))

        # 입력된 내용 Trig mem update
        self._update_trig_mem()

        # 초기화 요청
        self.trig_mem['Init_nub'] = int(self.ui.Initial_list.currentIndex()) + 1
        self.trig_mem['Init_Call'] = True

    def go_save(self):
        # 실시간 레코딩 중 ...
        pass

    def go_speed(self):
        self.trig_mem['Speed_Call'] = True
        self.trig_mem['Speed'] = int(self.ui.Se_SP.text())
        self.ui.Cu_SP.setText(str(self.trig_mem['Speed']))

    # def show_main_window(self):
    #     self.cns_main_win = CNS_mw(mem=self.mem, trig_mem=self.trig_mem)
