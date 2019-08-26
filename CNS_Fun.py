import multiprocessing
import time
import CNS_Send_UDP
from copy import deepcopy

# ======================================================================================================================
# 진단 기능 결합 필요
# 비정상 시, 3가지 출력 값만 잘 주면 됨.

class Func_diagnosis(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]
        self.trig_mem = mem[1]
        self.trig_mem_2 = mem[-2]

    def run(self):
        while True:

            # ===========================================
            self.dumy_mem = deepcopy(self.trig_mem)
            # ===========================================

            if self.mem['KLAMPO9']['V'] == 1:
                self.dumy_mem['alarm'].append(2)
                self.dumy_mem['diagnosis'].append(0)
                self.dumy_mem['training_cond'].append(0)

            elif self.trig_mem_2['Abnormal_Dig_result']['Result'] != []:
                # print(self.trig_mem_2['Abnormal_Dig_result']['Result'][-1][0])
                if self.trig_mem_2['Abnormal_Dig_result']['Result'][-1][0] < 0.9:
                    self.dumy_mem['alarm'].append(1)
                    self.dumy_mem['diagnosis'].append(2301)
                    self.dumy_mem['training_cond'].append(1)
            else:
                self.dumy_mem['alarm'].append(0)
                self.dumy_mem['diagnosis'].append(0)
                self.dumy_mem['training_cond'].append(0)



            # if self.mem['KLAMPO9']['V'] != 1:                   ############### 대일 로직 [Result] < 0.9
            #     self.dumy_mem['alarm'].append(0)
            #     self.dumy_mem['diagnosis'].append(0)
            #     self.dumy_mem['training_cond'].append(0)
            #
            # else:
            #     self.dumy_mem['alarm'].append(1)                 # O1: 비정상 여부/
            #     self.dumy_mem['diagnosis'].append(2301)        # O2: 진단된 비정상 절차서
            #     self.dumy_mem['training_cond'].append(1)         # O3: 학습 여부

            # =================================================
            # test
            # =================================================
            # self.dumy_mem['alarm'].append(1)                    # O1: 비정상 여부
            # self.dumy_mem['diagnosis'].append('2301')           # O2: 진단된 비정상 절차서
            # self.dumy_mem['training_cond'].append(1)            # O3: 학습 여부
            # print('1')

            # =================================================         # 노이해..
            for key_val in self.trig_mem.keys():
                self.trig_mem[key_val] = self.dumy_mem[key_val]

            print(self, self.trig_mem)
            # =================================================
            time.sleep(1)

# ======================================================================================================================
# 전략 설정 기능

class Func_strategy(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]
        self.mem_2 = mem[-2]
        self.trig_mem = mem[1]
        # self.dumy_mem = deepcopy(self.trig_mem)

    def run(self):
        while True:
            self.dumy_mem = deepcopy(self.trig_mem)
            self.Identification_operation_mode()
            self.strategy_selection()


    def Identification_operation_mode(self):

        if self.trig_mem['alarm'] != []:
            if self.trig_mem['alarm'][-1] == 1:                 # 비정상 운전 상태 식별
                self.dumy_mem['operation_mode'].append(1)

            elif self.trig_mem['alarm'][-1] == 0:               # 정상 운전 상태 식별
                self.dumy_mem['operation_mode'].append(0)

            elif self.trig_mem['alarm'][-1] == 2:               # 비상 운전 상태 식별
                self.dumy_mem['operation_mode'].append(2)
            else:
                pass

            for key_val in self.trig_mem.keys():
                self.trig_mem[key_val] = self.dumy_mem[key_val]

            # print(self, self.trig_mem)

            time.sleep(1.5)

    def strategy_selection(self):                   # I1: 운전 모드, I2: 기타 정보 / O1: 세부 전략, O2: 제어 기능 활성화 신호
        if self.trig_mem['operation_mode'] != []:

            if self.trig_mem['operation_mode'][-1] == 2:                                                        # 비상 전략
                self.dumy_mem['strategy'].append('EA')                                                          # 추후 변경/ 전략: Autonomous control by what??

            if self.trig_mem['operation_mode'][-1] == 1:                                                        # 비정상 전략
                if self.trig_mem['training_cond'] != [] and self.trig_mem['diagnosis'] != []:
                    if self.trig_mem['training_cond'][-1] == 1 and self.trig_mem['diagnosis'][-1] == 2301:      # 전략: Autonomous control by LSTM for leak of RCS
                        self.dumy_mem['strategy'].append('AA_2301')
                        self.dumy_mem['control_activation'].append(10)       # 필요하려나?..

                    else:
                        pass

            elif self.trig_mem['operation_mode'][-1] == 0:                                                      # 정상 전략
                if self.mem_2['Man_state'] == True:                                                             # 전략: 수동
                    self.dumy_mem['strategy'].append('NM')

                    # for key_val in self.trig_mem.keys():
                    #     self.trig_mem[key_val] = self.dumy_mem[key_val]

                elif self.mem_2['Man_state'] == False:                                                          # 전략: Autonomous control by RL for startup
                    self.dumy_mem['strategy'].append('NA')

            for key_val in self.trig_mem.keys():
                self.trig_mem[key_val] = self.dumy_mem[key_val]

            print(self, self.trig_mem)

            time.sleep(1.5)

