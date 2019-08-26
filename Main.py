from db import db_make
from multiprocessing import Manager
from CNS_UDP import *
from CNS_Fun import *
# from CNS_Power import Power_increase_module as PI_module
from CNS_AB_DIG import Abnormal_dig_module as AB_DIG_module
from CNS_GFun import *
from CNS_CFun import *
from CNS_Interface import *
import argparse

import LIGHT

class body:
    def __init__(self):
        # 초기 입력 인자 전달 -------------------------------------------------------------------- #
        parser = argparse.ArgumentParser(description='CNS 플랫폼')
        parser.add_argument('--comip', type=str, default='', required=False, help="현재 컴퓨터의 ip [default='']")
        parser.add_argument('--comport', type=int, default=7001, required=False, help="현재 컴퓨터의 port [default=7001]")
        parser.add_argument('--cnsip', type=str, default='192.168.0.100', required=False, help="현재 컴퓨터의 ip [default='']")
        parser.add_argument('--cnsport', type=int, default=7003, required=False, help="현재 컴퓨터의 port [default=7001]")
        parser.add_argument('--mode', default='All', required=False, help='구동할 프로레서를 선택 [default="all"]')
        parser.add_argument('--shutup', action="store_false", required=False, help='세부 정보를 출력할 것인지 판단[default=True]')
        parser.add_argument('--PIshutup', action="store_false", required=False, help='세부 정보를 출력할 것인지 판단[default=True]')
        self.args = parser.parse_args()
        print('=' * 25 + '초기입력 파라메터' + '=' * 25)

        with open('pro.txt', 'w') as f:                             # 타기능에서 CNS 정보 확인 용
            f.write(f'{self.args.cnsip}\t{self.args.cnsport}')

        print(self.args)
        self.shared_mem = generate_mem().make_mem_structure()
        # ---------------------------------------------------------------------------------------- #
        self.UDP_net = [UDPSocket(self.shared_mem, IP=self.args.comip, Port=self.args.comport, shut_up=self.args.shutup)]
        print('=' * 25 + ' 소켓통신  개방 ' + '=' * 25 + '\n' + 'Sock Port - {}'.format(self.args.comport) + '\n' +
              '=' * 25 + ' 소켓개방  완료 ' + '=' * 25)
        # ---------------------------------------------------------------------------------------- #
        pro_list = [clean_mem(self.shared_mem, shut_up=self.args.shutup),   # [0]
                    interface_function(self.shared_mem),                    # [1]
                    funtion5(self.shared_mem),                              # [2]
                    Func_diagnosis(self.shared_mem),
                    Func_strategy(self.shared_mem),
                    #PI_module(self.shared_mem, self.args.PIshutup, self.args.cnsip, self.args.cnsport),           # [3]
                    AB_DIG_module(self.shared_mem, self.args.PIshutup),           # [4]
                    ]
        if self.args.mode == 'All':
            self.process_list = pro_list
        elif self.args.mode == 'Test_interface':
            self.process_list = [pro_list[0], pro_list[1]]
        elif self.args.mode == 'Test_mode':
            self.process_list = [pro_list[0], pro_list[1], pro_list[2]]
        elif self.args.mode == 'Test_PI':
            self.process_list = [pro_list[0], pro_list[1], pro_list[3]]
        else:   # Test_clean_mem
            self.process_list = [pro_list[0]]


    def start(self):
        job_list = []
        for __ in self.UDP_net:
            __.start()
            job_list.append(__)
        time.sleep(1)
        for __ in self.process_list:
           __.start()
           job_list.append(__)
        for job in job_list:
            job.join()


