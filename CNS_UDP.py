import threading
import socket
from struct import unpack

class UDPSocket(threading.Thread):
    def __init__(self, IP, Port):
        threading.Thread.__init__(self)
        self.address = (IP, Port)
        self.list_initial = True
        self.list_mem, self.mem, self.cns_time = {}, {}, 0

    def run(self):
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.bind(self.address)
        while True:
            data, client = udpSocket.recvfrom(4008)
            self.update_mem(data)
            #print(self.name, client, self.mem['QPROLD'], self.list_mem['QPROLD'], self.list_mem['CNS_time'])

    def update_mem(self, data):
        for i in range(0, 4000, 20):
            sig = unpack('h', data[24 + i: 26 + i])[0]
            para = '12sihh' if sig == 0 else '12sfhh'
            pid, val, sig, idx = unpack(para, data[8 + i:28 + i])
            pid = pid.decode().rstrip('\x00')  # remove '\x00'
            if pid != '':
                self.mem[pid] = {'Val': val, 'Sig': sig, 'Idx': idx}

        if self.list_initial is True:
            self.cns_time = 0
            for __ in self.mem.keys():
                self.list_mem[__] = {'Val': [self.mem[__]['Val']], 'Sig': self.mem[__]['Sig'],
                                     'Idx': self.mem[__]['Idx']}
            self.list_initial = False

        if self.mem['KCNTOMS']['Val'] == 0 and self.cns_time == 0:
            self.cns_time = 0
            for __ in self.mem.keys():
                self.list_mem[__] = {'Val': [self.mem[__]['Val']], 'Sig': self.mem[__]['Sig'],
                                     'Idx': self.mem[__]['Idx']}
        elif self.mem['KCNTOMS']['Val'] == 0 and self.cns_time != 0:
            self.cns_time = 0
            for __ in self.mem.keys():
                self.list_mem[__] = {'Val': [self.mem[__]['Val']], 'Sig': self.mem[__]['Sig'],
                                     'Idx': self.mem[__]['Idx']}

        elif self.mem['KCNTOMS']['Val'] != 0:
            if self.mem['KCNTOMS']['Val'] // 5 != self.cns_time:
                for __ in self.mem.keys():
                    data_ = self.mem[__]['Val']
                    self.list_mem[__]['Val'].append(data_)
                self.cns_time = self.mem['KCNTOMS']['Val'] // 5

        self.list_mem['CNS_time'] = {'Val': []}
        for __ in range(0, len(self.list_mem['KCNTOMS']['Val'])):
            self.list_mem['CNS_time']['Val'].append(__)



