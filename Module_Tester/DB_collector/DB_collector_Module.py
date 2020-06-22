import multiprocessing
import pandas as pd
import random
from time import sleep

from Module_Tester.EX_CNS_Send_UDP import CNS_Send_Signal

TEST_FOR_LOAD = False

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
        self.CNS_udp._send_control_signal(self.para, self.val)

    def run(self):
        get_nub_act_list = len(self.Act_list)
        endtime = 100
        max_case = 6
        mal_list = [_ for _ in zip([12 for _ in range(max_case)],
                                   [100000*random.randint(1, 3)
                                    +10*random.randint(1, 20) for _ in range(max_case)],
                                   [5+5*random.randint(1, 10) for _ in range(max_case)])]
        mal_case_cr = 0
        print(mal_list)

        # 1. Loop 시작
        # Call initial
        initial_condition = 1
        print(f'초기화 {initial_condition} 요청')
        self.CNS_udp._send_control_signal(['KFZRUN', 'KSWO277'], [5, initial_condition])
        sleep(1)
        # Call malfunction
        Mal_nub, Mal_type, Mal_time = mal_list[mal_case_cr]
        print(f'Malfun {Mal_nub}-{Mal_type}-{Mal_time}')
        self.CNS_udp._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                          [10, int(Mal_nub),
                                           int(Mal_type),
                                           int(Mal_time)])
        sleep(1)
        self.trig_mem['Loop'] = True

        while True:
            if self.trig_mem['Run']:
                print('계산중....', end='\t')
                ##
                print('계산 종료! ....', end='\t')
                print(self, self.mem['KSWO278']['V'],
                      self.mem['KCNTOMS']['L'], self.Act_list, self.trig_mem['Loop'], self.trig_mem['Run'])
                self.trig_mem['Run'] = False

            if self.mem['KCNTOMS']['V'] > endtime and self.mem['KFZRUN']['V'] != 5:
                self.trig_mem['Loop'] = False
                # Call save file
                s = f'{mal_list[mal_case_cr]}'
                temp = pd.DataFrame()
                for keys in self.mem.keys():
                    temp[keys] = self.mem[keys]['L']
                temp.to_csv(f'DB/{s}.csv')
                print('DB save')
                # initial next mal_case
                mal_case_cr += 1

                # Call initial
                initial_condition = 1
                print(f'초기화 {initial_condition} 요청')
                self.CNS_udp._send_control_signal(['KFZRUN', 'KSWO277'], [5, initial_condition])
                sleep(1)
                # Call malfunction
                Mal_nub, Mal_type, Mal_time = mal_list[mal_case_cr]
                print(f'Malfun {Mal_nub}-{Mal_type}-{Mal_time}')
                self.CNS_udp._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                                  [10, int(Mal_nub),
                                                   int(Mal_type),
                                                   int(Mal_time)])
                sleep(1)

                self.trig_mem['Loop'] = True