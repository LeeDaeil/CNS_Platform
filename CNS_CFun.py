import multiprocessing
import time
from copy import deepcopy

class clean_mem(multiprocessing.Process):
    def __init__(self, mem, shut_up):
        multiprocessing.Process.__init__(self)
        self.all_mem = mem
        self.clean_signal_mem = mem[-1]

        self.shut_up = shut_up

    def run(self):
        while True:
            if self.clean_signal_mem['Clean']:
                if not self.shut_up:
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