class function1(multiprocessing.Process):
    ## 단순한 값만 읽어 오는 예제
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]   # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

    def run(self):
        while True:
            print(self, self.mem['QPROREL'])
            time.sleep(1)


class function2(multiprocessing.Process):
    ## 제어 신호 보내는 예제
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem
        self.mem2 = mem[2]

        # UDP send part
        self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal('192.168.0.55', 7001)

    def run(self):
        while True:
            # print(self, self.mem[1]['Test'], '->', 1, self.mem2)
            self.mem[1]['Test'] = 1
            self.mem[2].append(1)
            self.UDP_sock._send_control_signal(['KSWO33', 'KSWO32'], [1, 0])
            time.sleep(1)


class function3(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem
        self.mem2 = mem[2]

    def run(self):
        while True:
            # print(self, self.mem[1]['Test'], '->', 2, self.mem2)
            self.mem[1]['Test'] = 2
            self.mem[2].append(2)
            time.sleep(3)

#========================================================================
'''
예시
- Function 4_1 돌고 있음 (출력 증,감발 기능)
- 만약 출력이 90% 이하가 되면 Function 4_2 (진단 기능)에서 진단됨.
- Function 4_3(전략 설정) 만약 진단되면 Function4_1 정지 신호 Function 4_4(조치기능) 동작 신호 전달.
'''


class function4_1(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]  # main mem connection
        self.trigger_mem = mem[1]    # {'4_1_state' : True, '4_2_state': '90%Min', '4_4_state': False}
        # {'Numb_LCO' : 4.2, 'Contents': 'LCO가 위반되었다', '시간': 2}

        # UDP send part
        self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal('192.168.0.55', 7001)
    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['D']) > 2:
            # ==========================================================================================#
                if self.trigger_mem['4_1_state']:
                    print('{} 출력 증감발 기능이 운전 중'.format(self))
                    print(self.trigger_mem)
                    self.UDP_sock._send_control_signal(['KSWO33'], [0])
                else:
                    pass
            time.sleep(1)


class function4_2(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]  # main mem connection
        self.trigger_mem = mem[1]    # {'4_1_state' : True, '4_2_state': '90%Min', '4_4_state': False}

    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['D']) > 2:
            # ==========================================================================================#
                if self.mem['QPROREL']['V'] < 0.80:
                    print('{} 출력 80% 이하 감지 진단'.format(self))
                    print(self.trigger_mem)
                    self.trigger_mem['4_2_state'] = '80%Min'

                if self.mem['QPROREL']['V'] < 0.70:
                    print('{} 출력 70% 이하 감지 진단'.format(self))
                    print(self.trigger_mem)
                    self.trigger_mem['4_2_state'] = '70%Min'

            time.sleep(1)


class function4_3(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]  # main mem connection
        self.trigger_mem = mem[1]  # {'4_1_state' : True, '4_2_state': '90%Min', '4_4_state': False}

    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['D']) > 2:
            # ==========================================================================================#
                if self.trigger_mem['4_2_state'] == '80%Min':
                    print('{} 출력 80% 이하 감지로 전략 조정'.format(self))
                    print(self.trigger_mem)
                    self.trigger_mem['4_1_state'] = False
                    self.trigger_mem['4_4_state'] = True

                if self.trigger_mem['4_2_state'] == '70%Min':
                    print('{} 출력 70% 이하 감지로 전략 조정'.format(self))
                    print(self.trigger_mem)
                    self.trigger_mem['4_1_state'] = False
                    self.trigger_mem['4_4_state'] = True

            time.sleep(1)


class function4_4(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]  # main mem connection
        self.trigger_mem = mem[1]    # {'4_1_state' : True, '4_2_state': '90%Min', '4_4_state': False}

        # UDP send part
        self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal('192.168.0.55', 7001)
    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['D']) > 2:
            # ==========================================================================================#
                if self.trigger_mem['4_4_state']:
                    print('{} 조치 기능이 운전 중'.format(self))
                    print(self.trigger_mem)
                    self.UDP_sock._send_control_signal(['KSWO32'], [0])
                else:
                    pass
            time.sleep(1)

#========================================================================


class funtion5(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]  # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

        self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal('192.168.0.24', 7001)

        self.one_time = 0

    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['D']) > 2:
            # ==========================================================================================#
            #     print(self, self.mem['Normal_0']['V'], self.mem['Normal_1']['V'])
                if len(self.mem['Normal_0']['D']) > 5:
                    self.trig_mem['Normal'] = False
                    if self.one_time == 0:
                        self.UDP_sock._send_control_signal(['KFZRUN', 'KSWO280', 'KSWO279', 'KSWO278'],
                                                           [10, 12, 100100, 5])  # 10은 멜펑션
                        self.one_time += 1
            time.sleep(1)

class t_function1(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0] # main mem connection

    def run(self):
        para = ['KMSISO']
        while True:
            print(self, self.mem['KCNTOMS']['V'])
            time.sleep(1)