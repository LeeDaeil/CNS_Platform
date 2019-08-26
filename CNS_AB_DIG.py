import multiprocessing
import time
import numpy as np
import copy
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler


class Power_increase_module(multiprocessing.Process):
    def __init__(self, mem, shut, cns_ip, cns_port):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]           # main mem connection

        self.auto_mem = mem[-2]     # 자율 운전 메모리
        self.dumy_auto_mem = copy.deepcopy(self.auto_mem)

        self.trig_mem = mem[1]      # 전략 설정 기능으로 부터의 로직
        self.shut = shut

        self.time_legnth = 10

    def p_shut(self, txt):
        if not self.shut:
            print(self, txt)

    # ================================================================================================================#
    def run(self):

        self.Dig_net = MainNet(net_type='LSTM', input_pa=136, output_pa=21, time_leg=10)
        self.Dig_net.load_model()
        with open('minmax.bin', 'rb') as f:
            self.mix_max = pickle.load(f)

        self.p_shut('네트워크 모델 로드')
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

                    input_data = self.make_input_data(time_legnth=self.time_legnth)
                    proba = self.Dig_net.predict_action(input_data)
                    print(proba)
            time.sleep(1)

    def make_input_data(self, time_legnth):
        # ------------------------------------------
        self.dumy_auto_mem = copy.deepcopy(self.auto_mem)
        # ------------------------------------------
        temp = []
        try:
            tick = self.mem['KCNTOMS']['L'][_]

            input_para = [
                self.mem['BFV122']['L'][_],
                self.mem['BFV478']['L'][_],
                self.mem['BFV479']['L'][_],
                self.mem['BFV488']['L'][_],
                self.mem['BFV489']['L'][_],
                self.mem['BFV498']['L'][_],
                self.mem['BFV499']['L'][_],
                self.mem['BHSV']['L'][_],
                self.mem['BHTBY']['L'][_],
                self.mem['BHV033']['L'][_],
                self.mem['BHV1']['L'][_],
                self.mem['BHV108']['L'][_],
                self.mem['BHV2']['L'][_],
                self.mem['BHV208']['L'][_],
                self.mem['BHV3']['L'][_],
                self.mem['BHV308']['L'][_],
                self.mem['BHV41']['L'][_],
                self.mem['BHV6']['L'][_],
                self.mem['BLV459']['L'][_],
                self.mem['BPORV']['L'][_],
                self.mem['BPSV10']['L'][_],
                self.mem['BPV145']['L'][_],
                self.mem['BRHSV']['L'][_],
                self.mem['BTV143']['L'][_],
                self.mem['BTV418']['L'][_],
                self.mem['BV101']['L'][_],
                self.mem['BV102']['L'][_],
                self.mem['BV201']['L'][_],
                self.mem['BV202']['L'][_],
                self.mem['BV301']['L'][_],
                self.mem['BV302']['L'][_],
                self.mem['KBCDO10']['L'][_],
                self.mem['KBCDO17']['L'][_],
                self.mem['KBCDO18']['L'][_],
                self.mem['KBCDO19']['L'][_],
                self.mem['KBCDO3']['L'][_],
                self.mem['KBCDO4']['L'][_],
                self.mem['KBCDO5']['L'][_],
                self.mem['KBCDO6']['L'][_],
                self.mem['KBCDO7']['L'][_],
                self.mem['KBCDO8']['L'][_],
                self.mem['KBCDO9']['L'][_],
                self.mem['KFV610']['L'][_],
                self.mem['KFV613']['L'][_],
                self.mem['KHV43']['L'][_],
                self.mem['KLAMPO110']['L'][_],
                self.mem['KLAMPO117']['L'][_],
                self.mem['KLAMPO118']['L'][_],
                self.mem['KLAMPO119']['L'][_],
                self.mem['KLAMPO144']['L'][_],
                self.mem['KLAMPO145']['L'][_],
                self.mem['KLAMPO146']['L'][_],
                self.mem['KLAMPO147']['L'][_],
                self.mem['KLAMPO148']['L'][_],
                self.mem['KLAMPO149']['L'][_],
                self.mem['KLAMPO201']['L'][_],
                self.mem['KLAMPO202']['L'][_],
                self.mem['KLAMPO203']['L'][_],
                self.mem['KLAMPO204']['L'][_],
                self.mem['KLAMPO206']['L'][_],
                self.mem['KLAMPO209']['L'][_],
                self.mem['KLAMPO216']['L'][_],
                self.mem['KLAMPO28']['L'][_],
                self.mem['KLAMPO28']['L'][_],
                self.mem['KLAMPO28']['L'][_],
                self.mem['KLAMPO28']['L'][_],
                self.mem['KLAMPO29']['L'][_],
                self.mem['KLAMPO29']['L'][_],
                self.mem['KLAMPO29']['L'][_],
                self.mem['KLAMPO29']['L'][_],
                self.mem['KLAMPO30']['L'][_],
                self.mem['KLAMPO30']['L'][_],
                self.mem['KLAMPO30']['L'][_],
                self.mem['KLAMPO30']['L'][_],
                self.mem['KLAMPO31']['L'][_],
                self.mem['KLAMPO31']['L'][_],
                self.mem['KLAMPO31']['L'][_],
                self.mem['KLAMPO31']['L'][_],
                self.mem['KLAMPO69']['L'][_],
                self.mem['KLAMPO70']['L'][_],
                self.mem['KLAMPO71']['L'][_],
                self.mem['KLAMPO84']['L'][_],
                self.mem['KLAMPO86']['L'][_],
                self.mem['KLAMPO89']['L'][_],
                self.mem['KLAMPO9']['L'][_],
                self.mem['KLAMPO95']['L'][_],
                self.mem['PVCT']['L'][_],
                self.mem['QPROREL']['L'][_],
                self.mem['QPRZH']['L'][_],
                self.mem['UAVLEG1']['L'][_],
                self.mem['UAVLEG2']['L'][_],
                self.mem['UAVLEG3']['L'][_],
                self.mem['UAVLEGM']['L'][_],
                self.mem['UCHGUT']['L'][_],
                self.mem['UNRHXUT']['L'][_],
                self.mem['UPRZ']['L'][_],
                self.mem['URHXUT']['L'][_],
                self.mem['WBOAC']['L'][_],
                self.mem['WCHGNO']['L'][_],
                self.mem['WDEWT']['L'][_],
                self.mem['WFWLN1']['L'][_],
                self.mem['WFWLN2']['L'][_],
                self.mem['WFWLN3']['L'][_],
                self.mem['WRCPSI1']['L'][_],
                self.mem['WRCPSI2']['L'][_],
                self.mem['WRCPSI3']['L'][_],
                self.mem['WRCPSR1']['L'][_],
                self.mem['WRCPSR2']['L'][_],
                self.mem['WRCPSR3']['L'][_],
                self.mem['WSPRAY']['L'][_],
                self.mem['WSTM1']['L'][_],
                self.mem['WSTM2']['L'][_],
                self.mem['WSTM3']['L'][_],
                self.mem['ZINST1']['L'][_],
                self.mem['ZINST101']['L'][_],
                self.mem['ZINST102']['L'][_],
                self.mem['ZINST124']['L'][_],
                self.mem['ZINST15']['L'][_],
                self.mem['ZINST2']['L'][_],
                self.mem['ZINST22']['L'][_],
                self.mem['ZINST3']['L'][_],
                self.mem['ZINST36']['L'][_],
                self.mem['ZINST56']['L'][_],
                self.mem['ZINST63']['L'][_],
                self.mem['ZINST65']['L'][_],
                self.mem['ZINST66']['L'][_],
                self.mem['ZINST67']['L'][_],
                self.mem['ZINST70']['L'][_],
                self.mem['ZINST71']['L'][_],
                self.mem['ZINST72']['L'][_],
                self.mem['ZINST73']['L'][_],
                self.mem['ZINST74']['L'][_],
                self.mem['ZINST75']['L'][_],
                self.mem['ZINST76']['L'][_],
                self.mem['ZINST77']['L'][_],
                self.mem['ZINST78']['L'][_],
                self.mem['ZINST85']['L'][_],
                self.mem['ZINST86']['L'][_],
                self.mem['ZINST87']['L'][_],
                self.mem['ZINST98']['L'][_],
                self.mem['ZINST99']['L'][_],
                self.mem['ZPRZNO']['L'][_],
                self.mem['ZPRZSP']['L'][_],
                self.mem['ZPRZUN']['L'][_],
                self.mem['ZSGNOR1']['L'][_],
                self.mem['ZSGNOR2']['L'][_],
                self.mem['ZSGNOR3']['L'][_],
                self.mem['ZVCT']['L'][_]
            ]
        except:
            pass
        for _ in reversed(range(-1, -(time_legnth*2), -2)): # 가장 끝에서 부터 저장하기 위해서
            pass

        # ------------------------------------------
        # 비정상 상태 진단 정보를 전달하기 위해서 Autonomous mem 에 정보를 전달
        self.dumy_auto_mem['Abnormal_Dig_result']['Result'].append(1)
        for key_val in self.auto_mem.keys():
            self.auto_mem[key_val] = self.dumy_auto_mem[key_val]
        # ------------------------------------------
        return temp

    # ================================================================================================================#
    # 2 Section - 네트워크 입출력 계산
    # ================================================================================================================#
    def sub_run_1(self, input_data, time_legnth):
        if len(input_data) == time_legnth:
            proba = self.Dig_net.predict_action(input_data)
            print(proba)
            self.p_shut('데이터 길이 완료 - 네트워크 계산 시작 - {}'.format(proba))
        else:
            self.p_shut('데이터 길이 부족함 - 네트워크 계산 대기')


class MainNet:
    def __init__(self, net_type='DNN', input_pa=1, output_pa=1, time_leg=1):
        self.net_type = net_type
        self.input_pa = input_pa
        self.output_pa = output_pa
        self.time_leg = time_leg
        self.all_dig, self.critic = self.build_model(in_pa=self.input_pa, time_leg=self.time_leg)

    def build_model(self, in_pa=1, time_leg=1):
        from keras.layers import Dense, Input, Conv1D, MaxPooling1D, CuDNNLSTM, Flatten
        from keras.models import Model

        state = Input(batch_shape=(None, time_leg, in_pa))
        shared = CuDNNLSTM(256)(state)
        shared = Dense(256, activation='relu')(shared)
        shared = Dense(512, activation='relu')(shared)
        shared = Dense(21, activation='softmax')(shared)

        model = Model(inputs=state, outputs=shared)
        return model

    def predict_action(self, input_window):
        predict_result = self.all_dig.predict([[input_window]])
        return predict_result

    def load_model(self):
        self.all_dig.load_weights("ab_nor_model.h5")
