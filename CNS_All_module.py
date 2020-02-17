import multiprocessing
import CNS_Platform_PARA as PARA
import copy
from time import sleep


class All_Function_module(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)

        self.mem = mem[0]  # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

        self.temp_mem = copy.deepcopy(self.mem)
        self.temp_trig_mem = copy.deepcopy(self.trig_mem)

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
                self.temp_trig_mem['Event_DIG_His']['X'].append(self.mem['KCNTOMS']['V'])
                self.temp_trig_mem['Event_DIG_His']['Y'].append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

                # 3. 최종 MEM 업데이트

                print('계산 종료! ....', end='\t')
                self.temp_trig_mem['Run'] = False

                for key_val in self.temp_trig_mem.keys():
                    self.trig_mem[key_val] = self.temp_trig_mem[key_val]
                print(self, self.mem['KCNTOMS'], self.trig_mem['Loop'], self.trig_mem['Run'])
