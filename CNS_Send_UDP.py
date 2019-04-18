import socket
from struct import pack
from numpy import shape

class CNS_Send_Signal:
    def __init__(self, ip, port):
        self.CNS_ip = ip
        self.CNS_port = port
        self.db_structure = self.initial_db_structure()

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def initial_db_structure(self):
        idx = 0
        db_structure = {}
        with open('./db.txt', 'r') as f:
            while True:
                temp_ = f.readline().split('\t')
                if temp_[0] == '':  # if empty space -> break
                    break
                sig = 0 if temp_[1] == 'INTEGER' else 1
                db_structure[temp_[0]] = {'Sig': sig, 'Val': 0, 'Num': idx}
                idx += 1
        return db_structure

    def _send_control_signal(self, para, val):
        '''
        조작 필요없음
        :param para:
        :param val:
        :return:
        '''
        for i in range(shape(para)[0]):
            self.db_structure[para[i]]['Val'] = val[i]
        UDP_header = b'\x00\x00\x00\x10\xa8\x0f'
        buffer = b'\x00' * 4008
        temp_data = b''

        # make temp_data to send CNS
        for i in range(shape(para)[0]):
            pid_temp = b'\x00' * 12
            pid_temp = bytes(para[i], 'ascii') + pid_temp[len(para[i]):]  # pid + \x00 ..

            para_sw = '12sihh' if self.db_structure[para[i]]['Sig'] == 0 else '12sfhh'

            temp_data += pack(para_sw,
                              pid_temp,
                              self.db_structure[para[i]]['Val'],
                              self.db_structure[para[i]]['Sig'],
                              self.db_structure[para[i]]['Num'])

        buffer = UDP_header + pack('h', shape(para)[0]) + temp_data + buffer[len(temp_data):]

        self.send_sock.sendto(buffer, (self.CNS_ip, self.CNS_port))

if __name__ == '__main__':
    import time
    test_udp_send = CNS_Send_Signal('192.168.0.55', 7001)
    while True:
        # print('CNS 동작 테스트')
        # test_udp_send._send_control_signal(['KFZRUN'], [3])
        # time.sleep(5)
        # print('CNS 초기 조건 테스트')
        # test_udp_send._send_control_signal(['KFZRUN'], [5])
        # time.sleep(5)
        # print('CNS Malfunction 테스트')
        # test_udp_send._send_control_signal(['KFZRUN'], [10]) # 10은 멜펑션
        pass
