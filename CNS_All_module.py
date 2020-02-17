import multiprocessing
import CNS_Platform_PARA as PARA
import copy
from CNS_Module_ALL_AI_Unit import MainNet
from CNS_Module_AB_Dig import Abnormal_dig_module as AB_DIG_M
from time import sleep
import pickle
import numpy as np


class All_Function_module(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)

        self.mem = mem[0]  # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

        self.temp_mem = copy.deepcopy(self.mem)
        self.temp_trig_mem = copy.deepcopy(self.trig_mem)

        self.AI_AGENT = MainNet()
        self.AB_DIG_M = AB_DIG_M(network=self.AI_AGENT.AB_DIG_AI)   # 비정상 진단 AI 모듈 불러옴

    def run(self):
        while True:
            if self.trig_mem['Loop'] and self.trig_mem['Run']:
                print('계산중....', end='\t')
                # # 1. Mem 변경을 위해 Copy
                self.temp_mem = copy.deepcopy(self.mem)
                self.temp_trig_mem = copy.deepcopy(self.trig_mem)

                # 1.1 원자로 트립 시 비상으로 변경
                if self.temp_mem['KRXTRIP']['V'] == 1:
                    self.temp_trig_mem['OPStrategy'] = PARA.Emergency
                else:
                    self.temp_trig_mem['OPStrategy'] = PARA.Normal

                # 2. Dig 에서 변경 사항 업데이트
                print('DIG 모듈 계산 시작->', end='\t')
                self.temp_trig_mem['Event_DIG_His']['X'].append(self.mem['KCNTOMS']['V'])   # x 값 업데이트
                if self.temp_trig_mem['OPStrategy'] == PARA.Abnormal or len(self.mem['KCNTOMS']['D']) >= 10:
                    # 비정상이 발생 했고, AB_DIG_M의 Local Input 데이터가 10이 되면 진단 결과 보여줌.
                    # 현재는 Or 이지만, Abnormal 진단 모듈 완성되면 And로 바꿔야함.
                    self.temp_trig_mem['Event_DIG_His']['Y'].append(self.AB_DIG_M.predict_action(self.mem))
                else:
                    self.temp_trig_mem['Event_DIG_His']['Y'].append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                print('DIG 모듈 계산 종료 ... ', end='\t')

                # 3. 최종 MEM 업데이트 =================================================================================
                print('계산 종료! ....', end='\t')
                self.temp_trig_mem['Run'] = False

                for key_val in self.temp_trig_mem.keys():
                    self.trig_mem[key_val] = self.temp_trig_mem[key_val]
                print(self.mem['KCNTOMS'], self.trig_mem['Loop'], self.trig_mem['Run'])
                # End =================================================================================================
