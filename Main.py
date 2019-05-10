from db import db_make
from multiprocessing import Manager
from CNS_UDP import *
from CNS_Fun import *
from CNS_GFun import *
from CNS_CFun import *
from CNS_TSMS import *

class body:
    def __init__(self):
        #==== Initial part for testing===========================================================#
        self.test_mode = 'TSMS' # 'Normal', 'TSMS', 'Test_clean'
        self.shut_up = True
        #========================================================================================#
        self.shared_mem = generate_mem().make_mem_structure()
        self.UDP_net = [UDPSocket(self.shared_mem, IP='', Port=7001, shut_up=self.shut_up)]

        if self.test_mode == 'Normal':
            self.process_list = [
                clean_mem(self.shared_mem, shut_up=self.shut_up),
                # function1(self.shared_mem),
                # function2(self.shared_mem),
                # function3(self.shared_mem),
                # gfunction(self.shared_mem),
                # gfunction2(self.shared_mem),
                # function4_1(self.shared_mem),
                # function4_2(self.shared_mem),
                # function4_3(self.shared_mem),
                # function4_4(self.shared_mem),
                funtion5(self.shared_mem),
            ]
        elif self.test_mode == 'TSMS':
            self.process_list = [
                clean_mem(self.shared_mem, shut_up=self.shut_up),
                TSMS(self.shared_mem),
            ]
        else:
            self.process_list = [
                clean_mem(self.shared_mem, shut_up=self.shut_up),
            ]

    def start(self):
        print('CNS Platfrom mode : {}'.format(self.test_mode))
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
    def make_test_mem(self):
        memory_dict = {'4_1_state': True, '4_2_state': '', '4_4_state': False}
        return memory_dict

    def make_test_list_mem(self):
        memory_list = []
        return memory_list

    def make_CNS_time_mem(self):
        memory_list = []
        return memory_list

    def make_TSMS_mem(self):
        memory_dict = {'Monitoring_result': 0,
                       'Raw_violation': '', 'Raw_text_result': '', 'Raw_result': 0, 'Raw_action': '',
                       'Shut_BOL': 0, 'Shut_EOL': 0, 'Shut_Burn_up': 0, 'Shut_Fin': 0, 'Shut_Inoper_rod': 0,
                       'Shut_Abnormal_rod_worth': 0, 'Shut_Inoper_ableAbnormal_RodWorth': 0, 'Shut_ShutdownMargin': 0,
                       'Shut_Result': '', 'Shut_ab_comment': '', 'PT_Result': 0}
        return memory_dict

    def make_clean_mem(self):
        memory_dict = {'Clean': True, 'Normal': True, 'Accident_nb': 0}
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
        return memory_dict

    def make_mem_structure(self, show_mem_list=False):
        memory_list = [Manager().dict(self.make_main_mem_structure(max_len_deque=10)),  # [0]
                       # Manager().dict(self.make_test_mem()),
                       # Manager().list(self.make_test_list_mem()),
                       Manager().dict(self.make_TSMS_mem()),                            # [-3]
                       Manager().list(self.make_CNS_time_mem()),                        # [-2]
                       Manager().dict(self.make_clean_mem()),                           # [-1]
                       ]
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