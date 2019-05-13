from Main import generate_mem, body
from Net_Test import C_LSTM_Test
from Value_test_Main import body as tese_body
from CNS_UDP import UDPSocket
import unittest


class Test_UDP(unittest.TestCase):
    def test_run(self):
        mem = generate_mem().make_mem_structure()
        UDPSocket(mem, IP='', Port=7001)


class Test_esay_function(unittest.TestCase):
    def test_easy_function(self):
        a = [0, 1, 2, 3]
        print(a[:-1])

    def test_2(self):
        a = {'aa': 3, 'bb': 4}
        if 'aa' in a.keys():
            print('TT')


class Test_network(unittest.TestCase):
    def test_C_LSTM(self):
        C_LSTM_Test().run()

    def test_C_LSTM_array(self):
        C_LSTM_Test().make_array()


class Test_module_for_generate_mem(unittest.TestCase):
    def test_main_mem_structure(self):
        generate_mem().make_main_mem_structure(True)

    def test_mem_structure(self):
        '''
        메모리 생성여부 및 생성된 메모리의 리스트 반환
        '''
        generate_mem().make_mem_structure(True)


class Test_module_for_main(unittest.TestCase):
    def test_main_start(self):
        '''
        기본적인 메인 바디 시작
        '''
        body().start()

class Test_A3C_module_for_main(unittest.TestCase):
    def test_main_start(self):
        '''
        A3C 테스터 동작 부분
        '''
        tester = body()
        tester.a3c_test_mode = True
        tester.start()

# import CNS_TSMS
# class Test_TSMS_module(unittest.TestCase):
#     def test_t_1(self):
#