import sys
import multiprocessing

from PySide2.QtWidgets import QApplication, QWidget

from Module_Tester.Test_Interface import TE_interface
from Module_Tester.EX_CNS_Send_UDP import *


class interface_function(multiprocessing.Process):
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
        self.trig_mem = mem[-1]  # main mem connection

        print('Test UI 호출')
        self.ui = TE_interface.Ui_Form()
        self.ui.setupUi(self)
        # ---- 초기함수 호출
        self.call_cns_udp_sender()
        # ---- 버튼 명령
        self.ui.Run.clicked.connect(self.run_cns)
        self.ui.Freeze.clicked.connect(self.freeze_cns)
        self.ui.Go_mal.clicked.connect(self.go_mal)
        # ----
        self.show()

    def call_cns_udp_sender(self):
        # CNS 정보 읽기
        with open('EX_pro.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')   # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

    def run_cns(self):
        self.trig_mem['Loop'] = True

    def freeze_cns(self):
        self.trig_mem['Loop'] = False

    def go_mal(self):
        if self.ui.Mal_nub.text() != '' and self.ui.Mal_type.text() != '' and self.ui.Mal_time.text() != '':
            self.CNS_udp._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                               [10, int(self.ui.Mal_nub.text()),
                                                int(self.ui.Mal_type.text()),
                                                int(self.ui.Mal_time.text())])
            self.ui.Mal_list.addItem('{}_{}_{}'.format(self.ui.Mal_nub.text(),
                                                       self.ui.Mal_type.text(),
                                                       self.ui.Mal_time.text()))
            print('Malfunction 입력 완료')
        else:
            print('Malfunction 입력 실패')