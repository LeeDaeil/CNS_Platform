from Main import generate_mem, body
import unittest


class Test_esay_function(unittest.TestCase):
    def test_easy_function(self):
        a = [0, 1, 2, 3]
        print(a[:-1])

    def test_2(self):
        a = {'aa': 3, 'bb': 4}
        if 'aa' in a.keys():
            print('TT')


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
        body().start()
