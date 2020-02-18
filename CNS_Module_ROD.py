import numpy as np
from CNS_Send_UDP import CNS_Send_Signal
import CNS_Platform_PARA as PARA
from collections import deque


class rod_controller_module:
    def __init__(self, network):

        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')  # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

        self.network = network
        self.tick = deque(maxlen=10)
        self.change_st = deque(maxlen=2)
        self.stop_val = 0
        self.gap = 0

    def predict_action(self, mem, tirg_mem):
        # 이전 전략과 비교하여 바뀌는 경우 gap을 재계산 해야함.
        self.change_st.append(tirg_mem['Auto'])
        if len(self.change_st) < 2:
            # 초기 상태의 경우 전략 HIS를 2개 만들어야함.
            self.change_st.append(tirg_mem['Auto'])

        if tirg_mem['OPStrategy'] == PARA.Normal and tirg_mem['Auto'] == True:
            # 현재 Nomal 이고 Auto mode 임.
            if self.change_st[0] != self.change_st[1]:
                # self.gap = mem['KCNTOMS']['V'] * tirg_mem['Speed'] - self.stop_val
                self.gap = mem['KCNTOMS']['V'] - self.stop_val
            # self.tick.append(mem['KCNTOMS']['V'] * tirg_mem['Speed'] - self.gap)
            self.tick.append(mem['KCNTOMS']['V'] - self.gap)
        elif tirg_mem['OPStrategy'] == PARA.Normal and tirg_mem['Auto'] == False:
            # Auto로 동작하기 이전까지 Tick은 0 또는 이전의 Tick을 가져와야함.
            if len(self.tick) == 0:
                self.tick.append(0)
            else:
                self.stop_val = self.tick[-1]
                self.tick.append(self.tick[-1])
        else:
            pass

        input_data = self.make_input_data(mem=mem)
        if len(mem['KCNTOMS']['D']) >= 10:  # Rod가 동작하지 않는 경우에도 데이터를 계산하기 위해서 사용
            predict_result = self.network.predict([[input_data]])
            policy = predict_result[0]
            action = np.random.choice(np.shape(policy)[0], 1, p=policy)[0]
            # 계산된 액션은 CNS로 보내짐.
            self.send_action(mem=mem, trig_mem=tirg_mem, R_A=action)

        return input_data[-1]  # action, proba, 마지막 네트워크 값

    def make_input_data(self, mem):
        temp = []
        for _ in range(0, len(mem['KCNTOMS']['D'])):  # Rod가 동작하지 않는 경우에도 데이터를 계산하기 위해서 사용
            try:
                # 사용되는 파라메터 전체 업데이트
                tick = self.tick[_]
                self.Reactor_power = mem['QPROREL']['D'][_]
                self.TRIP = mem['KRXTRIP']['D'][_]
                # 온도 고려 2019-11-04
                self.Tref_Tavg = mem['ZINST15']['D'][_]  # Tref-Tavg
                self.Tavg = mem['UAVLEGM']['D'][_]  # 308.21
                self.Tref = mem['UAVLEGS']['D'][_]  # 308.22
                # 제어봉 Pos
                self.rod_pos = [mem[nub_rod]['D'][_] for nub_rod in ['KBCDO10', 'KBCDO9', 'KBCDO8', 'KBCDO7']]
                #
                self.charging_valve_state = mem['KLAMPO95']['D'][_]
                self.main_feed_valve_1_state = mem['KLAMPO147']['D'][_]
                self.main_feed_valve_2_state = mem['KLAMPO148']['D'][_]
                self.main_feed_valve_3_state = mem['KLAMPO149']['D'][_]
                self.vct_level = mem['ZVCT']['D'][_]
                self.pzr_level = mem['ZINST63']['D'][_]
                #
                self.Turbine_setpoint = mem['KBCDO17']['D'][_]
                self.Turbine_ac = mem['KBCDO18']['D'][_]  # Turbine ac condition
                self.Turbine_real = mem['KBCDO19']['D'][_]
                self.load_set = mem['KBCDO20']['D'][_]  # Turbine load set point
                self.load_rate = mem['KBCDO21']['D'][_]  # Turbine load rate
                self.Mwe_power = mem['KBCDO22']['D'][_]
                #
                self.Netbreak_condition = mem['KLAMPO224']['D'][_]  # 0 : Off, 1 : On
                self.trip_block = mem['KLAMPO22']['D'][_]  # Trip block condition 0 : Off, 1 : On
                #
                self.steam_dump_condition = mem['KLAMPO150']['D'][_]  # 0: auto 1: man
                self.heat_drain_pump_condition = mem['KLAMPO244']['D'][_]  # 0: off, 1: on
                self.main_feed_pump_1 = mem['KLAMPO241']['D'][_]  # 0: off, 1: on
                self.main_feed_pump_2 = mem['KLAMPO242']['D'][_]  # 0: off, 1: on
                self.main_feed_pump_3 = mem['KLAMPO243']['D'][_]  # 0: off, 1: on
                self.cond_pump_1 = mem['KLAMPO181']['D'][_]  # 0: off, 1: on
                self.cond_pump_2 = mem['KLAMPO182']['D'][_]  # 0: off, 1: on
                self.cond_pump_3 = mem['KLAMPO183']['D'][_]  # 0: off, 1: on

                self.ax_off = mem['CAXOFF']['D'][_]

                if True:
                    # 평균온도에 기반한 출력 증가 알고리즘
                    # (290.2~308.2: 18도 증가) -> ( 2%~100%: 98% 증가 )
                    # 18 -> 98 따라서 1%증가시 요구되는 온도 증가량 18/98
                    # 1분당 1% 증가시 0.00306 도씩 초당 증가해야함.
                    # 2% start_ref_temp = 290.2 매틱 마다 0.00306 씩 증가
                    # increase_slop = 0.0001(5배에서 시간당 1%임).
                    #               = 0.001 (5배에서 시간당 10%?, 분당 약 0.46~0.5%, 0.085도/분) - Ver10
                    #               = 0.001489 (5배에서 시간당 10%?, 분당 약 0.46~0.5%, ?도/분) - Ver11
                    #               = 0.001489 (5배에서 시간당 10%?, 분당 약 0.46~0.5%, ?도/분) - Ver11
                    increase_slop = 0.001
                    start_2per_temp = 291.97

                    self.get_current_t_ref = start_2per_temp + (increase_slop) * tick

                    self.up_dead_band = self.get_current_t_ref + 1
                    self.down_dead_band = self.get_current_t_ref - 1
                    self.up_operation_band = self.get_current_t_ref + 3
                    self.down_operation_band = self.get_current_t_ref - 3

                temp.append([
                    # 네트워크의 Input 에 들어 가는 변수 들
                    self.Reactor_power, self.up_dead_band / 1000, self.down_dead_band / 1000,
                                        self.get_current_t_ref / 1000, self.Mwe_power / 1000,
                                        self.up_operation_band / 1000, self.down_operation_band / 1000,
                                        self.load_set / 100, self.Tavg / 1000,
                                        self.rod_pos[0] / 1000, self.rod_pos[1] / 1000, self.rod_pos[2] / 1000,
                                        self.rod_pos[3] / 1000,
                ])
            except Exception as e:
                print(self, e)
        return temp

    # ================================================================================================================#
    # 2 Section - 네트워크 입출력 계산
    # ================================================================================================================#
    def send_action_append(self, pa, va):
        for _ in range(len(pa)):
            self.para.append(pa[_])
            self.val.append(va[_])

    def send_action(self, mem, trig_mem, R_A):

        # 전송될 변수와 값 저장하는 리스트
        self.para = []
        self.val = []

        self.Time_tick = mem['KCNTOMS']['V']
        self.Reactor_power = mem['QPROREL']['V']
        self.TRIP_SIG = mem['KLAMPO9']['V']
        self.charging_valve_state = mem['KLAMPO95']['V']  #
        self.main_feed_valve_1_state = mem['KLAMPO147']['V']  #
        self.main_feed_valve_2_state = mem['KLAMPO148']['V']  #
        self.main_feed_valve_3_state = mem['KLAMPO149']['V']  #

        self.Turbine_setpoint = mem['KBCDO17']['V']
        self.Turbine_ac = mem['KBCDO18']['V']  # Turbine ac condition
        self.Turbine_real = mem['KBCDO19']['V']
        self.load_set = mem['KBCDO20']['V']  # Turbine load set point
        self.load_rate = mem['KBCDO21']['V']  # Turbine load rate
        self.Mwe_power = mem['KBCDO22']['V']

        self.Netbreak_condition = mem['KLAMPO224']['V']  # 0 : Off, 1 : On
        self.trip_block = mem['KLAMPO22']['V']  # Trip block condition 0 : Off, 1 : On

        self.steam_dump_condition = mem['KLAMPO150']['V']  # 0: auto 1: man
        self.heat_drain_pump_condition = mem['KLAMPO244']['V']  # 0: off, 1: on
        self.main_feed_pump_1 = mem['KLAMPO241']['V']  # 0: off, 1: on
        self.main_feed_pump_2 = mem['KLAMPO242']['V']  # 0: off, 1: on
        self.main_feed_pump_3 = mem['KLAMPO243']['V']  # 0: off, 1: on
        self.cond_pump_1 = mem['KLAMPO181']['V']  # 0: off, 1: on
        self.cond_pump_2 = mem['KLAMPO182']['V']  # 0: off, 1: on
        self.cond_pump_3 = mem['KLAMPO183']['V']  # 0: off, 1: on

        # Chargning Valve _ mal
        self.send_action_append(['KSWO100'], [1])

        # 주급수 및 CVCS 자동
        if self.charging_valve_state == 1:
            self.send_action_append(['KSWO100'], [0])
        if self.main_feed_valve_1_state == 1 or self.main_feed_valve_2_state == 1 or self.main_feed_valve_3_state == 1:
            self.send_action_append(['KSWO171', 'KSWO165', 'KSWO159'], [0, 0, 0])
        self.send_action_append(['KSWO78', 'WDEWT'], [1, 1])  # Makeup

        # 절차서 구성 순서로 진행
        # 1) 출력이 4% 이상에서 터빈 set point를 맞춘다.
        if self.Reactor_power >= 0.04 and self.Turbine_setpoint != 1800:
            if self.Turbine_setpoint < 1790:  # 1780 -> 1872
                self.send_action_append(['KSWO213'], [1])
            elif self.Turbine_setpoint >= 1790:
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
            if self.load_set < 100:
                self.send_action_append(['KSWO225', 'KSWO224'], [1, 0])  # 터빈 load를 150 Mwe 까지,
            else:
                self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])
            if self.load_rate < 5:
                self.send_action_append(['KSWO227', 'KSWO226'], [1, 0])
            else:
                self.send_action_append(['KSWO227', 'KSWO226'], [0, 0])

        def range_fun(st, end, goal):
            if st <= self.Reactor_power < end:
                if self.load_set < goal:
                    self.send_action_append(['KSWO225', 'KSWO224'], [1, 0])  # 터빈 load를 150 Mwe 까지,
                else:
                    self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])

        if True:
            range_fun(st=0.10, end=0.20, goal=100)
            range_fun(st=0.20, end=0.25, goal=150)
            range_fun(st=0.25, end=0.30, goal=200)
            range_fun(st=0.30, end=0.35, goal=250)
            range_fun(st=0.35, end=0.40, goal=300)
            range_fun(st=0.40, end=0.45, goal=350)
            range_fun(st=0.45, end=0.50, goal=400)
            range_fun(st=0.50, end=0.55, goal=450)
            range_fun(st=0.55, end=0.60, goal=500)
            range_fun(st=0.60, end=0.65, goal=550)
            range_fun(st=0.65, end=0.70, goal=600)
            range_fun(st=0.70, end=0.75, goal=650)
            range_fun(st=0.75, end=0.80, goal=700)
            range_fun(st=0.80, end=0.85, goal=750)
            range_fun(st=0.85, end=0.90, goal=800)
            range_fun(st=0.90, end=0.95, goal=850)
            range_fun(st=0.95, end=1.00, goal=900)
            range_fun(st=1.00, end=1.50, goal=930)

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
            self.send_action_append(['KSWO205'], [1])
        # 6) 출력 40% 이상 및 전기 출력이 380Mwe 이상 인경우
        if self.Reactor_power >= 0.40 and self.Mwe_power >= 380 and self.main_feed_pump_2 == 0:
            self.send_action_append(['KSWO193'], [1])
        # 7) 출력 50% 이상 및 전기 출력이 475Mwe
        if self.Reactor_power >= 0.50 and self.Mwe_power >= 475 and self.cond_pump_3 == 0:
            self.send_action_append(['KSWO206'], [1])
        # 8) 출력 80% 이상 및 전기 출력이 765Mwe
        if self.Reactor_power >= 0.80 and self.Mwe_power >= 765 and self.main_feed_pump_3 == 0:
            self.send_action_append(['KSWO192'], [1])

        if trig_mem['OPStrategy'] == PARA.Normal and trig_mem['Auto'] == True:
            # # 9) 제어봉 조작 신호를 보내기
            if self.Reactor_power >= 0.97:  # 파라가 save 즉 0.97 보다 파워가 큼
                self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # Stay
            else:
                if R_A == 0:
                    self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # Stay
                elif R_A == 1:
                    self.send_action_append(['KSWO33', 'KSWO32'], [1, 0])  # Out
                elif R_A == 2:
                    self.send_action_append(['KSWO33', 'KSWO32'], [0, 1])  # In

        self.CNS_udp._send_control_signal(self.para, self.val)

