import multiprocessing
import time

class TSMS(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]

    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['L']) > 2:
            # ==========================================================================================#
                print(self, self.mem['QPROREL'])
                time.sleep(1)