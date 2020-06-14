import sys
import multiprocessing
import time
import pandas as pd

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

        print('Test UI 호출')
        self.ui = TE_interface.Ui_Form()
        self.ui.setupUi(self)

        if mem == None: # TEST Stay
            pass
        else:
            self.mem = mem[0]  # main mem connection
            self.Act_list = mem[1]
            self.trig_mem = mem[-1]  # main mem connection
            # ---- 초기함수 호출
            self.call_cns_udp_sender()
            # ---- 버튼 명령
            self.ui.Run.clicked.connect(self.run_cns)
            self.ui.Freeze.clicked.connect(self.freeze_cns)
            self.ui.Go_mal.clicked.connect(self.go_mal)
            self.ui.Initial.clicked.connect(self.go_init)
            self.ui.Go_db.clicked.connect(self.go_save)
            self.ui.His_input_bar.returnPressed.connect(self.add_item)
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

    def go_init(self):
        initial_nub = int(self.ui.Initial_list.currentIndex()) + 1
        print(f'초기화 {initial_nub} 요청')
        self.CNS_udp._send_control_signal(['KFZRUN', 'KSWO277'], [5, initial_nub])

    def go_save(self):
        if self.ui.Mal_list.count() > 0:
            s = self.ui.Mal_list.item(self.ui.Mal_list.count()-1).text()
            print(s)
        else:
            now = time.localtime()
            s = "%02d-%02d_%02d_%02d_%02d_%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_min,
                                                   now.tm_sec)
        temp = pd.DataFrame()
        for keys in self.mem.keys():
            temp[keys] = self.mem[keys]['L']
        temp.to_csv(f'{s}.csv')
        print('DB save')

    def add_item(self):
        self.Act_list.append(int(self.ui.His_input_bar.text()))
        self.ui.His_input_list.insertItems(0, self.ui.His_input_bar.text())


if __name__ == '__main__':
    # test for interface
    app = QApplication(sys.argv)
    w = MyForm(None)
    sys.exit(app.exec_())