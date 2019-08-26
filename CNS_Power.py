import multiprocessing
import time
import numpy as np
import CNS_Send_UDP
import copy


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

    def p_shut(self, txt):
        if not self.shut:
            print(self, txt)

    # ================================================================================================================#
    def run(self):

        self.Rod_net = MainNet(net_type='LSTM', input_pa=6, output_pa=3, time_leg=10)
        self.Rod_net.load_model()
        self.p_shut('네트워크 모델 로드')
        if not self.shut:
            self.Rod_net.actor.summary()
            self.Rod_net.critic.summary()

        while True:
            #==========================================================================================#
            if self.mem['KCNTOMS']['V'] == 0:
                self.p_shut('초기 조건 상태가 감지 - 모듈 대기')
                self.mem_len = len(self.mem['KCNTOMS']['L'])
            # ==========================================================================================#
            else:
                if self.mem_len == len(self.mem['KCNTOMS']['L']):
                    self.p_shut('CNS가 정지된 상태 - 모듈 대기')
                else:
                    self.p_shut('CNS가 동작 상태 - 모듈 동작')
                    self.mem_len = len(self.mem['KCNTOMS']['L'])
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
                tick = self.mem['KCNTOMS']['L'][_]
                power = self.mem['QPROREL']['L'][_]
                base_condition = tick / 30000
                up_base_condition = (tick * 53) / 1470000
                low_base_condition = (tick * 3) / 98000

                stady_condition = base_condition + 0.02

                distance_up = up_base_condition + 0.04 - power
                distance_low = power - low_base_condition

                Mwe_power = self.mem['KBCDO22']['L'][_]
                load_set = self.mem['KBCDO20']['L'][_]

                temp.append([power, distance_up, distance_low, stady_condition, Mwe_power/1000, load_set/100])
            except:
                pass

        # ------------------------------------------
        # 제어봉 Display로 정보를 전달하기 위해서 Autonomous mem 에 정보를 전달
        self.dumy_auto_mem['Start_up_operation_his']['power'].append(power)
        self.dumy_auto_mem['Start_up_operation_his']['up_cond'].append(up_base_condition + 0.07)
        self.dumy_auto_mem['Start_up_operation_his']['low_cond'].append(low_base_condition + 0.01)

        for key_val in self.auto_mem.keys():
            self.auto_mem[key_val] = self.dumy_auto_mem[key_val]
        # ------------------------------------------
        return temp

    # ================================================================================================================#
    # 2 Section - 네트워크 입출력 계산
    # ================================================================================================================#
    def sub_run_1(self, input_data, time_legnth):
        if len(input_data) == time_legnth:
            act, proba = self.Rod_net.predict_action(input_data)
            # print(act, proba)
            self.p_shut('데이터 길이 완료 - 네트워크 계산 시작 - {}'.format(act))
            if act == 0:
                self.UDP_sock._send_control_signal(['KSWO33', 'KSWO32'], [0, 0])
            elif act == 1:
                self.UDP_sock._send_control_signal(['KSWO33', 'KSWO32'], [1, 0])
            elif act == 2:
                self.UDP_sock._send_control_signal(['KSWO33', 'KSWO32'], [0, 1])
        else:
            self.p_shut('데이터 길이 부족함 - 네트워크 계산 대기')

class MainNet:
    def __init__(self, net_type='DNN', input_pa=1, output_pa=1, time_leg=1):
        self.net_type = net_type
        self.input_pa = input_pa
        self.output_pa = output_pa
        self.time_leg = time_leg
        self.actor, self.critic = self.build_model(net_type=self.net_type, in_pa=self.input_pa,
                                                   ou_pa=self.output_pa, time_leg=self.time_leg)

    def build_model(self, net_type='DNN', in_pa=1, ou_pa=1, time_leg=1):
        from keras.layers import Dense, Input, Conv1D, MaxPooling1D, LSTM, Flatten
        from keras.models import Model
        # 8 16 32 64 128 256 512 1024 2048
        if net_type == 'DNN':
            state = Input(batch_shape=(None, in_pa))
            shared = Dense(32, input_dim=in_pa, activation='relu', kernel_initializer='glorot_uniform')(state)
            # shared = Dense(48, activation='relu', kernel_initializer='glorot_uniform')(shared)

        elif net_type == 'CNN' or net_type == 'LSTM' or net_type == 'CLSTM':
            state = Input(batch_shape=(None, time_leg, in_pa))
            if net_type == 'CNN':
                shared = Conv1D(filters=10, kernel_size=3, strides=1, padding='same')(state)
                shared = MaxPooling1D(pool_size=2)(shared)
                shared = Flatten()(shared)

            elif net_type == 'LSTM':
                shared = LSTM(32, activation='relu')(state)
                shared = Dense(64)(shared)

            elif net_type == 'CLSTM':
                shared = Conv1D(filters=10, kernel_size=3, strides=1, padding='same')(state)
                shared = MaxPooling1D(pool_size=2)(shared)
                shared = LSTM(8)(shared)

        # ----------------------------------------------------------------------------------------------------
        # Common output network
        actor_hidden = Dense(64, activation='relu', kernel_initializer='glorot_uniform')(shared)
        action_prob = Dense(ou_pa, activation='softmax', kernel_initializer='glorot_uniform')(actor_hidden)

        value_hidden = Dense(32, activation='relu', kernel_initializer='he_uniform')(shared)
        state_value = Dense(1, activation='linear', kernel_initializer='he_uniform')(value_hidden)

        actor = Model(inputs=state, outputs=action_prob)
        critic = Model(inputs=state, outputs=state_value)

        actor._make_predict_function()
        critic._make_predict_function()

        return actor, critic

    def predict_action(self, input_window):
        predict_result = self.actor.predict([[input_window]])
        policy = predict_result[0]
        action = np.random.choice(np.shape(policy)[0], 1, p=policy)[0]
        return action, predict_result

    def load_model(self):
        self.actor.load_weights("ROD_A3C_actor.h5")
        self.critic.load_weights("ROD_A3C_cric.h5")
