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

    def _send_malfunction_signal(self, Mal_nub, Mal_opt, Mal_time):
        '''
        CNS_04_18.tar 버전에서 동작함.
        :param Mal_nub: Malfunction 번호
        :param Mal_opt: Malfunction operation
        :param Mal_time: Malfunction의 동작하는 시간
        :return:
        '''
        if Mal_time == 0:
            Mal_time = 5
        else:
            Mal_time = Mal_time * 5
        return self._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                         [10, Mal_nub, Mal_opt, Mal_time])

if __name__ == '__main__':
    import time
    test_udp_send = CNS_Send_Signal('192.168.0.93', 7101)
    Test_1 = False  # 일반적인 UDP 테스트
    if Test_1:
        while True:
            # print('CNS 동작 테스트')
            # test_udp_send._send_control_signal(['KFZRUN'], [3])
            # time.sleep(5)
            # print('CNS 초기 조건 테스트')
            # test_udp_send._send_control_signal(['KFZRUN'], [5])
            # time.sleep(5)
            # print('CNS Malfunction 테스트')
            # test_udp_send._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'], [10, 12, 100100, 5]) # 10은 멜펑션
            # print('CNS 값 전송 테스트')
            # test_udp_send._send_control_signal(['KSWO280'], [2])
            time.sleep(1)
            pass
    Test_2 = False # CNS의 Malfunction 원격 조작을 위한 로직
    if Test_2:
        while True:
            print('CNS 동작 후 정지')
            test_udp_send._send_control_signal(['KFZRUN'], [3])
            time.sleep(2)
            print('CNS Malfunction 입력')
            test_udp_send._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                               [10, 12, 100100, 5])  # 10은 멜펑션
            time.sleep(2)
            print('CNS 동작 후 정지')
            test_udp_send._send_control_signal(['KFZRUN'], [3])
            time.sleep(2)
            print('CNS 동작 후 정지')
            test_udp_send._send_control_signal(['KFZRUN'], [3])
            time.sleep(2)
    Test_3 = True # CNS의 Malfunction 원격 조작을 위한 로직
    if Test_3:
        while True:
            print('CNS 동작 후 정지')
            test_udp_send._send_control_signal(['KFZRUN'], [105])
            time.sleep(2)
            print('CNS Malfunction 입력')
            test_udp_send._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                               [10, 12, 100100, 5])  # 10은 멜펑션
            time.sleep(2)
            print('CNS 동작 후 정지')
            test_udp_send._send_control_signal(['KFZRUN'], [105])
            time.sleep(2)
            print('CNS 동작 후 정지')
            test_udp_send._send_control_signal(['KFZRUN'], [105])
            time.sleep(2)
