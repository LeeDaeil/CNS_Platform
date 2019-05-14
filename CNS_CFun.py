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

    def run(self):
        while True:
            if self.clean_signal_mem['Clean']:
                if not self.shut_up:
                    print(self, 'Clean Mem')
                # ------------------------------------------------------------#
                # save data part
                if True:
                    temp = pd.DataFrame()
                    if len(self.db_mem['KFIGIV']['L']) > 2:     # 아무의미없는 KFIGIV
                        for keys in self.db_mem.keys():
                            print(keys, len(self.db_mem[keys]['L']))
                            temp[keys] = self.db_mem[keys]['L']
                        now = time.localtime()
                        s = "%02d-%02d_%02d_%02d_%02d_%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_min,
                                                               now.tm_sec)
                        temp.to_csv('{}_{}.csv'.format(self.name, s))
                        print('Save_db')
                    else:
                        print('불충분한 저장 요건으로 파일저장 pass')
                # ------------------------------------------------------------#
                nub_mem = 0
                for __ in self.all_mem[:-1]:
                    # print(type(__).__name__) Show shared memory type
                    if type(__).__name__ == 'DictProxy':    # Dict clear

                        # ----------------------------------------------------#
                        if 'KFIGIV' in __.keys():   # Main mem clean
                            dumy = deepcopy(__)
                            for dumy_key in dumy.keys():
                                dumy[dumy_key]['L'].clear()
                                dumy[dumy_key]['D'].clear()
                            for _ in dumy.keys():
                                __[_] = dumy[_]
                        # -----------------------------------------------------#
                        else:
                            # 개인이 만든 메모리 초기화
                            for dic_key_value in self.all_mem[nub_mem].keys():
                                self.all_mem[nub_mem][dic_key_value] = self.recover_initial_mem[nub_mem][dic_key_value]

                    if type(__).__name__ == 'ListProxy':    # List clear
                        __[:] = [] # List mem clean
                    nub_mem += 1
                self.clean_signal_mem['Clean'] = False
                self.clean_signal_mem['Normal'] = True
            time.sleep(0.1)