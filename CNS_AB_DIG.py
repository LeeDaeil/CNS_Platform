import multiprocessing
import time
import numpy as np
import copy
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler


class Abnormal_dig_module(multiprocessing.Process):
    def __init__(self, mem, shut):
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
        with open('FIN_all_db_min_max_sc.bin', 'rb') as f:
            self.mix_max = pickle.load(f)

        self.p_shut('네트워크 모델 로드')
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
                    input_data = self.make_input_data(time_legnth=self.time_legnth)
                    if len(input_data) >= 10:
                        proba = self.Dig_net.predict_action(input_data)
                        # print(proba)
                        # ------------------------------------------
                        # 비정상 상태 진단 정보를 전달하기 위해서 Autonomous mem 에 정보를 전달
                        self.dumy_auto_mem['Abnormal_Dig_result']['Result'].append(proba[0])
                        for key_val in self.auto_mem.keys():
                            self.auto_mem[key_val] = self.dumy_auto_mem[key_val]
                        # ------------------------------------------
                    
            time.sleep(0.5)

    def make_input_data(self, time_legnth):
        # ------------------------------------------
        self.dumy_auto_mem = copy.deepcopy(self.auto_mem)
        # ------------------------------------------
        temp = []
        for _ in reversed(range(-1, -(time_legnth*2), -2)):
            try:
                tick = self.mem['KCNTOMS']['D'][_]
                input_para = [
                    self.mem['BFV122']['D'][_],
                    self.mem['BFV478']['D'][_],
                    self.mem['BFV479']['D'][_],
                    self.mem['BFV488']['D'][_],
                    self.mem['BFV489']['D'][_],
                    self.mem['BFV498']['D'][_],
                    self.mem['BFV499']['D'][_],
                    self.mem['BHSV']['D'][_],
                    self.mem['BHTBY']['D'][_],
                    self.mem['BHV033']['D'][_],
                    self.mem['BHV1']['D'][_],
                    self.mem['BHV108']['D'][_],
                    self.mem['BHV2']['D'][_],
                    self.mem['BHV208']['D'][_],
                    self.mem['BHV3']['D'][_],
                    self.mem['BHV308']['D'][_],
                    self.mem['BHV41']['D'][_],
                    self.mem['BHV6']['D'][_],
                    self.mem['BLV459']['D'][_],
                    self.mem['BPORV']['D'][_],
                    self.mem['BPSV10']['D'][_],
                    self.mem['BPV145']['D'][_],
                    self.mem['BRHSV']['D'][_],
                    self.mem['BTV143']['D'][_],
                    self.mem['BTV418']['D'][_],
                    self.mem['BV101']['D'][_],
                    self.mem['BV102']['D'][_],
                    self.mem['BV201']['D'][_],
                    self.mem['BV202']['D'][_],
                    self.mem['BV301']['D'][_],
                    self.mem['BV302']['D'][_],
                    self.mem['KBCDO10']['D'][_],
                    self.mem['KBCDO17']['D'][_],
                    self.mem['KBCDO18']['D'][_],
                    self.mem['KBCDO19']['D'][_],
                    self.mem['KBCDO3']['D'][_],
                    self.mem['KBCDO4']['D'][_],
                    self.mem['KBCDO5']['D'][_],
                    self.mem['KBCDO6']['D'][_],
                    self.mem['KBCDO7']['D'][_],
                    self.mem['KBCDO8']['D'][_],
                    self.mem['KBCDO9']['D'][_],
                    self.mem['KFV610']['D'][_],
                    self.mem['KFV613']['D'][_],
                    self.mem['KHV43']['D'][_],
                    self.mem['KLAMPO110']['D'][_],
                    self.mem['KLAMPO117']['D'][_],
                    self.mem['KLAMPO118']['D'][_],
                    self.mem['KLAMPO119']['D'][_],
                    self.mem['KLAMPO144']['D'][_],
                    self.mem['KLAMPO145']['D'][_],
                    self.mem['KLAMPO146']['D'][_],
                    self.mem['KLAMPO147']['D'][_],
                    self.mem['KLAMPO148']['D'][_],
                    self.mem['KLAMPO149']['D'][_],
                    self.mem['KLAMPO201']['D'][_],
                    self.mem['KLAMPO202']['D'][_],
                    self.mem['KLAMPO203']['D'][_],
                    self.mem['KLAMPO204']['D'][_],
                    self.mem['KLAMPO206']['D'][_],
                    self.mem['KLAMPO209']['D'][_],
                    self.mem['KLAMPO216']['D'][_],
                    self.mem['KLAMPO28']['D'][_],
                    self.mem['KLAMPO29']['D'][_],
                    self.mem['KLAMPO30']['D'][_],
                    self.mem['KLAMPO31']['D'][_],
                    self.mem['KLAMPO69']['D'][_],
                    self.mem['KLAMPO70']['D'][_],
                    self.mem['KLAMPO71']['D'][_],
                    self.mem['KLAMPO84']['D'][_],
                    self.mem['KLAMPO86']['D'][_],
                    self.mem['KLAMPO89']['D'][_],
                    self.mem['KLAMPO9']['D'][_],
                    self.mem['KLAMPO95']['D'][_],
                    self.mem['PVCT']['D'][_],
                    self.mem['QPROREL']['D'][_],
                    self.mem['QPRZH']['D'][_],
                    self.mem['UAVLEG1']['D'][_],
                    self.mem['UAVLEG2']['D'][_],
                    self.mem['UAVLEG3']['D'][_],
                    self.mem['UAVLEGM']['D'][_],
                    self.mem['UCHGUT']['D'][_],
                    self.mem['UNRHXUT']['D'][_],
                    self.mem['UPRZ']['D'][_],
                    self.mem['URHXUT']['D'][_],
                    self.mem['WBOAC']['D'][_],
                    self.mem['WCHGNO']['D'][_],
                    self.mem['WDEWT']['D'][_],
                    self.mem['WFWLN1']['D'][_],
                    self.mem['WFWLN2']['D'][_],
                    self.mem['WFWLN3']['D'][_],
                    self.mem['WRCPSI1']['D'][_],
                    self.mem['WRCPSI2']['D'][_],
                    self.mem['WRCPSI3']['D'][_],
                    self.mem['WRCPSR1']['D'][_],
                    self.mem['WRCPSR2']['D'][_],
                    self.mem['WRCPSR3']['D'][_],
                    self.mem['WSPRAY']['D'][_],
                    self.mem['WSTM1']['D'][_],
                    self.mem['WSTM2']['D'][_],
                    self.mem['WSTM3']['D'][_],
                    self.mem['ZINST1']['D'][_],
                    self.mem['ZINST101']['D'][_],
                    self.mem['ZINST102']['D'][_],
                    self.mem['ZINST124']['D'][_],
                    self.mem['ZINST15']['D'][_],
                    self.mem['ZINST2']['D'][_],
                    self.mem['ZINST22']['D'][_],
                    self.mem['ZINST3']['D'][_],
                    self.mem['ZINST36']['D'][_],
                    self.mem['ZINST56']['D'][_],
                    self.mem['ZINST63']['D'][_],
                    self.mem['ZINST65']['D'][_],
                    self.mem['ZINST66']['D'][_],
                    self.mem['ZINST67']['D'][_],
                    self.mem['ZINST70']['D'][_],
                    self.mem['ZINST71']['D'][_],
                    self.mem['ZINST72']['D'][_],
                    self.mem['ZINST73']['D'][_],
                    self.mem['ZINST74']['D'][_],
                    self.mem['ZINST75']['D'][_],
                    self.mem['ZINST76']['D'][_],
                    self.mem['ZINST77']['D'][_],
                    self.mem['ZINST78']['D'][_],
                    self.mem['ZINST85']['D'][_],
                    self.mem['ZINST86']['D'][_],
                    self.mem['ZINST87']['D'][_],
                    self.mem['ZINST98']['D'][_],
                    self.mem['ZINST99']['D'][_],
                    self.mem['ZPRZNO']['D'][_],
                    self.mem['ZPRZSP']['D'][_],
                    self.mem['ZPRZUN']['D'][_],
                    self.mem['ZSGNOR1']['D'][_],
                    self.mem['ZSGNOR2']['D'][_],
                    self.mem['ZSGNOR3']['D'][_],
                    self.mem['ZVCT']['D'][_],
                    self.mem['ZVCT']['D'][_], # 이거 뺴야함 137번째 더미 값
                ]

                out_min_max = self.mix_max.transform([input_para])[0] # 137번 값 제거
                # print(np.shape(out_min_max[0:136]))
                temp.append(out_min_max[0:136])

            except Exception as e:
                pass
                # print(self, e)

        return temp

    # ================================================================================================================#
    # 2 Section - 네트워크 입출력 계산
    # ================================================================================================================#
    def sub_run_1(self, input_data, time_legnth):
        if len(input_data) == time_legnth:
            proba = self.Dig_net.predict_action(input_data)
            # print(proba)
            self.p_shut('데이터 길이 완료 - 네트워크 계산 시작 - {}'.format(proba))
        else:
            self.p_shut('데이터 길이 부족함 - 네트워크 계산 대기')


class MainNet:
    def __init__(self, net_type='DNN', input_pa=1, output_pa=1, time_leg=1):
        self.net_type = net_type
        self.input_pa = input_pa
        self.output_pa = output_pa
        self.time_leg = time_leg
        self.all_dig = self.build_model(in_pa=self.input_pa, time_leg=self.time_leg)

    def build_model(self, in_pa=1, time_leg=1):
        from keras.layers import Dense, Input, Conv1D, MaxPooling1D, LSTM, Flatten
        from keras.models import Model

        state = Input(batch_shape=(None, time_leg, in_pa))
        shared = LSTM(256)(state)
        shared = Dense(256, activation='relu')(shared)
        shared = Dense(512, activation='relu')(shared)
        shared = Dense(21, activation='softmax')(shared)

        model = Model(inputs=state, outputs=shared)
        return model

    def predict_action(self, input_window):
        predict_result = self.all_dig.predict([[input_window]])
        return predict_result

    def load_model(self):
        self.all_dig.load_weights("ab_all_model.h5")
