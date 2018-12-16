import multiprocessing
import socket
from struct import unpack
from copy import deepcopy
from time import sleep

class UDPSocket(multiprocessing.Process):
    def __init__(self, mem, IP, Port, shut_up = False):
        multiprocessing.Process.__init__(self)
        self.address = (IP, Port)

        self.mem = mem

        self.old_CNS_data = deepcopy(self.mem[0])   # main mem copy
        self.read_CNS_data = deepcopy(self.mem[0])

        self.shut_up = shut_up

    def run(self):
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.bind(self.address)
        while True:
            data, client = udpSocket.recvfrom(4008)
            pid_list = self.update_mem(data)
            if self.old_CNS_data['KCNTOMS']['L'] == []:
                if not self.shut_up:
                    print('List mem empty')
                for _ in self.read_CNS_data.keys():
                    self.old_CNS_data[_]['V'] = self.read_CNS_data[_]['V']
                    self.old_CNS_data[_]['L'].append(self.read_CNS_data[_]['V'])
                    self.old_CNS_data[_]['D'].append(self.read_CNS_data[_]['V'])

                    # self.old_CNS_data[_]['N_V'] = self.read_CNS_data[_]['N_V']
                    # self.old_CNS_data[_]['N_L'].append(self.read_CNS_data[_]['N_V'])
                    # self.old_CNS_data[_]['N_D'].append(self.read_CNS_data[_]['N_V'])

            if self.read_CNS_data['KCNTOMS']['V'] == 0:
                if self.old_CNS_data['KCNTOMS']['D'][-1] != self.read_CNS_data['KCNTOMS']['V']:
                    self.mem[-1]['Clean'] = True
                    if not self.shut_up:
                        print(self, 'Memory clear')
                    sleep(0.2) # 조정이 필요함.
                    self.old_CNS_data = deepcopy(self.mem[0])  # main mem copy
                    self.read_CNS_data = deepcopy(self.mem[0])
                    for __ in self.old_CNS_data.keys():
                        self.mem[0][__] = self.old_CNS_data[__]
                else:
                    if not self.shut_up:
                        print(self, 'initial stedy')
                    for __ in self.old_CNS_data.keys():
                        self.mem[0][__] = self.old_CNS_data[__]
                    pass
            else:   # not 0
                if self.old_CNS_data['KCNTOMS']['D'][-1] != self.read_CNS_data['KCNTOMS']['V']:
                    if not self.shut_up:
                        print(self, 'run CNS')
                    for _ in self.read_CNS_data.keys():
                        self.old_CNS_data[_]['V'] = self.read_CNS_data[_]['V']
                        self.old_CNS_data[_]['L'].append(self.read_CNS_data[_]['V'])
                        self.old_CNS_data[_]['D'].append(self.read_CNS_data[_]['V'])

                        # self.old_CNS_data[_]['N_V'] = self.read_CNS_data[_]['N_V']
                        # self.old_CNS_data[_]['N_L'].append(self.read_CNS_data[_]['N_V'])
                        # self.old_CNS_data[_]['N_D'].append(self.read_CNS_data[_]['N_V'])

                    for __ in self.old_CNS_data.keys():
                        self.mem[0][__] = self.old_CNS_data[__]
                else:
                    if not self.shut_up:
                        print(self, 'stop CNS')
                    pass

    def update_mem(self, data):
        pid_list = []
        for i in range(0, 4000, 20):
            sig = unpack('h', data[24 + i: 26 + i])[0]
            para = '12sihh' if sig == 0 else '12sfhh'
            pid, val, sig, idx = unpack(para, data[8 + i:28 + i])
            pid = pid.decode().rstrip('\x00')  # remove '\x00'
            if pid != '':
                self.read_CNS_data[pid] = {'V': val, 'type': sig}
                # self.read_CNS_data[pid] = {'V': val, 'type': sig, 'N_V': val}
                pid_list.append(pid)
        return pid_list

    # def generate_noise(self, para):
    #
    #     para_add_noise = para * 0.1
    #     return para_add_noise