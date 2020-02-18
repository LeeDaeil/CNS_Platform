import numpy as np
from CNS_Send_UDP import CNS_Send_Signal
import CNS_Platform_PARA as PARA
from collections import deque


class pzr_controller_module:
    def __init__(self, network):

        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')  # [cns ip],[cns port]
        self.CNS_udp = CNS_Send_Signal(self.cns_ip, int(self.cns_port))

        self.network = network

    def predict_action(self, mem, tirg_mem):

        input_data = self.make_input_data(mem=mem)
        if len(mem['KCNTOMS']['D']) >= 10:  # PZR가 동작하지 않는 경우에도 데이터를 계산하기 위해서 사용
            predict_result = self.network.predict([[input_data[5:10]]]) # 10가 아니라 5개 라서
            policy = predict_result[0]
            action = np.random.choice(np.shape(policy)[0], 1, p=policy)[0]
            # 계산된 액션은 CNS로 보내짐.
            self.send_action(mem=mem, trig_mem=tirg_mem, action=action)

        return input_data[-1]  # action, proba, 마지막 네트워크 값

    def make_input_data(self, mem):
        temp = []
        for _ in range(0, len(mem['KCNTOMS']['D'])):  # PZR가 동작하지 않는 경우에도 데이터를 계산하기 위해서 사용
            try:
                # 사용되는 파라메터 전체 업데이트
                self.PZR_pressure = mem['ZINST58']['D'][_]  # 25.47
                self.PZR_level = mem['ZINST63']['D'][_]  # 100.00
                self.PZR_temp = mem['UPRZ']['D'][_]  # 68.74
                self.PZR_Back_heater = mem['KLAMPO118']['D'][_]  # 0(off) - 1(on)
                self.PZR_Back_on_off_act = mem['KSWO125']['D'][_]  # 0(off) - 1(on)
                self.PZR_Pro_heater = mem['QPRZH']['D'][_]  # 0-1 pos
                self.PZR_Pro_close_act = mem['KSWO121']['D'][_]  # Close (0 off - 1 on)
                self.PZR_Pro_open_act = mem['KSWO122']['D'][_]  # Open (0 off - 1 on)
                self.HV142_man = mem['KLAMPO89']['D'][_]  # 0(Auto) - 1(Man)

                self.HV142_pos = mem['BHV142']['D'][_]  # 13.95
                self.HV142_close_act = mem['KSWO231']['D'][_]  # Close (0 off - 1 on)
                self.HV145_open_act = mem['KSWO232']['D'][_]  # Open (0 off - 1 on)

                self.BFV122_man = mem['KLAMPO95']['D'][_]  # 0(Auto) - 1(Man)
                self.BFV122_pos = mem['BFV122']['D'][_]  # 0.70
                self.BFV122_close_act = mem['KSWO101']['D'][_]  # Close (0 off - 1 on)
                self.BFV122_open_act = mem['KSWO102']['D'][_]  # Open (0 off - 1 on)
                self.Charging_flow = mem['WCHGNO']['D'][_]  # 7.5
                self.Letdown_HX_flow = mem['WNETLD']['D'][_]  # 8.43
                self.Letdown_HX_temp = mem['UNRHXUT']['D'][_]  # 34.07
                self.Core_out_temp = mem['UUPPPL']['D'][_]  # 54.92

                # 가압기 안전 영역 설정 및 보상 계산
                self.PZR_pressure_float = self.PZR_pressure / 100  # 현재 압력을 float로 변환 25.47 -> 0.2547

                self.top_safe_pressure_boundary = 0.30
                self.bottom_safe_pressure_bondary = 0.20
                self.middle_safe_pressure = 0.25

                self.distance_top_current = self.top_safe_pressure_boundary - self.PZR_pressure_float
                self.distance_bottom_current = self.PZR_pressure_float - self.bottom_safe_pressure_bondary
                self.distance_mid = abs(self.PZR_pressure_float - self.middle_safe_pressure)
                
                temp.append([
                    # 네트워크의 Input 에 들어 가는 변수 들
                    self.PZR_pressure_float / 100, self.distance_top_current, self.distance_bottom_current,
                    self.Charging_flow / 100, self.BFV122_pos, self.distance_mid,
                    self.HV142_pos
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

    def send_action(self, mem, trig_mem, action):

        # 전송될 변수와 값 저장하는 리스트
        self.para = []
        self.val = []

        self.PZR_pressure = mem['ZINST58']['V']  # 25.47
        self.PZR_level = mem['ZINST63']['V']  # 100.00
        self.PZR_temp = mem['UPRZ']['V']  # 68.74
        self.PZR_Back_heater = mem['KLAMPO118']['V']  # 0(off) - 1(on)
        self.PZR_Back_on_off_act = mem['KSWO125']['V']  # 0(off) - 1(on)
        self.PZR_Pro_heater = mem['QPRZH']['V']  # 0-1 pos
        self.PZR_Pro_close_act = mem['KSWO121']['V']  # Close (0 off - 1 on)
        self.PZR_Pro_open_act = mem['KSWO122']['V']  # Open (0 off - 1 on)
        self.HV142_man = mem['KLAMPO89']['V']  # 0(Auto) - 1(Man)

        self.HV142_pos = mem['BHV142']['V']  # 13.95
        self.HV142_close_act = mem['KSWO231']['V']  # Close (0 off - 1 on)
        self.HV145_open_act = mem['KSWO232']['V']  # Open (0 off - 1 on)

        self.BFV122_man = mem['KLAMPO95']['V']  # 0(Auto) - 1(Man)
        self.BFV122_pos = mem['BFV122']['V']  # 0.70
        self.BFV122_close_act = mem['KSWO101']['V']  # Close (0 off - 1 on)
        self.BFV122_open_act = mem['KSWO102']['V']  # Open (0 off - 1 on)
        self.Charging_flow = mem['WCHGNO']['V']  # 7.5
        self.Letdown_HX_flow = mem['WNETLD']['V']  # 8.43
        self.Letdown_HX_temp = mem['UNRHXUT']['V']  # 34.07
        self.Core_out_temp = mem['UUPPPL']['V']  # 54.92

        # All Heater On
        if self.PZR_Back_heater == 0:
            self.send_action_append(['KSWO125'], [1])   # Back Heater on
        # else:
        #     self.send_action_append(['KSWO125'], [0])  # Back Heater on
        if self.PZR_Pro_heater != 1:
            self.send_action_append(['KSWO122'], [1])  # Pro up

        if action == 0:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [0, 0, 0, 0])   # All Stay
        elif action == 1:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [1, 0, 0, 0])   # HV142 Close, BFV122 Stay
        elif action == 2:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [0, 1, 0, 0])   # HV142 Open, BFV122 Stay
        elif action == 3:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [0, 0, 1, 0])   # HV142 Stay, BFV122 Close
        elif action == 4:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [1, 0, 1, 0])   # HV142 Close, BFV122 Close
        elif action == 5:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [0, 1, 1, 0])   # HV142 Open, BFV122 Close
        elif action == 6:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [0, 0, 0, 1])   # HV142 Stay, BFV122 Open
        elif action == 7:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [1, 0, 0, 1])   # HV142 Close, BFV122 Open
        elif action == 8:
            self.send_action_append(['KSWO231', 'KSWO232', 'KSWO101', 'KSWO102'], [0, 1, 0, 1])   # HV142 Open, BFV122 Open

        self.CNS_udp._send_control_signal(self.para, self.val)