class generate_mem:
    def make_autonomous_mem(self):
        memory_dict = {'Man_state': True, 'Auto_state': False, 'Man_require': False,
                       'Current_op': 'LSTM-based algorithm', #'['LSTM-based algorithm', 'Tech Spec action', 'Ruel-based algorithm'],
                       'Strategy_out': ['[00:00:00] Start - Normal Operation - LSTM-base algorithm',
                                        '[00:00:46] Emergency Operation - LSTM-base algorithm'],
                       'Auto_operation_out': ['[00:00:00] Start',
                                              '[00:00:46] Reactor Trip',
                                              '[00:00:57] SI Valve Open',
                                              '[00:00:58] Charging Pump 1 Start',
                                              '[00:00:58] Aux Feed Water Pump 1 Start',
                                              '[00:00:58] Aux Feed Water Pump 3 Start',
                                              '[00:00:59] Aux Feed Water Control Valve (HV313) Open',
                                              '[00:00:59] Aux Feed Water Control Valve (HV315) Open',
                                              '[00:01:25] Aux Feed Water Pump 2 Start',
                                              '[00:01:27] Aux Feed Water Control Valve (HV314) Open',
                                              '[00:02:06] MSIV Close (HV108, HV208, HV308',
                                              '[00:04:36] RCP 1 Stop',
                                              '[00:04:36] RCP 2 Stop',
                                              '[00:04:36] RCP 3 Stop',
                                              ],
                       'Start_up_operation_his': {'time': [], 'power': [], 'up_cond': [], 'low_cond': []}, # Start-up 시 제어봉 제어 결과 표시
                       'Abnormal_Dig_result': {'Result': []},
                       }
        print('자율운전 메모리 생성 완료')
        return memory_dict

    def make_strategy_selection_mem(self):
        memory_dict = {'alarm': [],                         # 0: normal, 1: abnormal, 2: emergency
                       'diagnosis': [],                     # 0: x, 2301: RCS Leak .... Rule) 절차서 번호
                       'training_cond': [],                 # 0: x, 1: Trained, 2: Untrained
                       'operation_mode': [],                # 0: Normal, 1: Abnormal, 2: Emergency
                       'strategy': [],                      # Auto_LSTM # '2301_LSTM' .... Rule) '절차서번호_알고리즘' 1: RCS _LSTM 2: CVCS_RL
                       'control_activation': []}
        print('전략 설정용 메모리 설정 완료')
        return memory_dict

    def make_test_mem(self):
        memory_dict = {'4_1_state': True, '4_2_state': '', '4_4_state': False}
        return memory_dict

    def make_test_list_mem(self):
        memory_list = []
        return memory_list

    def make_CNS_time_mem(self):
        memory_list = []
        return memory_list

    def make_clean_mem(self):
        memory_dict = {'Clean': True, 'Normal': True, 'Accident_nb': 0}
        print('Clean 메모리 생성 완료')
        return memory_dict

    def make_main_mem_structure(self, max_len_deque=10, show_main_mem=False):
        memory_dict = db_make().make_db_structure(max_len_deque)

        # with open('./db.txt', 'r') as f:
        #     while True:
        #         temp_ = f.readline().split('\t')
        #         if temp_[0] == '':  # if empty space -> break
        #             break
        #         sig = 0 if temp_[1] == 'INTEGER' else 1
        #         memory_dict[temp_[0]] = {'V': 0, 'L': [], 'D': deque(maxlen=max_len_deque), "type": sig}
        #         # memory_dict[temp_[0]] = {'V': 0, 'L': [], 'D': deque(maxlen=max_len_deque), "type": sig,
        #         #                          'N_V': 0, 'N_L': [], 'N_D': deque(maxlen=max_len_deque)}  # Noise parameter

        ## DCSCommPid.ini 만드는 기능
        make_DCSCommPid = False
        if make_DCSCommPid:
            with open('./db.txt', 'r') as f:
                nub_line = -1
                while True:
                    temp_ = f.readline().split('\t')
                    if temp_[0] == '':
                        break
                    if nub_line != -1:  # 첫번째 헤더의 내용 제외하고 추가
                        with open('./DCSCommPid.ini', 'a') as f_pid:
                            if nub_line == 0:
                                f_pid.write('{}\t{}\t{}'.format(nub_line, temp_[0], temp_[1]))
                            else:
                                f_pid.write('\n{}\t{}\t{}'.format(nub_line, temp_[0], temp_[1]))
                    nub_line += 1

        if show_main_mem:
            print(memory_dict)
        print('Main 메모리 생성 완료')
        return memory_dict

    def make_mem_structure(self, show_mem_list=False):
        print('=' * 25 + '메모리 생성 시작' + '=' * 25)
        if LIGHT.LIGHT:
            # LIGHT 버전이 동작하고 있으면 메모리에서는 'L'에 데이터를 축적하지 않음.
            # 모든 데이터는 일회성 'D' 에 기입됨.
            print('=' * 25 + '라이트 버전으로 동작' + '=' * 25)
            memory_list = [Manager().dict(self.make_main_mem_structure(max_len_deque=50)),  # [0]
                           Manager().dict(self.make_strategy_selection_mem()),              # [1]
                           # Manager().dict(self.make_diagnosis_mem()),                     # [1]
                           # Manager().dict(self.make_strategy_mem()),                      # [2]
                           Manager().dict(self.make_autonomous_mem()),                      # [-2]
                           Manager().dict(self.make_clean_mem()),                           # [-1]
                           ]
        else:
            memory_list = [Manager().dict(self.make_main_mem_structure(max_len_deque=10)),  # [0]
                           Manager().dict(self.make_strategy_selection_mem()),              # [1]
                           # Manager().dict(self.make_diagnosis_mem()),                     # [1]
                           # Manager().dict(self.make_strategy_mem()),                      # [2]
                           Manager().dict(self.make_autonomous_mem()),                      # [-2]
                           Manager().dict(self.make_clean_mem()),                           # [-1]
                           ]
        print('=' * 25 + '메모리 생성 완료' + '=' * 25)
        '''
        개인이 설계한 메모리를 추가로 집어 넣을 것.
        ex) 
            memory_list = [Manager().dict(self.make_main_mem_structure(max_len_deque=10)),
                           Manager().dict(자신이 설계한 메모리 구조)),
                           ...
                           Manager().dict(self.make_clean_mem()),]
        '''
        if show_mem_list:
            i = 0
            for __ in memory_list:
                print('{}번째 리스트|{}'.format(i, __))
                i += 1
        return memory_list


if __name__ == '__main__':
    main_process = body()
    main_process.start()