class rod_controller_module_Back:
    def __init__(self, network):

        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')   # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

        self.network = network
        self.tick = deque(maxlen=10)
        self.change_st = deque(maxlen=2)
        self.stop_val = 0
        self.gap = 0

    def predict_action(self, mem, tirg_mem):
        # 이전 전략과 비교하여 바뀌는 경우 gap을 재계산 해야함.
        self.change_st.append(tirg_mem['Auto'])
        if len(self.change_st) < 2:
            # 초기 상태의 경우 전략 HIS를 2개 만들어야함.
            self.change_st.append(tirg_mem['Auto'])

        if tirg_mem['OPStrategy'] == PARA.Normal and tirg_mem['Auto'] == True:
            # 현재 Nomal 이고 Auto mode 임.
            if self.change_st[0] != self.change_st[1]:
                self.gap = mem['KCNTOMS']['V'] * tirg_mem['Speed'] - self.stop_val
            self.tick.append(mem['KCNTOMS']['V'] * tirg_mem['Speed'] - self.gap)
        elif tirg_mem['OPStrategy'] == PARA.Normal and tirg_mem['Auto'] == False:
            # Auto로 동작하기 이전까지 Tick은 0 또는 이전의 Tick을 가져와야함.
            if len(self.tick) == 0:
                self.tick.append(0)
            else:
                self.stop_val = self.tick[-1]
                self.tick.append(self.tick[-1])
        else:
            pass

        input_data = self.make_input_data(mem=mem)
        if len(mem['KCNTOMS']['D']) >= 10: # Rod가 동작하지 않는 경우에도 데이터를 계산하기 위해서 사용
            predict_result = self.network.predict([[input_data]])
            policy = predict_result[0]
            action = np.random.choice(np.shape(policy)[0], 1, p=policy)[0]
            # 계산된 액션은 CNS로 보내짐.
            self.send_action(mem=mem, trig_mem = tirg_mem, R_A=action)

        return input_data[-1] # action, proba, 마지막 네트워크 값
    
    def make_input_data(self, mem):
        temp = []
        for _ in range(0, len(mem['KCNTOMS']['D'])):  # Rod가 동작하지 않는 경우에도 데이터를 계산하기 위해서 사용
            try:
                # Tick 은 변경 될 수도 있으므로 내부적으로 저장 및 이에 기반하여 계산함.
                tick = self.tick[_]
                Mwe_power = mem['KBCDO22']['D'][_]
                load_set = mem['KBCDO20']['D'][_]
                power = mem['QPROREL']['D'][_]
                base_condition = tick / 30000
                up_base_condition = (tick * 53) / 1470000
                low_base_condition = (tick * 3) / 98000

                stady_condition = base_condition + 0.02

                distance_up = up_base_condition + 0.04 - power
                distance_low = power - low_base_condition
                temp.append([power, distance_up, distance_low, stady_condition, Mwe_power/1000, load_set/100])
            except Exception as e:
                print(self, e)
        return temp
    
    # ================================================================================================================#
    # 2 Section - 네트워크 입출력 계산
    # ================================================================================================================#
    def send_action_append(self, pa, va):
        for _ in range(len(pa)):
            self.para.append(pa[_])
            self.val.append(va[_])
            
    def send_action(self, mem, trig_mem, R_A):

        # 전송될 변수와 값 저장하는 리스트
        self.para = []
        self.val = []

        self.Time_tick = mem['KCNTOMS']['V']
        self.Reactor_power = mem['QPROREL']['V']
        self.TRIP_SIG = mem['KLAMPO9']['V']
        self.charging_valve_state = mem['KLAMPO95']['V']           #
        self.main_feed_valve_1_state = mem['KLAMPO147']['V']       #
        self.main_feed_valve_2_state = mem['KLAMPO148']['V']       #
        self.main_feed_valve_3_state = mem['KLAMPO149']['V']       #

        self.Turbine_setpoint = mem['KBCDO17']['V']
        self.Turbine_ac = mem['KBCDO18']['V']  # Turbine ac condition
        self.Turbine_real = mem['KBCDO19']['V']
        self.load_set = mem['KBCDO20']['V']  # Turbine load set point
        self.load_rate = mem['KBCDO21']['V']  # Turbine load rate
        self.Mwe_power = mem['KBCDO22']['V']

        self.Netbreak_condition = mem['KLAMPO224']['V'] # 0 : Off, 1 : On
        self.trip_block = mem['KLAMPO22']['V']  # Trip block condition 0 : Off, 1 : On

        self.steam_dump_condition = mem['KLAMPO150']['V'] # 0: auto 1: man
        self.heat_drain_pump_condition = mem['KLAMPO244']['V'] # 0: off, 1: on
        self.main_feed_pump_1 = mem['KLAMPO241']['V'] # 0: off, 1: on
        self.main_feed_pump_2 = mem['KLAMPO242']['V'] # 0: off, 1: on
        self.main_feed_pump_3 = mem['KLAMPO243']['V'] # 0: off, 1: on
        self.cond_pump_1 = mem['KLAMPO181']['V'] # 0: off, 1: on
        self.cond_pump_2 = mem['KLAMPO182']['V'] # 0: off, 1: on
        self.cond_pump_3 = mem['KLAMPO183']['V'] # 0: off, 1: on

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

        if trig_mem['OPStrategy'] == PARA.Normal and trig_mem['Auto'] == True:
            # # 9) 제어봉 조작 신호를 보내기
            if self.Reactor_power >= 0.97 :      # 파라가 save 즉 0.97 보다 파워가 큼
                self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # Stay
            else:
                '''
                제어봉을 어느정도 조작하고 싶은지 설정하는 부분 여기서는 20 tick(4초) 마다 1번 제어하도록 설정
                '''
                if R_A == 0: self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # Stay
                elif R_A == 1: self.send_action_append(['KSWO33', 'KSWO32'], [1, 0])  # Out
                elif R_A == 2: self.send_action_append(['KSWO33', 'KSWO32'], [0, 1])  # In
        self.CNS_udp._send_control_signal(self.para, self.val)
