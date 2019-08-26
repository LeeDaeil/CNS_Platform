import multiprocessing
import socket
from struct import unpack
from copy import deepcopy
from time import sleep
import time
import pandas as pd
import LIGHT


class UDPSocket(multiprocessing.Process):
    def __init__(self, mem, IP, Port, shut_up = False):
        multiprocessing.Process.__init__(self)
        self.address = (IP, Port)

        self.mem = mem
        self.trigger_mem = mem[-1]   # Clean mem -> 'Normal':True
        # self.TSMS_mem = mem[-3]

        self.old_CNS_data = deepcopy(self.mem[0])   # main mem copy
        self.read_CNS_data = deepcopy(self.mem[0])

        self.shut_up = shut_up

        self.initial_save = False # 초기 상태가 호출된 경우 1번만 저장하는 기능

        now = time.localtime()
        s = "%02d-%02d_%02d_%02d_%02d_%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_min,
                                               now.tm_sec)
        self.save_file_name = '{}.csv'.format(s)

        # 일정 시간마다 데이터 저장 용 타이머
        self.history_min = time.localtime().tm_min

    def run(self):
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.bind(self.address)
        udpSocket.settimeout(5)     # 5초 대기 후 연결 없으면 연결 안됨을 호출

        # data, client = udpSocket.recvfrom(44388) # 최대 버퍼 수
        while True:
            # try:
            data, client = udpSocket.recvfrom(44388)
            # print(len(data))
            pid_list = self.update_mem(data[8:]) # 주소값을 가지는 8바이트를 제외한 나머지 부분

            # 코드가 처음 돌때만 동작 ----------------------
            if self.old_CNS_data['KCNTOMS']['L'] == []:
                if not self.shut_up: print('List mem empty')
                self.update_old_CNS_data()
            # ----------------------------------------------

            if self.read_CNS_data['KCNTOMS']['V'] == 0:
                if self.old_CNS_data['KCNTOMS']['L'][-1] != self.read_CNS_data['KCNTOMS']['V']:
                    self.mem[-1]['Clean'] = True
                    if not self.shut_up: print(self, 'Memory clear')

                    dumy = deepcopy(self.mem[0])
                    for dumy_key in dumy.keys():
                        dumy[dumy_key]['L'].clear()
                        dumy[dumy_key]['D'].clear()
                    for _ in dumy.keys():
                        self.mem[0][_] = dumy[_]

                    self.old_CNS_data = deepcopy(self.mem[0])  # main mem copy
                    self.read_CNS_data = deepcopy(self.mem[0])
                    for __ in self.old_CNS_data.keys():
                        self.mem[0][__] = self.old_CNS_data[__]
                else:
                    if not self.shut_up: print(self, 'initial stedy')

                    # 초기 상태인 경우 수집된 데이터를 저장하기위한 파일 이름을 선정 -------
                    now = time.localtime()
                    s = "%02d-%02d_%02d_%02d_%02d_%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_min,
                                                           now.tm_sec)
                    self.save_file_name = '{}.csv'.format(s)
                    self.initial_save = False  # 초기 상태가 호출된 경우 1번만 저장하는 기능
                    # ---------------------------------------------------------

                    for __ in self.old_CNS_data.keys():
                        self.old_CNS_data[__]['V'] = self.read_CNS_data[__]['V'] # 초기 상태여도 V는 업데이트
                        self.mem[0][__] = self.old_CNS_data[__]

            else:   # not 0
                if self.old_CNS_data['KCNTOMS']['D'][-1] != self.read_CNS_data['KCNTOMS']['V']:
                    if not self.shut_up: print(self, 'run CNS')
                    self.initial_save = False  # run에서 stop으로 상태가 바뀔때 데이터 저장을 위해서 사용

                    # 일정 시간마다 데이터 저장하는 파트 -------
                    if self.history_min != time.localtime().tm_min:
                        self.save_file(self.save_file_name)
                        self.history_min = time.localtime().tm_min  #timer  업데이터
                    # ------------------------------------------

                    self.update_old_CNS_data()

                    for __ in self.old_CNS_data.keys():
                        self.mem[0][__] = self.old_CNS_data[__]
                else:
                    if not self.shut_up: print(self, 'stop CNS')
                    self.save_file(self.save_file_name)
                    pass
            # except Exception as e:
            #     print(e)

    def update_mem(self, data):
        pid_list = []
        # print(len(data)) data의 8바이트를 제외한 나머지 버퍼의 크기
        for i in range(0, len(data), 20):
            sig = unpack('h', data[16 + i: 18 + i])[0]
            para = '12sihh' if sig == 0 else '12sfhh'
            pid, val, sig, idx = unpack(para, data[i:20 + i])

            pid = pid.decode().rstrip('\x00')  # remove '\x00'
            if pid != '':
                self.read_CNS_data[pid] = {'V': val, 'type': sig}
                # self.read_CNS_data[pid] = {'V': val, 'type': sig, 'N_V': val}
                pid_list.append(pid)
        return pid_list

    def append_value_to_old_CNS_data(self, key, value):
        self.old_CNS_data[key]['V'] = value
        if LIGHT.LIGHT:
            if len(self.old_CNS_data[key]['L']) > 0:
                pass
            else:
                self.old_CNS_data[key]['L'].append(value)
        else:
            self.old_CNS_data[key]['L'].append(value)
        self.old_CNS_data[key]['D'].append(value)

    def update_other_state_to_old_CNS_data(self, para, value):
        for length in range(0, len(para)):
            self.append_value_to_old_CNS_data(key=para[length], value=value[length])

    def update_old_CNS_data(self):

        for _ in self.read_CNS_data.keys():
            self.append_value_to_old_CNS_data(key=_, value=self.read_CNS_data[_]['V'])
            if _ == 'KFZRUN': break # CNS에서 제공하는 DB까지 읽고 나머지는 아래에서 수동으로 업데이트

        # 정상 상태 라벨링 업데이트
        temp_list = [1, 0] if self.trigger_mem['Normal'] else [0, 1]
        self.update_other_state_to_old_CNS_data(['Normal_0', 'Normal_1'], temp_list)

        # 비상 상태 라벨링 업데이트
        temp_list = [0, 0, 0, 0, 0, 0, 0]
        temp_list[self.trigger_mem['Accident_nb']] = 1
        self.update_other_state_to_old_CNS_data(['Accident_0', 'Accident_1', 'Accident_2', 'Accident_3',
                                                 'Accident_4', 'Accident_5'], temp_list)

    def save_file(self, file_name):
        if not self.initial_save:
            if not self.shut_up: print(self, 'CNS file save')
            temp = pd.DataFrame()
            if LIGHT.LIGHT:
                for keys in self.mem[0].keys():
                    temp[keys] = self.mem[0][keys]['D']
            else:
                for keys in self.mem[0].keys():
                    temp[keys] = self.mem[0][keys]['L']
            temp.to_csv(file_name)
            self.initial_save = True
