import multiprocessing
import time


class Power_increase_module(multiprocessing.Process):
    def __init__(self, mem, shut):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]  # main mem connection
        self.trig_mem = mem[-1]  # main mem connection
        self.shut = shut

        # self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal('192.168.0.24', 7001)

    def p_shut(self, txt):
        if not self.shut:
            print(self, txt)

    def run(self):
        while True:
            #==========================================================================================#
            if self.mem['KCNTOMS']['V'] == 0:
                self.p_shut('초기 조건 상태가 감지 - 모듈 대기')
                self.mem_len = len(self.mem['KCNTOMS']['L'])
            # ==========================================================================================#
            else:
                if self.mem_len == len(self.mem['KCNTOMS']['L']):
                    self.p_shut('CNS가 정지된 상태 - 모듈 대기')
                else:
                    self.p_shut('CNS가 동작 상태 - 모듈 동작')
                    self.mem_len = len(self.mem['KCNTOMS']['L'])
                    input_data = self.make_input_data()
                    print(input_data, self.mem['KCNTOMS']['L'])
            time.sleep(0.5)

    def make_input_data(self):
        temp = []
        for _ in [-13, -11, -9, -7, -5, -3, -1]:
            try:
                temp.append(self.mem['KCNTOMS']['L'][_])
            except:
                pass
        return temp



