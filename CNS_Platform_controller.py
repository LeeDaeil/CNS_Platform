import sys
import multiprocessing
import time
import pandas as pd

from PySide2.QtWidgets import QApplication, QWidget

from Interface import CNS_Platform_controller_interface as CNS_controller
from CNS_Platform_mainwindow import CNS_mw
from CNS_Send_UDP import CNS_Send_Signal
import CNS_Platform_PARA as PARA

from copy import deepcopy


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
        self.copy_mem_structure = deepcopy(self.mem)
        self.trig_mem = mem[-1]  # main mem connection

        print('Test UI 호출')
        self.ui = CNS_controller.Ui_Form()
        self.ui.setupUi(self)
        self.ui.Se_SP.setText(self.ui.Cu_SP.text())
        # ---- 초기함수 호출
        self.call_cns_udp_sender()
        # ---- 버튼 명령
        self.ui.Run.clicked.connect(self.run_cns)
        self.ui.Freeze.clicked.connect(self.freeze_cns)
        self.ui.Go_mal.clicked.connect(self.go_mal)
        self.ui.Initial.clicked.connect(self.go_init)
        self.ui.Go_db.clicked.connect(self.go_save)
        self.ui.Apply_Sp.clicked.connect(self.go_speed)
        self.ui.Show_main_win.clicked.connect(self.show_main_window)
        # ----
        self.show()

    def call_cns_udp_sender(self):
        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')   # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

    def run_cns(self):
        print('CNS 시작')
        self.trig_mem['Loop'] = True

    def freeze_cns(self):
        print('CNS 일시정지')
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

        if initial_nub == 17:
            self.trig_mem['ST_OPStratey'] = PARA.ST_OP
        elif initial_nub == 13:
            self.trig_mem['ST_OPStratey'] = PARA.PZR_OP

            print('CNS 10 배속 변경')
            self.ui.Se_SP.setText('10')

            self.CNS_udp._send_control_signal(['TDELTA'], [0.2 * int(self.ui.Se_SP.text())])
            self.trig_mem['Speed'] = int(self.ui.Se_SP.text())
            self.ui.Cu_SP.setText(self.ui.Se_SP.text())

        else:
            self.trig_mem['ST_OPStratey'] = PARA.ST_OP  ### 디폴트

        Mode = self.trig_mem['ST_OPStratey']
        print(f'초기화 {initial_nub} 요청 + {Mode}')
        self.CNS_udp._send_control_signal(['KFZRUN', 'KSWO277'], [5, initial_nub])

    def go_save(self):
        now = time.localtime()
        s = "%02d-%02d_%02d_%02d_%02d_%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_min,
                                               now.tm_sec)
        temp = pd.DataFrame()
        for keys in self.mem.keys():
            temp[keys] = self.mem[keys]['L']
        temp.to_csv(f'{s}.csv')
        print('DB save')

    def go_speed(self):
        if not self.trig_mem['Loop']:
            print('CNS 배속 변경')
            self.CNS_udp._send_control_signal(['TDELTA'], [0.2 * int(self.ui.Se_SP.text())])
            self.trig_mem['Speed'] = int(self.ui.Se_SP.text())
            self.ui.Cu_SP.setText(self.ui.Se_SP.text())
        else:
            print('CNS 배속 변경 시 Freeze에서 변경 가능함.')
            pass

    def show_main_window(self):
        self.cns_main_win = CNS_mw(mem=self.mem, trig_mem=self.trig_mem)
