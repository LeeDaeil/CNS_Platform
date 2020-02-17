import pickle
from collections import deque


class Abnormal_dig_module:
    def __init__(self, network):
        # minmax Load
        with open('FIN_all_db_min_max_sc.bin', 'rb') as f:
            self.mix_max = pickle.load(f)
        with open('C_in_sc.bin', 'rb') as f:
            self.cont_mix_max = pickle.load(f)
        
        self.network = network

    def predict_action(self, mem):
        input_window = self.make_input_data(mem=mem)
        # (10, 136) 나오므로 -> (1,10,136) 로 변환
        predict_result = self.network.predict([[input_window]])
        # (1, 21) 나오므로 -> (21) 로 변환
        return predict_result[0]

    def make_input_data(self, mem):
        temp = []
        for _ in range(0, 10): # D에서 0부터 9까지 가져옴.
            try:
                tick = mem['KCNTOMS']['D'][_]
                input_para = [
                    mem['BFV122']['D'][_], mem['BFV478']['D'][_], mem['BFV479']['D'][_],
                    mem['BFV488']['D'][_], mem['BFV489']['D'][_], mem['BFV498']['D'][_],
                    mem['BFV499']['D'][_], mem['BHSV']['D'][_], mem['BHTBY']['D'][_],
                    mem['BHV033']['D'][_], mem['BHV1']['D'][_], mem['BHV108']['D'][_],
                    mem['BHV2']['D'][_], mem['BHV208']['D'][_], mem['BHV3']['D'][_],
                    mem['BHV308']['D'][_], mem['BHV41']['D'][_], mem['BHV6']['D'][_],
                    mem['BLV459']['D'][_], mem['BPORV']['D'][_], mem['BPSV10']['D'][_],
                    mem['BPV145']['D'][_], mem['BRHSV']['D'][_], mem['BTV143']['D'][_],
                    mem['BTV418']['D'][_], mem['BV101']['D'][_], mem['BV102']['D'][_],
                    mem['BV201']['D'][_], mem['BV202']['D'][_], mem['BV301']['D'][_],
                    mem['BV302']['D'][_], mem['KBCDO10']['D'][_],mem['KBCDO17']['D'][_],
                    mem['KBCDO18']['D'][_], mem['KBCDO19']['D'][_], mem['KBCDO3']['D'][_],
                    mem['KBCDO4']['D'][_], mem['KBCDO5']['D'][_], mem['KBCDO6']['D'][_],
                    mem['KBCDO7']['D'][_], mem['KBCDO8']['D'][_], mem['KBCDO9']['D'][_],
                    mem['KFV610']['D'][_], mem['KFV613']['D'][_], mem['KHV43']['D'][_],
                    mem['KLAMPO110']['D'][_], mem['KLAMPO117']['D'][_], mem['KLAMPO118']['D'][_],
                    mem['KLAMPO119']['D'][_], mem['KLAMPO144']['D'][_], mem['KLAMPO145']['D'][_],
                    mem['KLAMPO146']['D'][_], mem['KLAMPO147']['D'][_], mem['KLAMPO148']['D'][_],
                    mem['KLAMPO149']['D'][_], mem['KLAMPO201']['D'][_], mem['KLAMPO202']['D'][_],
                    mem['KLAMPO203']['D'][_], mem['KLAMPO204']['D'][_], mem['KLAMPO206']['D'][_],
                    mem['KLAMPO209']['D'][_], mem['KLAMPO216']['D'][_], mem['KLAMPO28']['D'][_],
                    mem['KLAMPO29']['D'][_], mem['KLAMPO30']['D'][_], mem['KLAMPO31']['D'][_],
                    mem['KLAMPO69']['D'][_], mem['KLAMPO70']['D'][_], mem['KLAMPO71']['D'][_],
                    mem['KLAMPO84']['D'][_], mem['KLAMPO86']['D'][_], mem['KLAMPO89']['D'][_],
                    mem['KLAMPO9']['D'][_], mem['KLAMPO95']['D'][_], mem['PVCT']['D'][_],
                    mem['QPROREL']['D'][_], mem['QPRZH']['D'][_], mem['UAVLEG1']['D'][_],
                    mem['UAVLEG2']['D'][_], mem['UAVLEG3']['D'][_], mem['UAVLEGM']['D'][_],
                    mem['UCHGUT']['D'][_], mem['UNRHXUT']['D'][_], mem['UPRZ']['D'][_],
                    mem['URHXUT']['D'][_], mem['WBOAC']['D'][_], mem['WCHGNO']['D'][_],
                    mem['WDEWT']['D'][_], mem['WFWLN1']['D'][_], mem['WFWLN2']['D'][_],
                    mem['WFWLN3']['D'][_], mem['WRCPSI1']['D'][_], mem['WRCPSI2']['D'][_],
                    mem['WRCPSI3']['D'][_],
                    mem['WRCPSR1']['D'][_],
                    mem['WRCPSR2']['D'][_],
                    mem['WRCPSR3']['D'][_],
                    mem['WSPRAY']['D'][_],
                    mem['WSTM1']['D'][_],
                    mem['WSTM2']['D'][_],
                    mem['WSTM3']['D'][_],
                    mem['ZINST1']['D'][_],
                    mem['ZINST101']['D'][_],
                    mem['ZINST102']['D'][_],
                    mem['ZINST124']['D'][_],
                    mem['ZINST15']['D'][_],
                    mem['ZINST2']['D'][_],
                    mem['ZINST22']['D'][_],
                    mem['ZINST3']['D'][_],
                    mem['ZINST36']['D'][_],
                    mem['ZINST56']['D'][_],
                    mem['ZINST63']['D'][_],
                    mem['ZINST65']['D'][_],
                    mem['ZINST66']['D'][_],
                    mem['ZINST67']['D'][_],
                    mem['ZINST70']['D'][_],
                    mem['ZINST71']['D'][_],
                    mem['ZINST72']['D'][_],
                    mem['ZINST73']['D'][_],
                    mem['ZINST74']['D'][_],
                    mem['ZINST75']['D'][_],
                    mem['ZINST76']['D'][_],
                    mem['ZINST77']['D'][_],
                    mem['ZINST78']['D'][_],
                    mem['ZINST85']['D'][_],
                    mem['ZINST86']['D'][_],
                    mem['ZINST87']['D'][_],
                    mem['ZINST98']['D'][_],
                    mem['ZINST99']['D'][_],
                    mem['ZPRZNO']['D'][_],
                    mem['ZPRZSP']['D'][_],
                    mem['ZPRZUN']['D'][_],
                    mem['ZSGNOR1']['D'][_],
                    mem['ZSGNOR2']['D'][_],
                    mem['ZSGNOR3']['D'][_],
                    mem['ZVCT']['D'][_],
                    mem['ZVCT']['D'][_], # 이거 뺴야함 137번째 더미 값
                ]
                out_min_max = self.mix_max.transform([input_para])[0] # 137번 값 제거
                temp.append(out_min_max[0:136])
            except Exception as e:
                pass
        return temp