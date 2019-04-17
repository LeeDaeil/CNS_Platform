import A3C_Fun as A3
from db import db_make
from multiprocessing import Manager
from CNS_UDP import *
from CNS_CFun import *

TOP_TITLE = 'Ver1'

class body:
    def __init__(self):
        # ========================================================================================#
        # self.a3c_mode : a3c모드의 여부와 에이전트의 갯수를 조정하는 곳이다.
        self.a3c_num_agent = 2
        self.a3c_mode = {'mode': True, 'Nub_agent': self.a3c_num_agent, 'Range': range(0, self.a3c_num_agent)}
        # Clean mem 기능 및 기타 기능에서 print로 출력되는 정보를 출력하지 않도록 하는 기능
        self.shut_up = [True for _ in self.a3c_mode['Range']]
        #========================================================================================#
        # 공유 메모리
        self.gen_mem = generate_mem()
        self.shared_mem = [self.gen_mem.make_mem_structure() for _ in self.a3c_mode['Range']]
        #========================================================================================#
        # 병렬적인 UDP 네트워크 소켓 생성하는 부분
        # - 포트는 7001번 부터 에이전트 수가 증가하면 +1씩 증가
        # - 1개의 에이전트 및 모듈을 사용하면 단일 소켓만 개방됨
        self.UDP_net = [UDPSocket(self.shared_mem[_], IP='', Port=7001+_,
                                  shut_up=self.shut_up[_]) for _ in self.a3c_mode['Range']]
        # ========================================================================================#
        if self.a3c_mode['mode']:
            clean_mem_list = [clean_mem(self.shared_mem[_], shut_up=self.shut_up[_]) for _ in self.a3c_mode['Range']]
            self.process_list = clean_mem_list + [A3.A3C_Process_Module(self.shared_mem, 'LSTM', TOP_TITLE)]
        else:
            self.process_list = [
                clean_mem(self.shared_mem, shut_up=self.shut_up),
            ]
        # ========================================================================================#

    def start(self):
        print('A3C mode : {}'.format(self.a3c_mode['mode']))
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
    '''
    공유 메모리를 선언하는 클레스
    - 클래스 내의 함수를 작성하여 개별적인 메모리 선언가능
    '''
    def __init__(self):
        self.db_maker_ = db_make()

    def make_test_mem(self):
        memory_dict = {'Test': 0, 'List_Test': []}
        return memory_dict

    def make_test_list_mem(self):
        memory_list = []
        return memory_list

    def make_CNS_time_mem(self):
        memory_list = []
        return memory_list

    def make_clean_mem(self):
        memory_dict = {'Clean': True}
        return memory_dict

    def make_main_mem_structure(self, max_len_deque=10, show_main_mem=False):
        memory_dict = self.db_maker_.make_db_structure(max_len_deque)
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
                       # Manager().list(self.make_CNS_time_mem()),                        # [-2]
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
        print('Mem_List 생성 완료')
        return memory_list


if __name__ == '__main__':
    main_process = body()
    main_process.start()