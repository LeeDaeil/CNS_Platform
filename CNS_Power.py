import multiprocessing
import time
import numpy as np
import CNS_Send_UDP
import copy
import CNS_Network


class Power_increase_module(multiprocessing.Process):
    def __init__(self, mem, shut, cns_ip, cns_port):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]           # main mem connection

        self.auto_mem = mem[-2]     # 자율 운전 메모리
        self.dumy_auto_mem = copy.deepcopy(self.auto_mem)

        self.trig_mem = mem[1]      # 전략 설정 기능으로 부터의 로직
        self.shut = shut

        self.UDP_sock = CNS_Send_UDP.CNS_Send_Signal(cns_ip, cns_port)
        self.time_legnth = 10

        self.save_para = False
        self.save_tick = 0

    def p_shut(self, txt):
        if not self.shut:
            print(self, txt)

    # ================================================================================================================#
    def run(self):

        self.Rod_net = CNS_Network.MainNet(net_type='LSTM', input_pa=6, output_pa=3, time_leg=10)
        self.Rod_net.load_model()
        self.p_shut('네트워크 모델 로드')

        self.timmer = 0

        if not self.shut:
            self.Rod_net.actor.summary()
            self.Rod_net.critic.summary()

        while True:
            #==========================================================================================#
            if self.mem['KCNTOMS']['V'] == 0:
                self.p_shut('초기 조건 상태가 감지 - 모듈 대기')
                if len(self.mem['KCNTOMS']['D']) == 0:
                    self.mem_len = 0
                else:
                    self.mem_len = self.mem['KCNTOMS']['D'][-1]
            # ==========================================================================================#
            else:
                if self.mem_len == self.mem['KCNTOMS']['D'][-1]:
                    self.p_shut('CNS가 정지된 상태 - 모듈 대기')
                else:
                    self.p_shut('CNS가 동작 상태 - 모듈 동작')
                    self.mem_len = self.mem['KCNTOMS']['D'][-1]
                    if self.trig_mem['strategy'][-1] == 'NA':
                        input_data = self.make_input_data(time_legnth=self.time_legnth)
                        self.sub_run_1(input_data=input_data, time_legnth=self.time_legnth)
                    elif self.trig_mem['strategy'][-1] == 'AA_2301':
                        self.UDP_sock._send_control_signal(['KSWO33', 'KSWO32'], [0, 0])

            time.sleep(0.5)

    def make_input_data(self, time_legnth):
        temp = []
        self.dumy_auto_mem = copy.deepcopy(self.auto_mem)

        for _ in reversed(range(-1, -(time_legnth*2), -2)):
            try:
                tick = self.mem['KCNTOMS']['D'][_]
                Mwe_power = self.mem['KBCDO22']['D'][_]
                load_set = self.mem['KBCDO20']['D'][_]
                power = self.mem['QPROREL']['D'][_]

                if power >= 0.97 and self.save_tick == 0:
                    self.save_para = True
                    self.save_tick = tick

                if self.save_para:
                    tick = self.save_tick

                base_condition = tick / 30000
                up_base_condition = (tick * 53) / 1470000
                low_base_condition = (tick * 3) / 98000

                stady_condition = base_condition + 0.02

                distance_up = up_base_condition + 0.04 - power
                distance_low = power - low_base_condition

                temp.append([power, distance_up, distance_low, stady_condition, Mwe_power/1000, load_set/100])
            except:
                pass
        # ------------------------------------------
        # 제어봉 Display로 정보를 전달하기 위해서 Autonomous mem 에 정보를 전달
        self.dumy_auto_mem['Start_up_operation_his']['power'].append(power)
        self.dumy_auto_mem['Start_up_operation_his']['up_cond'].append(up_base_condition + 0.04)
        self.dumy_auto_mem['Start_up_operation_his']['low_cond'].append(low_base_condition)
        self.dumy_auto_mem['Start_up_operation_his']['time'].append(self.mem['KCNTOMS']['D'][-1]/5)

        for key_val in self.auto_mem.keys():
            self.auto_mem[key_val] = self.dumy_auto_mem[key_val]
        # ------------------------------------------
        return temp

    # ================================================================================================================#
    # 2 Section - 네트워크 입출력 계산
    # ================================================================================================================#
    def send_action_append(self, pa, va):
        for _ in range(len(pa)):
            self.para.append(pa[_])
            self.val.append(va[_])

    def sub_run_1(self, input_data, time_legnth):
        if len(input_data) == time_legnth:
            act, proba = self.Rod_net.predict_action(input_data)
            # print(act, proba)
            self.p_shut('데이터 길이 완료 - 네트워크 계산 시작 - {}'.format(act))
            self.send_action(act)
        else:
            self.p_shut('데이터 길이 부족함 - 네트워크 계산 대기')

    def send_action(self, R_A):

        # 전송될 변수와 값 저장하는 리스트
        self.para = []
        self.val = []

        self.Time_tick = self.mem['KCNTOMS']['V']
        self.Reactor_power = self.mem['QPROREL']['V']
        self.TRIP_SIG = self.mem['KLAMPO9']['V']
        self.charging_valve_state = self.mem['KLAMPO95']['V']           #
        self.main_feed_valve_1_state = self.mem['KLAMPO147']['V']       #
        self.main_feed_valve_2_state = self.mem['KLAMPO148']['V']       #
        self.main_feed_valve_3_state = self.mem['KLAMPO149']['V']       #

        self.Turbine_setpoint = self.mem['KBCDO17']['V']
        self.Turbine_ac = self.mem['KBCDO18']['V']  # Turbine ac condition
        self.Turbine_real = self.mem['KBCDO19']['V']
        self.load_set = self.mem['KBCDO20']['V']  # Turbine load set point
        self.load_rate = self.mem['KBCDO21']['V']  # Turbine load rate
        self.Mwe_power = self.mem['KBCDO22']['V']

        self.Netbreak_condition = self.mem['KLAMPO224']['V'] # 0 : Off, 1 : On
        self.trip_block = self.mem['KLAMPO22']['V']  # Trip block condition 0 : Off, 1 : On

        self.steam_dump_condition = self.mem['KLAMPO150']['V'] # 0: auto 1: man
        self.heat_drain_pump_condition = self.mem['KLAMPO244']['V'] # 0: off, 1: on
        self.main_feed_pump_1 = self.mem['KLAMPO241']['V'] # 0: off, 1: on
        self.main_feed_pump_2 = self.mem['KLAMPO242']['V'] # 0: off, 1: on
        self.main_feed_pump_3 = self.mem['KLAMPO243']['V'] # 0: off, 1: on
        self.cond_pump_1 = self.mem['KLAMPO181']['V'] # 0: off, 1: on
        self.cond_pump_2 = self.mem['KLAMPO182']['V'] # 0: off, 1: on
        self.cond_pump_3 = self.mem['KLAMPO183']['V'] # 0: off, 1: on

        # 주급수 및 CVCS 자동
        # if self.charging_valve_state == 1:
        #     self.send_action_append(['KSWO100'], [0])
        if self.main_feed_valve_1_state == 1 or self.main_feed_valve_2_state == 1 or self.main_feed_valve_3_state == 1:
            self.send_action_append(['KSWO171', 'KSWO165', 'KSWO159'], [0, 0, 0])
        self.send_action_append(['KSWO78'], [1]) # Make-up 물 넣는 기능

        # 절차서 구성 순서로 진행
        # 1) 출력이 4% 이상에서 터빈 set point를 맞춘다.
        if self.Reactor_power >= 0.04 and self.Turbine_setpoint != 1800:
            if self.Turbine_setpoint < 1750: # 1780 -> 1872
                self.send_action_append(['KSWO213'], [1])
            elif self.Turbine_setpoint >= 1750:
                self.send_action_append(['KSWO213'], [0])
        # 1) 출력 4% 이상에서 터빈 acc 를 200 이하로 맞춘다.
        if self.Reactor_power >= 0.04 and self.Turbine_ac != 210:
            if self.Turbine_ac < 200:
                self.send_action_append(['KSWO215'], [1])
            elif self.Turbine_ac >= 200:
                self.send_action_append(['KSWO215'], [0])
        # 2) 출력 10% 이상에서는 Trip block 우회한다.
        if self.Reactor_power >= 0.10 and self.trip_block != 1:
            self.send_action_append(['KSWO22', 'KSWO21'], [1, 1])
        # 2) 출력 10% 이상에서는 rate를 50까지 맞춘다.
        if self.Reactor_power >= 0.10 and self.Mwe_power <= 0:
            if self.load_set < 100: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
            if self.load_rate < 50: self.send_action_append(['KSWO227', 'KSWO226'], [1, 0])
            else: self.send_action_append(['KSWO227', 'KSWO226'], [0, 0])

        # if 0.10 <= self.Reactor_power < 0.20:
        if 0.15 <= self.Reactor_power < 0.20:
            if self.load_set < 100: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        # if 0.200 <= self.Reactor_power < 0.300:
        if 0.20 <= self.Reactor_power < 0.30:
            if self.load_set < 150: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        if 0.30 <= self.Reactor_power < 0.40:
            if self.load_set < 200: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        if 0.40 <= self.Reactor_power < 0.50:
            if self.load_set < 300: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        if 0.50 <= self.Reactor_power < 0.60:
            if self.load_set < 400: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        if 0.60 <= self.Reactor_power < 0.70:
            if self.load_set < 500: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        if 0.70 <= self.Reactor_power < 0.80:
            if self.load_set < 600: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        if 0.80 <= self.Reactor_power < 0.90:
            if self.load_set < 700: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
        if 0.90 <= self.Reactor_power < 100:
            if self.load_set < 850: self.send_action_append(['KSWO225', 'KSWO224'], [1, 0]) # 터빈 load를 150 Mwe 까지,
            else: self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])

        # 3) 출력 15% 이상 및 터빈 rpm이 1800이 되면 netbreak 한다.
        if self.Reactor_power >= 0.15 and self.Turbine_real >= 1790 and self.Netbreak_condition != 1:
            self.send_action_append(['KSWO244'], [1])
        # 4) 출력 15% 이상 및 전기 출력이 존재하는 경우, steam dump auto로 전향
        if self.Reactor_power >= 0.15 and self.Mwe_power > 0 and self.steam_dump_condition == 1:
            self.send_action_append(['KSWO176'], [0])
        # 4) 출력 15% 이상 및 전기 출력이 존재하는 경우, heat drain pump on
        if self.Reactor_power >= 0.15 and self.Mwe_power > 0 and self.heat_drain_pump_condition == 0:
            self.send_action_append(['KSWO205'], [1])
        # 5) 출력 20% 이상 및 전기 출력이 190Mwe 이상 인경우
        if self.Reactor_power >= 0.20 and self.Mwe_power >= 190 and self.cond_pump_2 == 0:
            self.send_action_append(['KSWO205'],[1])
        # 6) 출력 40% 이상 및 전기 출력이 380Mwe 이상 인경우
        if self.Reactor_power >= 0.40 and self.Mwe_power >= 380 and self.main_feed_pump_2 == 0:
            self.send_action_append(['KSWO193'], [1])
        # 7) 출력 50% 이상 및 전기 출력이 475Mwe
        if self.Reactor_power >= 0.50 and self.Mwe_power >= 475 and self.cond_pump_3 == 0:
            self.send_action_append(['KSWO206'], [1])
        # 8) 출력 80% 이상 및 전기 출력이 765Mwe
        if self.Reactor_power >= 0.80 and self.Mwe_power >= 765 and self.main_feed_pump_3 == 0:
            self.send_action_append(['KSWO192'], [1])

        # 9) 제어봉 조작 신호를 보내기
        if self.save_para:      # 파라가 save 즉 0.97 보다 파워가 큼
            self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # Stay
        else:
            '''
            제어봉을 어느정도 조작하고 싶은지 설정하는 부분 여기서는 20 tick(4초) 마다 1번 제어하도록 설정
            '''
            if self.timmer != divmod(self.Time_tick, 20)[0]:
                print('ACT')
                self.timmer = divmod(self.Time_tick, 20)[0]
                if R_A == 0: self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # Stay
                elif R_A == 1: self.send_action_append(['KSWO33', 'KSWO32'], [1, 0])  # Out
                elif R_A == 2: self.send_action_append(['KSWO33', 'KSWO32'], [0, 1])  # In

        self.UDP_sock._send_control_signal(self.para, self.val)

