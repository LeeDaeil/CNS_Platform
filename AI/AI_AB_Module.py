import pickle
import numpy as np
from collections import deque


class Abnormal_dig_module:
    def __init__(self, network):
        # minmax Load
        with open('./AI/AI_AB_DIG_MinMax.bin', 'rb') as f:
            self.mix_max = pickle.load(f)
        with open('./AI/AI_AB_Control_MinMax.bin', 'rb') as f:
            self.cont_mix_max = pickle.load(f)

        self.network = network
        self.stack_db = deque(maxlen=10)

    def predict_action(self, mem):
        self.make_input_data(mem=mem)
        # (10, 136) 나오므로 -> (1,10,136) 로 변환 해야함.

        input_array = np.array([self.stack_db])

        if input_array.shape[1] == 10:
            predict_result = self.network.predict(input_array)
            return predict_result[0] # 21개 결과값
        else:
            return [0 for _ in range(21)]

    def make_input_data(self, mem):
        # tick = mem['KCNTOMS']['Val']
        input_para = [
            mem['BFV122']['Val'], mem['BFV478']['Val'], mem['BFV479']['Val'],
            mem['BFV488']['Val'], mem['BFV489']['Val'], mem['BFV498']['Val'],
            mem['BFV499']['Val'], mem['BHSV']['Val'], mem['BHTBY']['Val'],
            mem['BHV033']['Val'], mem['BHV1']['Val'], mem['BHV108']['Val'],
            mem['BHV2']['Val'], mem['BHV208']['Val'], mem['BHV3']['Val'],
            mem['BHV308']['Val'], mem['BHV41']['Val'], mem['BHV6']['Val'],
            mem['BLV459']['Val'], mem['BPORV']['Val'], mem['BPSV10']['Val'],
            mem['BPV145']['Val'], mem['BRHSV']['Val'], mem['BTV143']['Val'],
            mem['BTV418']['Val'], mem['BV101']['Val'], mem['BV102']['Val'],
            mem['BV201']['Val'], mem['BV202']['Val'], mem['BV301']['Val'],
            mem['BV302']['Val'], mem['KBCDO10']['Val'], mem['KBCDO17']['Val'],
            mem['KBCDO18']['Val'], mem['KBCDO19']['Val'], mem['KBCDO3']['Val'],
            mem['KBCDO4']['Val'], mem['KBCDO5']['Val'], mem['KBCDO6']['Val'],
            mem['KBCDO7']['Val'], mem['KBCDO8']['Val'], mem['KBCDO9']['Val'],
            mem['KFV610']['Val'], mem['KFV613']['Val'], mem['KHV43']['Val'],
            mem['KLAMPO110']['Val'], mem['KLAMPO117']['Val'], mem['KLAMPO118']['Val'],
            mem['KLAMPO119']['Val'], mem['KLAMPO144']['Val'], mem['KLAMPO145']['Val'],
            mem['KLAMPO146']['Val'], mem['KLAMPO147']['Val'], mem['KLAMPO148']['Val'],
            mem['KLAMPO149']['Val'], mem['KLAMPO201']['Val'], mem['KLAMPO202']['Val'],
            mem['KLAMPO203']['Val'], mem['KLAMPO204']['Val'], mem['KLAMPO206']['Val'],
            mem['KLAMPO209']['Val'], mem['KLAMPO216']['Val'], mem['KLAMPO28']['Val'],
            mem['KLAMPO29']['Val'], mem['KLAMPO30']['Val'], mem['KLAMPO31']['Val'],
            mem['KLAMPO69']['Val'], mem['KLAMPO70']['Val'], mem['KLAMPO71']['Val'],
            mem['KLAMPO84']['Val'], mem['KLAMPO86']['Val'], mem['KLAMPO89']['Val'],
            mem['KLAMPO9']['Val'], mem['KLAMPO95']['Val'], mem['PVCT']['Val'],
            mem['QPROREL']['Val'], mem['QPRZH']['Val'], mem['UAVLEG1']['Val'],
            mem['UAVLEG2']['Val'], mem['UAVLEG3']['Val'], mem['UAVLEGM']['Val'],
            mem['UCHGUT']['Val'], mem['UNRHXUT']['Val'], mem['UPRZ']['Val'],
            mem['URHXUT']['Val'], mem['WBOAC']['Val'], mem['WCHGNO']['Val'],
            mem['WDEWT']['Val'], mem['WFWLN1']['Val'], mem['WFWLN2']['Val'],
            mem['WFWLN3']['Val'], mem['WRCPSI1']['Val'], mem['WRCPSI2']['Val'],
            mem['WRCPSI3']['Val'],
            mem['WRCPSR1']['Val'],
            mem['WRCPSR2']['Val'],
            mem['WRCPSR3']['Val'],
            mem['WSPRAY']['Val'],
            mem['WSTM1']['Val'],
            mem['WSTM2']['Val'],
            mem['WSTM3']['Val'],
            mem['ZINST1']['Val'],
            mem['ZINST101']['Val'],
            mem['ZINST102']['Val'],
            mem['ZINST124']['Val'],
            mem['ZINST15']['Val'],
            mem['ZINST2']['Val'],
            mem['ZINST22']['Val'],
            mem['ZINST3']['Val'],
            mem['ZINST36']['Val'],
            mem['ZINST56']['Val'],
            mem['ZINST63']['Val'],
            mem['ZINST65']['Val'],
            mem['ZINST66']['Val'],
            mem['ZINST67']['Val'],
            mem['ZINST70']['Val'],
            mem['ZINST71']['Val'],
            mem['ZINST72']['Val'],
            mem['ZINST73']['Val'],
            mem['ZINST74']['Val'],
            mem['ZINST75']['Val'],
            mem['ZINST76']['Val'],
            mem['ZINST77']['Val'],
            mem['ZINST78']['Val'],
            mem['ZINST85']['Val'],
            mem['ZINST86']['Val'],
            mem['ZINST87']['Val'],
            mem['ZINST98']['Val'],
            mem['ZINST99']['Val'],
            mem['ZPRZNO']['Val'],
            mem['ZPRZSP']['Val'],
            mem['ZPRZUN']['Val'],
            mem['ZSGNOR1']['Val'],
            mem['ZSGNOR2']['Val'],
            mem['ZSGNOR3']['Val'],
            mem['ZVCT']['Val'],
            mem['ZVCT']['Val'],  # 이거 뺴야함 137번째 더미 값
            ]
        out_min_max = self.mix_max.transform([input_para])[0] # 137번 값 제거

        self.stack_db.append(out_min_max[0:136])