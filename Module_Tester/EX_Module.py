import multiprocessing
from time import sleep
from Module_Tester.EX_CNS_Send_UDP import CNS_Send_Signal


class EX_module(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)

        self.mem = mem[0]  # main mem connection
        self.Act_list = mem[1]  # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

        with open('EX_pro.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')  # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

    def send_action_append(self, pa, va):
        for _ in range(len(pa)):
            self.para.append(pa[_])
            self.val.append(va[_])

    def send_action(self, R_A):
        # 전송될 변수와 값 저장하는 리스트
        self.para = []
        self.val = []

        Load_setpoint = self.mem['KBCDO20']['V']
        Mismatch = self.mem['ZINST15']['V']
        Down_LOAD = self.mem['KSWO224']['V']
        UP_LOAD = self.mem['KSWO225']['V']

        if Mismatch > 0:
            if 840 < Load_setpoint:
                self.send_action_append(['KSWO224', 'KSWO225'], [1, 0]) # down
        else:
            self.send_action_append(['KSWO224', 'KSWO225'], [0, 0])  # stay

        print(Mismatch, Load_setpoint)

        if R_A == 0:
            self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # Stay
        elif R_A == 1:
            self.send_action_append(['KSWO33', 'KSWO32'], [1, 0])  # Out
        elif R_A == 2:
            self.send_action_append(['KSWO33', 'KSWO32'], [0, 1])  # In

        self.CNS_udp._send_control_signal(self.para, self.val)

    def run(self):
        get_nub_act_list = len(self.Act_list)
        while True:
            if self.trig_mem['Loop'] and self.trig_mem['Run']:
                print('계산중....', end='\t')

                while get_nub_act_list == len(self.Act_list):
                    print('대기...')
                    sleep(1)

                self.send_action(R_A=self.Act_list[-1])

                get_nub_act_list = len(self.Act_list)
                print('계산 종료! ....', end='\t')
                print(self, self.mem['KCNTOMS'], self.Act_list, self.trig_mem['Loop'], self.trig_mem['Run'])
                self.trig_mem['Run'] = False