import multiprocessing
import socket
from struct import unpack

from copy import *
from time import sleep
from Module_Tester.EX_CNS_Send_UDP import *


class RUN_FREEZE(multiprocessing.Process):
    def __init__(self, mem, IP, Port):
        multiprocessing.Process.__init__(self)
        self.address = (IP, Port)

        self.mem = mem[0]   # main mem connection
        self.trig_mem = mem[-1]  # main mem connection
        self.call_cns_udp_sender()

        self.CNS_data = deepcopy(self.mem)

    # --------------------------------------------------------------------------------
    def call_cns_udp_sender(self):
        # CNS 정보 읽기
        with open('EX_pro.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')   # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

    # --------------------------------------------------------------------------------

    def update_mem(self, data):
        pid_list = []
        # print(len(data)) data의 8바이트를 제외한 나머지 버퍼의 크기
        for i in range(0, len(data), 20):
            sig = unpack('h', data[16 + i: 18 + i])[0]
            para = '12sihh' if sig == 0 else '12sfhh'
            pid, val, sig, idx = unpack(para, data[i:20 + i])

            pid = pid.decode().rstrip('\x00')  # remove '\x00'
            if pid != '':
                self.CNS_data[pid]['V'] = val
                self.CNS_data[pid]['type']= sig
                # pid_list.append(pid)
        return pid_list

    def update_cns_to_mem(self, key):
        self.mem[key] = self.CNS_data[key]

    def update_local_mem(self, key):
        self.CNS_data[key]['L'].append(self.CNS_data[key]['V'])
        self.CNS_data[key]['D'].append(self.CNS_data[key]['V'])

    def run(self):
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.bind(self.address)
        udpSocket.settimeout(5)     # 5초 대기 후 연결 없으면 연결 안됨을 호출

        while True:
            try:
                data, client = udpSocket.recvfrom(44388)
                pid_list = self.update_mem(data[8:])  # 주소값을 가지는 8바이트를 제외한 나머지 부분

                # Run 버튼 누르면 CNS 동작하는 모듈
                if self.trig_mem['Loop'] and self.trig_mem['Run'] is False:
                    self.CNS_udp._send_control_signal(['KFZRUN'], [3])
                    while True:
                        data, client = udpSocket.recvfrom(44388)
                        pid_list = self.update_mem(data[8:])  # 주소값을 가지는 8바이트를 제외한 나머지 부분
                        if self.CNS_data['KFZRUN']['V'] == 4 or self.CNS_data['KFZRUN']['V'] == 10:
                            [self.update_local_mem(key) for key in self.CNS_data.keys()]
                            self.trig_mem['Run'] = True
                            break

                # CNS 초기화 선언시 모든 메모리 초기화
                if self.CNS_data['KFZRUN']['V'] == 1:
                    [self.CNS_data[_]['L'].clear() for _ in self.CNS_data.keys()]
                    [self.CNS_data[_]['D'].clear() for _ in self.CNS_data.keys()]

                [self.update_cns_to_mem(key) for key in self.mem.keys()]  # 메인 메모리 업데이트
            except Exception as f:
                print("CNS time out")