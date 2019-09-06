from multiprocessing import Manager
from Module_Tester.EX_db import db_make
from Module_Tester.EX_interface import *
from Module_Tester.EX_RUN_Module import *
from Module_Tester.EX_Module import *
import argparse


class body:
    def __init__(self):
        # 초기 입력 인자 전달 -------------------------------------------------------------------- #
        parser = argparse.ArgumentParser(description='CNS 플랫폼_TE Ver')
        parser.add_argument('--comip', type=str, default='', required=False, help="현재 컴퓨터의 ip [default='']")
        parser.add_argument('--comport', type=int, default=7001, required=False, help="현재 컴퓨터의 port [default=7001]")
        parser.add_argument('--cnsip', type=str, default='192.168.0.100', required=False, help="현재 컴퓨터의 ip [default='']")
        parser.add_argument('--cnsport', type=int, default=7003, required=False, help="현재 컴퓨터의 port [default=7001]")
        self.args = parser.parse_args()
        print('=' * 25 + '초기입력 파라메터' + '=' * 25)

        with open('EX_pro.txt', 'w') as f:                             # 타기능에서 CNS 정보 확인 용
            f.write(f'{self.args.cnsip}\t{self.args.cnsport}')

        print(self.args)
        self.shared_mem = generate_mem().make_mem_structure()
        # ---------------------------------------------------------------------------------------- #
        pro_list = [RUN_FREEZE(self.shared_mem, IP=self.args.comip, Port=self.args.comport),    # [1]
                    interface_function(self.shared_mem),                                        # [2]
                    EX_module(self.shared_mem)                                                  # [3]
                    ]
        self.process_list = pro_list

    def start(self):
        [_.start() for _ in self.process_list]
        [_.join() for _ in self.process_list]


class generate_mem:
    def make_clean_mem(self):
        memory_dict = {'Clean': True, 'Loop': False, 'Run': False}
        print('Clean 메모리 생성 완료')
        return memory_dict

    def make_main_mem_structure(self, max_len_deque=10):
        memory_dict = db_make().make_db_structure(max_len_deque)
        print('Main 메모리 생성 완료')
        return memory_dict

    def make_mem_structure(self):
        print('=' * 25 + '메모리 생성 시작' + '=' * 25)
        memory_list = [Manager().dict(self.make_main_mem_structure(max_len_deque=10)),    # [0]
                       Manager().dict(self.make_clean_mem()),                             # [-1]
                       ]
        print('=' * 25 + '메모리 생성 완료' + '=' * 25)
        return memory_list


if __name__ == '__main__':
    main_process = body()
    main_process.start()
