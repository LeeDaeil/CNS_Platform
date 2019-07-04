import multiprocessing
import time
import pandas as pd
from copy import deepcopy
import time


class clean_mem(multiprocessing.Process):
    def __init__(self, mem, shut_up):
        multiprocessing.Process.__init__(self)
        self.all_mem = mem
        self.clean_signal_mem = mem[-1]
        self.db_mem = mem[0]

        self.shut_up = shut_up
        self.recover_initial_mem = deepcopy(self.all_mem)

    def p_shut(self, txt):
        if not self.shut_up:
            print(self, txt)

    def run(self):
        while True:
            if self.clean_signal_mem['Clean']:
                self.p_shut('메모리 지우는 것을 시도')
                # ------------------------------------------------------------#
                # save data part
                if True:
                    self.p_shut('메인 메모리 정리 시작 -> CNS_UDP로 넘어감)')
                # ------------------------------------------------------------#
                nub_mem = 0
                for __ in self.all_mem[:-1]:
                    # print(type(__).__name__) Show shared memory type
                    if type(__).__name__ == 'DictProxy':    # Dict clear
                        # ----------------------------------------------------#
                        self.p_shut('메인 메모리 정리 시작 -> CNS_UDP로 넘어감)')
                        if 'KFIGIV' in __.keys():   # Main mem clean
                            pass
                        # -----------------------------------------------------#
                        else:
                            # 개인이 만든 메모리 초기화
                            self.p_shut('기타 메모리 정리 시작')
                            for dic_key_value in self.all_mem[nub_mem].keys():
                                self.all_mem[nub_mem][dic_key_value] = self.recover_initial_mem[nub_mem][dic_key_value]
                    if type(__).__name__ == 'ListProxy':    # List clear
                        __[:] = [] # List mem clean
                    nub_mem += 1
                self.clean_signal_mem['Clean'] = False
                self.clean_signal_mem['Normal'] = True
                self.p_shut('메모리 정리 완료')
            time.sleep(0.1)