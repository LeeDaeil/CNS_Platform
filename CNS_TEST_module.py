import multiprocessing
from time import sleep


class EX_module(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)

        self.mem = mem[0]  # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

    def run(self):
        while True:
            if self.trig_mem['Loop'] and self.trig_mem['Run']:
                print('계산중....', end='\t')
                # sleep(1)
                print('계산 종료! ....', end='\t')
                print(self, self.mem['KCNTOMS'], self.trig_mem['Loop'], self.trig_mem['Run'])
                self.trig_mem['Run'] = False