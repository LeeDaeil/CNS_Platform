import multiprocessing
import socket
import sys
from struct import unpack

from copy import *
from time import sleep
from Module_Tester.EX_CNS_Send_UDP import *


class RUN_FREEZE_FAST(multiprocessing.Process):
    def __init__(self, mem, IP, Port):
        multiprocessing.Process.__init__(self)
        self.address = (IP, Port)

        self.mem = mem[0]   # main mem connection
        self.trig_mem = mem[-1]  # main mem connection
        self.call_cns_udp_sender()

        self.CNS_data = deepcopy(self.mem)

        # SIZE BUFFER
        self.size_buffer_mem = 46008
        # SEND TICK
        self.want_tick = 5

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
                self.CNS_data[pid]['type'] = sig
                # pid_list.append(pid)

        # Mal function 발생 시간 및 사고 기록
        if 'Normal_0' in self.CNS_data.keys():
            accident_neb = self.CNS_data['KSWO280']['V']
            # Nor / Ab
            if self.CNS_data['KSWO278']['V'] >= self.CNS_data['KCNTOMS']['V']:
                self.CNS_data['Normal_0']['V'] = 0
                self.CNS_data['Accident_nub']['V'] = 0
                self.CNS_data[f'Accident_{accident_neb}']['V'] = 0
            else:
                self.CNS_data['Normal_0']['V'] = 1
                condition_fun = {12: 1, 15: 1, 13: 2, 18: 3, 52: 3, 17: 4} # LOCA, SGTR, MSLB, MFWB
                self.CNS_data['Accident_nub']['V'] = condition_fun[accident_neb]
                self.CNS_data[f'Accident_{accident_neb}']['V'] = 1

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
                data, client = udpSocket.recvfrom(self.size_buffer_mem)
                pid_list = self.update_mem(data[8:])  # 주소값을 가지는 8바이트를 제외한 나머지 부분

                # Run 버튼 누르면 CNS 동작하는 모듈
                if self.trig_mem['Loop'] and self.trig_mem['Run'] is False:
                    self.CNS_udp._send_control_signal(['KFZRUN'], [self.want_tick+100]) # 400 - 100 -> 300 tick 20 sec
                    while True:
                        data, client = udpSocket.recvfrom(self.size_buffer_mem)
                        pid_list = self.update_mem(data[8:])  # 주소값을 가지는 8바이트를 제외한 나머지 부분
                        if self.CNS_data['KFZRUN']['V'] == 4 or self.CNS_data['KFZRUN']['V'] == 10:
                            [self.update_local_mem(key) for key in self.CNS_data.keys()]
                            self.trig_mem['Run'] = True
                            break

                # CNS 초기화 선언시 모든 메모리 초기화
                if self.CNS_data['KFZRUN']['V'] == 6:
                    [self.CNS_data[_]['L'].clear() for _ in self.CNS_data.keys()]
                    [self.CNS_data[_]['D'].clear() for _ in self.CNS_data.keys()]
                    print("CNS 메모리 초기화 완료")

                [self.update_cns_to_mem(key) for key in self.mem.keys()]  # 메인 메모리 업데이트
            except Exception as e:
                print(f"CNS time out {e}")
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
