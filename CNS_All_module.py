import multiprocessing
import numpy as np
import copy
#
from TOOL.TOOL_etc import ToolEtc
from ENVCNS import ENVCNS
# from CNS_AIl_AI_module import MainNet
# from CNS_Module_ALL_AI_Unit import MainNet
# from CNS_Module_AB_Dig import Abnormal_dig_module as AB_DIG_M
# from CNS_Module_ROD import rod_controller_module as ROD_CONT
# from CNS_Module_PZR import pzr_controller_module as PZR_CONT
# from CNS_Module_SAMPLE_CONTROLLER import controller_module as SAMP_CONT

import time


class All_Function_module(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)

        self.mem = mem[0]        # main mem connection
        self.trig_mem = mem[-1]  # main mem connection

        # self.copy_mem = copy.deepcopy(self.mem)
        self.copy_trig_mem = copy.deepcopy(self.trig_mem)

        # 1 CNS 환경 생성 ----------------------------------------------------
        # CNS 정보 읽기
        with open('CNS_Info.txt', 'r') as f:
            self.cns_ip, self.cns_port = f.read().split('\t')   # [cns ip],[cns port]
        self.cns_env = ENVCNS(Name='EnvCNS', IP=self.cns_ip, PORT=int(self.cns_port))

        # 2 AI network Load -------------------------------------------------
        # self.AI_AGENT = MainNet()
        # self.AB_DIG_M = AB_DIG_M(network=self.AI_AGENT.AB_DIG_AI)   # 비정상 진단 AI 모듈 불러옴
        # self.ROD_CONT = ROD_CONT(network=None)   # 정상에서 Rod control module
        # self.PZR_CONT = PZR_CONT(network=self.AI_AGENT.PZR_actor)   # 가압기 기포생성 모듈
        # self.SAMP_CONT = SAMP_CONT()

    def _update_cnsenv_to_sharedmem(self):
        # st = time.time()
        for key_val in self.cns_env.mem.keys():
            self.mem[key_val] = self.cns_env.mem[key_val]
        # print(time.time()-st)

    def run(self):
        # AI Model Call
        from CNS_AIl_AI_module import Mainnet
        from AI.AI_SV_Module import Signal_Validation
        SV_net = Signal_Validation(net=Mainnet().net_1)

        self.cns_env.reset(file_name=f'Log{ToolEtc.get_now_time()}', initial_nub=1)
        self._update_cnsenv_to_sharedmem()
        while True:
            # Speed ----------------------------------------------------------------------
            if self.trig_mem['Speed_Call']:
                self.cns_env.want_tick = self.trig_mem['Speed']
                self.trig_mem['Speed_Call'] = False
            # Init -----------------------------------------------------------------------
            if self.trig_mem['Init_Call']:
                self.cns_env.reset(file_name=f'Log{ToolEtc.get_now_time()}', initial_nub=self.trig_mem['Init_nub'])
                self.trig_mem['Init_Call'] = False
            else:
                # Mal fun, Run logic -----------------------------------------------------
                if self.trig_mem['Mal_Call']:
                    # 1] 마지막 Mal send
                    last_nub = len(self.trig_mem['Mal_list'])
                    get_mal_nub = self.trig_mem['Mal_list'][last_nub]['Mal_nub']
                    get_mal_opt = self.trig_mem['Mal_list'][last_nub]['Mal_opt']
                    get_mal_time = self.trig_mem['Mal_list'][last_nub]['Mal_time']
                    self.cns_env._send_malfunction_signal(get_mal_nub, get_mal_opt, get_mal_time)
                    self.trig_mem['Mal_Call'] = False
                if self.trig_mem['Run']:
                    # t
                    # Control... TODO
                    # t + 1
                    self.cns_env.step(A=0)

                    if self.cns_env.mem['KCNTOMS']['Val'] > 300:
                        self.cns_env.mem['UUPPPL']['Val'] = 450

                    self._monitoring(SV_net)
            # Update mem ------------------------------------------------------------------
            self._update_cnsenv_to_sharedmem()

    def _monitoring(self, SV_net):
        # 1. 정상 or 비상 판별
        if self.cns_env.mem['KLAMPO9']['Val'] == 1:
            self.trig_mem['Operation_Strategy'] = 'E'
        else:
            self.trig_mem['Operation_Strategy'] = 'N'

        # 진단 모듈 아래 넣을 것 TODO
        get_result = SV_net.step(self.cns_env.mem)  # {'cPara': val, ... }
        # SV의 값을 cns 메모리에 업데이트
        for key in get_result.keys():
            self.cns_env.mem[f'c{key}']['Val'] = get_result[key]

        pass

        # while True:
        #     if self.trig_mem['Loop'] and self.trig_mem['Run']:
        #         print('Run..', end='\t')
        #         time.sleep(1)
        #         # 3. 최종 MEM 업데이트 =================================================================================
        #         print('Stop!', end='\t')
        #         self.temp_trig_mem['Run'] = False
        #
        #         for key_val in self.temp_trig_mem.keys():
        #             self.trig_mem[key_val] = self.temp_trig_mem[key_val]
        #
        #         # for _ in range(0, 1605):
        #         #     print('Run..', end='\t')
        #         #     # # 1. Mem 변경을 위해 Copy
        #         #     self.temp_mem = copy.deepcopy(self.mem)
        #         #     self.temp_trig_mem = copy.deepcopy(self.trig_mem)
        #         #
        #         #     # 1.1 원자로 트립 시 비상으로 변경
        #         #     # if self.temp_mem['KRXTRIP']['V'] == 1:
        #         #     #     if self.temp_trig_mem['ST_OPStratey'] == PARA.PZR_OP:
        #         #     #         self.temp_trig_mem['OPStrategy'] = PARA.Normal
        #         #     #     else:
        #         #     #         self.temp_trig_mem['OPStrategy'] = PARA.Emergency
        #         #     # else:
        #         #     #     self.temp_trig_mem['OPStrategy'] = PARA.Normal
        #         #
        #         #     # # 2. Dig 에서 변경 사항 업데이트 ========================================================
        #         #     # print('DIG 모듈->', end=' ')
        #         #     # self.temp_trig_mem['Event_DIG_His']['X'].append(self.temp_mem['KCNTOMS']['V'])   # x 값 업데이트
        #         #     # if self.temp_trig_mem['OPStrategy'] == PARA.Abnormal or len(self.temp_mem['KCNTOMS']['D']) >= 10:
        #         #     #     # 비정상이 발생 했고, AB_DIG_M의 Local Input 데이터가 10이 되면 진단 결과 보여줌.
        #         #     #     # 현재는 Or 이지만, Abnormal 진단 모듈 완성되면 And로 바꿔야함.
        #         #     #     self.temp_trig_mem['Event_DIG_His']['Y'].append(self.AB_DIG_M.predict_action(self.temp_mem))
        #         #     #     print('[W]', end=' ')
        #         #     # else:
        #         #     #     self.temp_trig_mem['Event_DIG_His']['Y'].append([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #         #     #                                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        #         #     #     print('[S]', end=' ')
        #         #     # print('<-DIG 모듈', end='#')
        #         #     #
        #         #     # # 3. ROD_CONT의 제어 ============================================================
        #         #     # if self.temp_trig_mem['ST_OPStratey'] == PARA.ST_OP:
        #         #     #     print('ROD_CONT 모듈->', end=' ')
        #         #     #     if len(self.temp_mem['KCNTOMS']['D']) >= 1:
        #         #     #         self.temp_trig_mem['Rod_His']['X'].append(self.temp_mem['KCNTOMS']['V']*self.temp_trig_mem['Speed']/5)  # x 값 업데이트
        #         #     #         # 10개 보다 작으면 ROD_CONT는 제어하지 않음. 그리고 Man mode 면 계산 대기함.
        #         #     #         fin_input = self.ROD_CONT.predict_action(self.temp_mem, self.temp_trig_mem)
        #         #     #         # fin_input 데이터 저장
        #         #     #         # 'Rod_His': {'X': [], 'Y_avg': [], 'Y_up_dead': [], 'Y_down_dead': [],
        #         #     #         #             'Y_up_op': [], 'Y_down_op': [], 'Y_ax': []},
        #         #     #         self.temp_trig_mem['Rod_His']['Y_pow'].append([fin_input[0]*100])
        #         #     #         self.temp_trig_mem['Rod_His']['Y_avg'].append([fin_input[8]*1000])
        #         #     #         self.temp_trig_mem['Rod_His']['Y_up_dead'].append([fin_input[1]*1000])
        #         #     #         self.temp_trig_mem['Rod_His']['Y_down_dead'].append([fin_input[2]*1000])
        #         #     #         self.temp_trig_mem['Rod_His']['Y_up_op'].append([fin_input[5]*1000])
        #         #     #         self.temp_trig_mem['Rod_His']['Y_down_op'].append([fin_input[6]*1000])
        #         #     #         self.temp_trig_mem['Rod_His']['Y_ax'].append([self.temp_mem['CAXOFF']['V']])
        #         #     #     print('<-ROD_CONT 모듈', end='#')
        #         #     #
        #         #     # 3. ROD_CONT의 제어 ============================================================ VER2
        #         #     # if self.temp_trig_mem['ST_OPStratey'] == PARA.ST_OP:
        #         #     #     print('ROD_CONT 모듈->', end=' ')
        #         #     #     self.temp_trig_mem['TEMP_CONT'] += 1
        #         #     #     print('<-ROD_CONT 모듈', end='#')
        #         #
        #         #     # # 4. PZR_CONT의 제어 ============================================================
        #         #     # elif self.temp_trig_mem['ST_OPStratey'] == PARA.PZR_OP:
        #         #     #     print('PZR_CONT 모듈->', end=' ')
        #         #     #     if len(self.temp_mem['KCNTOMS']['D']) >= 1:
        #         #     #         pass
        #         #     #         self.temp_trig_mem['PZR_His']['X'].append(self.temp_mem['KCNTOMS']['V']*self.temp_trig_mem['Speed']/5)  # x 값 업데이트
        #         #     #         # # 10개 보다 작으면 PZR_CONT는 제어하지 않음. 그리고 Man mode 면 계산 대기함.
        #         #     #         fin_input = self.PZR_CONT.predict_action(self.temp_mem, self.temp_trig_mem)
        #         #     #         # fin_input 데이터 저장
        #         #     #         self.temp_trig_mem['PZR_His']['Y_pre'].append([self.temp_mem['ZINST58']['V'], 30, 20])
        #         #     #         self.temp_trig_mem['PZR_His']['Y_lv'].append([self.temp_mem['ZINST63']['V']])
        #         #     #         self.temp_trig_mem['PZR_His']['Y_temp'].append([self.temp_mem['UPRZ']['V']])
        #         #     #         self.temp_trig_mem['PZR_His']['Y_val'].append([fin_input[4], fin_input[6]])
        #         #     #         self.temp_trig_mem['PZR_His']['Y_het'].append([self.temp_mem['KLAMPO118']['V'],
        #         #     #                                                      self.temp_mem['QPRZH']['V']])
        #         #     #     print('<-PZR_CONT 모듈', end='#')
        #         #     # else:
        #         #     #     print("=선택되지않은 OP", end='##')
        #         #
        #         #     # 3. 최종 MEM 업데이트 =================================================================================
        #         #     print('Stop!', end='\t')
        #         #     self.temp_trig_mem['Run'] = False
        #         #
        #         #     for key_val in self.temp_trig_mem.keys():
        #         #         self.trig_mem[key_val] = self.temp_trig_mem[key_val]
        #         #
        #         #     time.sleep(0.5)
        #
        #         print(self.mem['KCNTOMS'], self.trig_mem['Loop'], self.trig_mem['Run'])
        #         time.sleep(1)
        #         # End =================================================================================================
