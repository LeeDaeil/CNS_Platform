import numpy as np
from collections import deque
from CNS_Send_UDP import CNS_Send_Signal
import CNS_Platform_PARA as PARA
import time


class controller_module:
    def __init__(self):
        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')  # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

        # NEW_VER_2 Initial COND
        self.COND_INIT = True
        self.COND_INIT_END_TIME = 0
        self.COND_ALL_ROD_OUT = False
        self.COND_NET_BRK = False
        self.COND_NET_BRK_DIS = 0
        self.COND_AFTER = False
        self.COND_AFTER_TIME = 0

        self.i = 0
    # ================================================================================================================#
    # 2 Section - 네트워크 입출력 계산
    # ================================================================================================================#
    def send_action_append(self, pa, va):
        for _ in range(len(pa)):
            self.para.append(pa[_])
            self.val.append(va[_])

    def send_action(self, mem, trig_mem, R_A):
        if 0 <= self.i <= 1064:
            trig_mem['CNS_SPEED'] = 300
            action = PARA.HIS_ALL_OUT_CONT['Act'][self.i]

        elif 1064 < self.i <= 2000:
            time.sleep(1000000000)
            pass

        print('--' + str(action), end='--')
        self.i += 1

        self.make_input(mem=mem)

        # 전송될 변수와 값 저장하는 리스트
        self.para = []
        self.val = []

        # 주급수 및 CVCS 자동
        if self.charging_valve_state == 1:
            self.send_action_append(['KSWO100'], [0])

        if self.Reactor_power >= 0.20:
            if self.main_feed_valve_1_state == 1 or self.main_feed_valve_2_state == 1 or self.main_feed_valve_3_state == 1:
                self.send_action_append(['KSWO171', 'KSWO165', 'KSWO159'], [0, 0, 0])

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

            # Turbine Load Rate
            if self.load_rate <= 1:
                self.send_action_append(['KSWO227', 'KSWO226'], [1, 0])
            else:
                self.send_action_append(['KSWO227', 'KSWO226'], [0, 0])

        def range_fun(st, end, goal):
            if st <= self.Reactor_power < end:
                if self.load_set < goal:
                    self.send_action_append(['KSWO225', 'KSWO224'], [1, 0])  # 터빈 load를 150 Mwe 까지,
                else:
                    if self.Mwe_power + 2 > goal:
                        self.send_action_append(['KSWO225', 'KSWO224'], [1, 0])  # 터빈 load를 150 Mwe 까지,
                    else:
                        self.send_action_append(['KSWO225', 'KSWO224'], [0, 0])

        range_fun(st=0.05, end=0.10, goal=50)
        range_fun(st=0.10, end=0.15, goal=125)
        range_fun(st=0.15, end=0.20, goal=100)
        range_fun(st=0.20, end=0.25, goal=125)
        range_fun(st=0.25, end=0.30, goal=200)
        range_fun(st=0.30, end=0.35, goal=225)
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
        range_fun(st=0.90, end=0.95, goal=825)
        range_fun(st=0.95, end=0.100, goal=900)

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
        if self.Reactor_power >= 0.20 and self.Mwe_power >= 1 and self.cond_pump_2 == 0:
            self.send_action_append(['KSWO205'], [1])
        # 6) 출력 40% 이상 및 전기 출력이 380Mwe 이상 인경우
        # if self.Reactor_power >= 0.40 and self.Mwe_power >= 380 and self.main_feed_pump_2 == 0:
        if self.Reactor_power >= 0.40 and self.main_feed_pump_2 == 0:
            self.send_action_append(['KSWO193'], [1])
        # 7) 출력 50% 이상 및 전기 출력이 475Mwe
        # if self.Reactor_power >= 0.50 and self.Mwe_power >= 475 and self.cond_pump_3 == 0:
        if self.Reactor_power >= 0.50 and self.cond_pump_3 == 0:
            self.send_action_append(['KSWO206'], [1])
        # 8) 출력 80% 이상 및 전기 출력이 765Mwe
        # if self.Reactor_power >= 0.80 and self.Mwe_power >= 765 and self.main_feed_pump_3 == 0:
        if self.Reactor_power >= 0.80 and self.main_feed_pump_3 == 0:
            self.send_action_append(['KSWO192'], [1])

        # 9) 제어봉 조작 신호
        if divmod(self.Time_tick, 400)[1] == 0:
            if self.rod_pos[3] > 221:
                self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # NO ROD CONTROL
            else:
                self.send_action_append(['KSWO33', 'KSWO32'], [1, 0])  # UP ROD CONTROL
        else:
            self.send_action_append(['KSWO33', 'KSWO32'], [0, 0])  # NO ROD CONTROL

        # 9) 제어봉 조작 신호 및 보론 조작 신호를 보내기
        if self.COND_INIT:
            self.send_action_append(['KSWO75'], [1])
            if action == 0:  # stay pow
                pass
            elif action == 1:  # increase pow
                self.send_action_append(['KSWO33', 'KSWO32'], [1, 0])  # UP ROD CONTROL
            elif action == 2:  # decrease pow
                self.send_action_append(['EBOAC'], [50])  # MAKE-Up
        elif self.COND_ALL_ROD_OUT or self.COND_NET_BRK or self.COND_AFTER:
            if action == 0:  # stay pow
                self.send_action_append(['KSWO75', 'KSWO77'], [1, 0])  # BOR on / ALTDIL off
                self.send_action_append(['WBOAC', 'WDEWT'], [1, 8])  # Set-Make-up Valve
                self.send_action_append(['EBOAC', 'EDEWT'], [0, 0])  # NO INJECT BORN
            elif action == 1:  # increase pow
                self.send_action_append(['KSWO75', 'KSWO77'], [0, 1])  # BOR off / ALTDIL on
                self.send_action_append(['WBOAC', 'WDEWT'], [1, 8])  # Valve POS
                # self.send_action_append(['EBOAC', 'EDEWT'], [0, 70])   # MAKE-Up
                self.send_action_append(['EBOAC', 'EDEWT'], [0, 200])  # MAKE-Up
            elif action == 2:  # decrease pow
                self.send_action_append(['KSWO75', 'KSWO77'], [1, 0])  # BOR off / ALTDIL on
                self.send_action_append(['WBOAC', 'WDEWT'], [1, 8])  # Valve POS
                # self.send_action_append(['EBOAC', 'EDEWT'], [10, 0])   # BORN
                self.send_action_append(['EBOAC', 'EDEWT'], [5, 0])  # BORN
            else:
                print('ERROR ACT')
        else:
            print('ERROR CONTROL PART!!')

        self.CNS_udp._send_control_signal(self.para, self.val)

    def make_input(self, mem):
        # 사용되는 파라메터 전체 업데이트
        self.Time_tick = mem['KCNTOMS']['V']
        self.Reactor_power = mem['QPROREL']['V']  # 0.02
        self.Tavg = mem['UAVLEGM']['V']  # 308.21
        self.Tref = mem['UAVLEGS']['V']  # 308.22
        self.rod_pos = [mem[nub_rod]['V'] for nub_rod in ['KBCDO10', 'KBCDO9', 'KBCDO8', 'KBCDO7']]

        self.charging_valve_state = mem['KLAMPO95']['V']  # 0(Auto) - 1(Man)
        self.main_feed_valve_1_state = mem['KLAMPO147']['V']
        self.main_feed_valve_2_state = mem['KLAMPO148']['V']
        self.main_feed_valve_3_state = mem['KLAMPO149']['V']
        self.vct_level = mem['ZVCT']['V']  # 74.45
        self.pzr_level = mem['ZINST63']['V']  # 34.32
        #
        self.boron_conc = mem['KBCDO16']['V']
        self.make_up_tank = mem['EDEWT']['V']
        self.boron_tank = mem['EBOAC']['V']
        #
        self.Turbine_setpoint = mem['KBCDO17']['V']
        self.Turbine_ac = mem['KBCDO18']['V']  # Turbine ac condition
        self.Turbine_real = mem['KBCDO19']['V']  # 20
        self.load_set = mem['KBCDO20']['V']  # Turbine load set point
        self.load_rate = mem['KBCDO21']['V']  # Turbine load rate
        self.Mwe_power = mem['KBCDO22']['V']  # 0

        self.Netbreak_condition = mem['KLAMPO224']['V']  # 0 : Off, 1 : On
        self.trip_block = mem['KLAMPO22']['V']  # Trip block condition 0 : Off, 1 : On
        #
        self.steam_dump_condition = mem['KLAMPO150']['V']  # 0: auto 1: man
        self.heat_drain_pump_condition = mem['KLAMPO244']['V']  # 0: off, 1: on
        self.main_feed_pump_1 = mem['KLAMPO241']['V']  # 0: off, 1: on
        self.main_feed_pump_2 = mem['KLAMPO242']['V']  # 0: off, 1: on
        self.main_feed_pump_3 = mem['KLAMPO243']['V']  # 0: off, 1: on
        self.cond_pump_1 = mem['KLAMPO181']['V']  # 0: off, 1: on
        self.cond_pump_2 = mem['KLAMPO182']['V']  # 0: off, 1: on
        self.cond_pump_3 = mem['KLAMPO183']['V']  # 0: off, 1: on

        self.ax_off = mem['CAXOFF']['V']  # -0.63

        if self.COND_INIT:
            # Goal 1.8% ~ 2.2% 사이에서 출력 유지

            # Get Op bound
            self.Op_ref_power = 0.020  # 0.020 ~ 0.020
            self.Op_hi_bound = 0.030  # 0.030 ~ 0.030
            self.Op_low_bound = 0.010  # 0.010 ~ 0.010
            self.Op_ref_temp = 291.7  #
            self.Op_T_hi_bound = 291.7 + 10
            self.Op_T_low_bound = 291.7 - 10
            # Get Op distance from current power & temp
            self.Op_hi_distance = self.Op_hi_bound - self.Reactor_power
            self.Op_low_distance = self.Reactor_power - self.Op_low_bound
            self.Op_T_hi_distance = self.Op_T_hi_bound - self.Tavg
            self.Op_T_low_distance = self.Tavg - self.Op_T_low_bound
            # Get Fin distance reward
            self.R_distance = min(self.Op_hi_distance, self.Op_low_distance)
            if self.R_distance <= 0:
                self.R_distance = 0

            self.R_T_distance = min(self.Op_T_hi_distance, self.Op_T_low_distance)
            self.R_T_distance = 0
        elif self.COND_ALL_ROD_OUT:
            # Goal 시간 당 1% 씩 출력 증가

            # Get Op bound
            increse_pow_per = 0.01  # 시간당 0.03 -> 3% 증가
            one_tick = increse_pow_per / (60 * 300)  # 300Tick = 1분 -> 60 * 300 = 1시간
            # 1Tick 당 증가해야할 Power 계산
            update_tick = self.Time_tick - self.COND_INIT_END_TIME  # 현재 - All rod out 해온 운전 시간 빼기
            self.Op_ref_power = update_tick * one_tick + 0.02  # 0.020 ~ 1.000
            support_up = update_tick * one_tick * 1.2 + 0.02  # 0.020 ~ 1.000
            support_down = update_tick * one_tick * 0.8 + 0.02  # 0.020 ~ 1.000

            # if abs(self.Op_ref_power - support_up) >= 0.05:
            #     support_up = self.Op_ref_power + 0.05
            #     support_down = self.Op_ref_power - 0.05

            self.Op_hi_bound = support_up + 0.02  # 0.040 ~ 1.020
            self.Op_low_bound = support_down - 0.02  # 0.000 ~ 0.980
            self.Op_ref_temp = 291.7  #
            self.Op_T_hi_bound = 291.7 + 10
            self.Op_T_low_bound = 291.7 - 10
            # Get Op distance from current power & temp
            self.Op_hi_distance = self.Op_hi_bound - self.Reactor_power
            self.Op_low_distance = self.Reactor_power - self.Op_low_bound
            self.Op_T_hi_distance = self.Op_T_hi_bound - self.Tavg
            self.Op_T_low_distance = self.Tavg - self.Op_T_low_bound
            # Get Fin distance reward
            self.R_distance = min(self.Op_hi_distance, self.Op_low_distance)
            if self.R_distance <= 0:
                self.R_distance = 0

            self.R_T_distance = min(self.Op_T_hi_distance, self.Op_T_low_distance)
            self.R_T_distance = 0
        elif self.COND_NET_BRK:
            # Goal 시간 당 1% 씩 출력 증가 + Tre/ave 보상 제공

            # Get Op bound
            increse_pow_per = 0.01  # 시간당 0.03 -> 3% 증가
            one_tick = increse_pow_per / (60 * 300)  # 300Tick = 1분 -> 60 * 300 = 1시간
            # 1Tick 당 증가해야할 Power 계산
            update_tick = self.Time_tick - self.COND_INIT_END_TIME  # 현재 - All rod out 해온 운전 시간 빼기
            self.Op_ref_power = update_tick * one_tick + 0.02  # 0.020 ~ 1.000
            support_up = update_tick * one_tick * 1.2 + 0.02  # 0.020 ~ 1.000
            support_down = update_tick * one_tick * 0.8 + 0.02  # 0.020 ~ 1.000

            # if abs(self.Op_ref_power - support_up) >= 0.05:
            #     support_up = self.Op_ref_power + 0.05
            #     support_down = self.Op_ref_power - 0.05

            self.Op_hi_bound = support_up + 0.02  # 0.040 ~ 1.020
            self.Op_low_bound = support_down - 0.02  # 0.000 ~ 0.980
            self.Op_ref_temp = self.Tref  #
            self.Op_T_hi_bound = self.Tref + 10
            self.Op_T_low_bound = self.Tref - 10
            # Get Op distance from current power & temp
            self.Op_hi_distance = self.Op_hi_bound - self.Reactor_power
            self.Op_low_distance = self.Reactor_power - self.Op_low_bound
            self.Op_T_hi_distance = self.Op_T_hi_bound - self.Tavg
            self.Op_T_low_distance = self.Tavg - self.Op_T_low_bound
            # Get Fin distance reward
            self.R_distance = min(self.Op_hi_distance, self.Op_low_distance)
            if self.R_distance <= 0:
                self.R_distance = 0

            self.R_T_distance = min(self.Op_T_hi_distance, self.Op_T_low_distance)
            if self.R_distance <= 0:
                self.R_T_distance = 0
        elif self.COND_AFTER:
            # Goal 출력 유지.

            # Get Op bound
            increse_pow_per = 0.01  # 시간당 0.03 -> 3% 증가
            one_tick = increse_pow_per / (60 * 300)  # 300Tick = 1분 -> 60 * 300 = 1시간
            # 1Tick 당 증가해야할 Power 계산
            update_tick = self.COND_AFTER_TIME - self.COND_INIT_END_TIME  # 현재 - All rod out 해온 운전 시간 빼기
            self.Op_ref_power = update_tick * one_tick + 0.02  # 0.020 ~ 1.000
            self.Op_hi_bound = 0.99 + 0.02  # 0.040 ~ 1.020
            self.Op_low_bound = 0.99 - 0.02  # 0.000 ~ 0.980
            self.Op_ref_temp = self.Tref  #
            self.Op_T_hi_bound = self.Tref + 10
            self.Op_T_low_bound = self.Tref - 10
            # Get Op distance from current power & temp
            self.Op_hi_distance = self.Op_hi_bound - self.Reactor_power
            self.Op_low_distance = self.Reactor_power - self.Op_low_bound
            self.Op_T_hi_distance = self.Op_T_hi_bound - self.Tavg
            self.Op_T_low_distance = self.Tavg - self.Op_T_low_bound
            # Get Fin distance reward
            self.R_distance = min(self.Op_hi_distance, self.Op_low_distance)
            # if self.R_distance <= 0:
            #     self.R_distance = 0

            self.R_T_distance = min(self.Op_T_hi_distance, self.Op_T_low_distance)
            # if self.R_distance <= 0:
            #     self.R_T_distance = 0
        else:
            print('ERROR Reward Calculation STEP!')

            # Cond Check
            if self.COND_INIT:
                # Cond Check - 해당 상태의 목적 달성하면 상태변화 및 시간 기록 - 이 부분만 존재
                if self.rod_pos[3] >= 221:  # D 뱅크 최대 인출
                    self.COND_INIT = False  # Change COND !!
                    self.COND_ALL_ROD_OUT = True  #
                    self.COND_NET_BRK = False  #
                    self.COND_AFTER = False
                    self.COND_INIT_END_TIME = self.Time_tick  # Save current tick!
            elif self.COND_ALL_ROD_OUT:
                # Cond Check
                if self.Mwe_power >= 1:  # 전기 출력 발생
                    self.COND_INIT = False  # Change COND !!
                    self.COND_ALL_ROD_OUT = False  #
                    self.COND_NET_BRK = True  #
                    self.COND_AFTER = False
                    # self.COND_INIT_END_TIME = self.Time_tick    # Save current tick!
            elif self.COND_NET_BRK:
                # Cond Check
                if self.Reactor_power >= 0.98:  # 목표 도달
                    self.COND_INIT = False  # Change COND !!
                    self.COND_ALL_ROD_OUT = False  #
                    self.COND_NET_BRK = False  #
                    self.COND_AFTER = True
                    self.COND_AFTER_TIME = self.Time_tick  # Save current tick!
            elif self.COND_AFTER:
                pass
            else:
                print('ERROR COND Check')