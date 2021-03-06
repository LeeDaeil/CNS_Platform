from multiprocessing import Manager
from db import db_make
from collections import deque
import argparse

from CNS_Platform_controller import interface_function
# from Module_Tester.EX_interface import interface_function
from CNS_Run_Freeze import RUN_FREEZE
from CNS_All_module import All_Function_module
import CNS_Platform_PARA as PARA

class body:
    def __init__(self):
        import AUTO_UI_TO_PY
        # 초기 입력 인자 전달 -------------------------------------------------------------------- #
        parser = argparse.ArgumentParser(description='CNS 플랫폼_Ver0')
        parser.add_argument('--comip', type=str, default='', required=False, help="현재 컴퓨터의 ip [default='']")
        parser.add_argument('--comport', type=int, default=7101, required=False, help="현재 컴퓨터의 port [default=7001]")
        parser.add_argument('--cnsip', type=str, default='192.168.0.103', required=False, help="CNS 컴퓨터의 ip [default='']")
        parser.add_argument('--cnsport', type=int, default=7101, required=False, help="CNS 컴퓨터의 port [default=7001]")
        self.args = parser.parse_args()
        print('=' * 25 + '초기입력 파라메터' + '=' * 25)

        with open('CNS_Info.txt', 'w') as f:                             # 타기능에서 CNS 정보 확인 용
            f.write(f'{self.args.cnsip}\t{self.args.cnsport}')

        print(self.args)
        self.shared_mem = generate_mem().make_mem_structure()
        # ---------------------------------------------------------------------------------------- #
        pro_list = [RUN_FREEZE(self.shared_mem, IP=self.args.comip, Port=self.args.comport),    # [1]
                    interface_function(self.shared_mem),                                        # [2]
                    All_Function_module(self.shared_mem)                                        # [3]
                    ]
        self.process_list = pro_list

    def start(self):
        [_.start() for _ in self.process_list]
        [_.join() for _ in self.process_list]


class generate_mem:
    def make_clean_mem(self):
        memory_dict = {'Clean': True, 'Loop': False, 'Run': False, 'Speed': 1,
                       'Auto': False,           # Auto : autonomous[True], manual[False]
                       'Rq_man': False,         # Auto : 운전원 개입 요청 [True], 자율 운전 중 [False]
                       # Operation Strategy His
                       'OPStrategy': PARA.Normal,      # Normal, Abnormal, Em
                       'ST_OPStratey': PARA.ST_OP,
                       'OpStrategy_detail': '',     #
                       'OPStrategy_his': deque(maxlen=2),
                       # Event Diagnosis His
                       'Event_DIG_His': {'X': deque(maxlen=20), 'Y': deque(maxlen=20)},
                       # Rod His
                       'Rod_His': {'X': [], 'Y_avg': [], 'Y_up_dead': [], 'Y_down_dead': [], 'Y_pow': [],
                                   'Y_up_op': [], 'Y_down_op': [], 'Y_ax': []},
                       # PZR His - 가압기 기포 생성 모듈
                       'PZR_His': {'X': deque(maxlen=50), 'Y_pre': deque(maxlen=50), 'Y_temp': deque(maxlen=50),
                                   'Y_lv': deque(maxlen=50), 'Y_val': deque(maxlen=50), 'Y_het': deque(maxlen=50)},
                       # CNS 건너띄기
                       'CNS_SPEED': 5,
                       # 순환 카운터
                       'TEMP_CONT': 0
                       }
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
