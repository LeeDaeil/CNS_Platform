import multiprocessing
import time
import CNS_Send_UDP


class Data_collector(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]  # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

        self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal('192.168.0.24', 7001)

        self.one_time = 0

    def run(self):
        print('효진이 데이터 파일 수집 시작~')
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['L']) > 0 and self.current_len != len(self.mem['QPROREL']['L']):
                self.current_len = len(self.mem['QPROREL']['L'])
            # ==========================================================================================#
                if len(self.mem['Normal_0']['L']) > 5:
                    self.trig_mem['Normal'] = False
                    if self.one_time == 0:
                        self.UDP_sock._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                                           [10, 12, 100100, 5])  # 10은 멜펑션
                        self.one_time += 1
            time.sleep(1)