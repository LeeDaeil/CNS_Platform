import multiprocessing
import time
import CNS_Send_UDP

class function1(multiprocessing.Process):
    ## 단순한 값만 읽어 오는 예제
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0] # main mem connection

    def run(self):
        while True:
            print(self, self.mem['KFZRUN'])
            time.sleep(1)


class function2(multiprocessing.Process):
    ## 제어 신호 보내는 예제
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem
        self.mem2 = mem[2]

        # UDP send part
        self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal('192.168.0.55', 7001)

    def run(self):
        while True:
            # print(self, self.mem[1]['Test'], '->', 1, self.mem2)
            self.mem[1]['Test'] = 1
            self.mem[2].append(1)
            print('send')
            self.UDP_sock._send_control_signal(['KSWO33', 'KSWO32'], [1, 0])
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

#========================================================================


class t_function1(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0] # main mem connection

    def run(self):
        para = ['KMSISO']
        while True:
            print(self, self.mem['KCNTOMS']['V'])
            time.sleep(1)