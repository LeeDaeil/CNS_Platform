import numpy as np
from collections import deque
from CNS_Send_UDP import CNS_Send_Signal
import CNS_Platform_PARA as PARA


class controller_module:
    def __init__(self):
        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')  # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))
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

        # self.send_action_append(['KSWO78', 'WDEWT'], [1, 1])  # Makeup

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