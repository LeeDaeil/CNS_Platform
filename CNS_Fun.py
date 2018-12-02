import multiprocessing
import time
from copy import deepcopy


class function1(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0] # main mem connection

    def run(self):
        while True:
            print(self, self.mem['KCNTOMS'])
            time.sleep(1)


class function2(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem
        self.mem2 = mem[2]

    def run(self):
        while True:
            # print(self, self.mem[1]['Test'], '->', 1, self.mem2)
            self.mem[1]['Test'] = 1
            self.mem[2].append(1)
            time.sleep(1)


class function3(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem
        self.mem2 = mem[2]

    def run(self):
        while True:
            # print(self, self.mem[1]['Test'], '->', 2, self.mem2)
            self.mem[1]['Test'] = 2
            self.mem[2].append(2)
            time.sleep(3)


class clean_mem(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.all_mem = mem
        self.clean_signal_mem = mem[-1]

    def run(self):
        while True:
            if self.clean_signal_mem['Clean']:
                print(self, 'Clean Mem')
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

                    if type(__).__name__ == 'ListProxy':    # List clear
                        __[:] = [] # List mem clean
                self.clean_signal_mem['Clean'] = False
            time.sleep(0.1)