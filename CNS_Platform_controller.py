#
import sys
import multiprocessing
from copy import deepcopy
from time import time
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
#
from Interface import CNS_Platform_controller_interface as CNS_controller
from CNS_Platform_mainwindow import CNSMainWinFunc


class InterfaceFun(multiprocessing.Process):
    def __init__(self, shmem):
        multiprocessing.Process.__init__(self)
        self.shmem = shmem

    def run(self):
        app = QApplication(sys.argv)
        w = MyForm(self.shmem)
        sys.exit(app.exec_())


class MyForm(QWidget):
    def __init__(self, shmem):
        super(MyForm, self).__init__()
        # shmem
        self.shmem = shmem
        # ---- UI 호출
        self.pr_('[SHMem:{self.shmem}][Controller UI 호출]')
        self.ui = CNS_controller.Ui_Form()
        self.ui.setupUi(self)
        # ---- UI 초기 세팅
        self.ui.Cu_SP.setText(str(self.shmem.get_logic('Speed')))
        self.ui.Se_SP.setText(str(self.shmem.get_logic('Speed')))
        # ---- 초기함수 호출
        # ---- 버튼 명령
        self.ui.Run.clicked.connect(self.run_cns)
        self.ui.Freeze.clicked.connect(self.freeze_cns)
        self.ui.Go_mal.clicked.connect(self.go_mal)
        self.ui.Initial.clicked.connect(self.go_init)
        self.ui.Apply_Sp.clicked.connect(self.go_speed)
        self.ui.Go_db.clicked.connect(self.go_save)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
        self.show()

        # Call
        self.cns_main_win = CNSMainWinFunc(shmem=self.shmem)
        self.cns_main_win.show()

    def pr_(self, s):
        head_ = 'Main_UI'
        return print(f'[{head_:10}][{s}]')

    def run_cns(self):
        if self.shmem.get_logic('Initial_condition'):
            self.pr_('CNS 시작')
            self.shmem.change_logic_val('Run', True)
        else:
            self.pr_('먼저 초기 조건을 선언')

    def freeze_cns(self):
        if self.shmem.get_logic('Initial_condition'):
            self.pr_('CNS 일시정지')
            self.shmem.change_logic_val('Run', False)
        else:
            self.pr_('먼저 초기 조건을 선언')

    def go_mal(self):
        if self.ui.Mal_nub.text() != '' and self.ui.Mal_type.text() != '' and self.ui.Mal_time.text() != '':
            # 1. 입력된 내용 List에 저장
            self.ui.Mal_list.addItem('{}_{}_{}'.format(self.ui.Mal_nub.text(),
                                                       self.ui.Mal_type.text(),
                                                       self.ui.Mal_time.text()))
            # 2. 입력된 내용 Trig mem에 저장
            Mal_index = self.ui.Mal_list.count()
            Mal_dict = {'Mal_nub': int(self.ui.Mal_nub.text()),
                        'Mal_opt': int(self.ui.Mal_type.text()),
                        'Mal_time': int(self.ui.Mal_time.text()) * 5,
                        'Mal_done': False}
            self.shmem.change_mal_val(mal_index=Mal_index, mal_dict=Mal_dict)
            # 3. 입력하는 레이블 Clear
            self.ui.Mal_nub.clear()
            self.ui.Mal_type.clear()
            self.ui.Mal_time.clear()
            self.pr_('Malfunction 입력 완료')
        else:
            self.pr_('Malfunction 입력 실패')

    def go_init(self):
        self.pr_('CNS 초기 조건 선언')
        # 1. Mal list clear
        self.ui.Mal_list.clear()
        # 2. Mal trig_mem clear
        self.shmem.call_init(int(self.ui.Initial_list.currentIndex()) + 1)
        # 3. Controller interface update
        self.ui.Cu_SP.setText(str(self.shmem.get_logic('Speed')))
        self.ui.Se_SP.setText(str(self.shmem.get_logic('Speed')))
        # Main window 초기화

    def go_save(self):
        # 실시간 레코딩 중 ...
        self.shmem.change_logic_val('Run_rc', True)
        self.pr_('Ester_Egg_Run_ROD CONTROL TRICK')

    def go_speed(self):
        self.pr_('CNS 속도 조절')
        self.ui.Cu_SP.setText(self.shmem.get_speed(int(self.ui.Se_SP.text())))

    def show_main_window(self):
        # Controller와 동시 실행
        pass

