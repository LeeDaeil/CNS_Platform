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
from AI.AI_EM_SAC import AIEMSAC
import time


class All_Function_module(multiprocessing.Process):
    def __init__(self, shmem):
        multiprocessing.Process.__init__(self)
        self.daemon = True
        self.shmem = shmem

        # 1 CNS 환경 생성 ----------------------------------------------------
        # CNS 정보 읽기
        self.cns_ip, self.cns_port = self.shmem.get_cns_info()
        self.cns_env = ENVCNS(Name='EnvCNS', IP=self.cns_ip, PORT=int(self.cns_port))

        # 2 AI network Load -------------------------------------------------
        # self.AI_AGENT = MainNet()
        # self.ROD_CONT = ROD_CONT(network=None)   # 정상에서 Rod control module
        # self.PZR_CONT = PZR_CONT(network=self.AI_AGENT.PZR_actor)   # 가압기 기포생성 모듈
        # self.SAMP_CONT = SAMP_CONT()

        # 2 AI Network
        self.AIEM = None
        self.AIRC = None

    def pr_(self, s):
        head_ = 'AllFuncM'
        return print(f'[{head_:10}][{s}]')

    def _update_cnsenv_to_sharedmem(self):
        # st = time.time()
        self.shmem.change_shmem_db(self.cns_env.mem)
        # print(time.time()-st)

    def check_init(self):
        if self.shmem.get_logic('Init_Call'):
            self.pr_('Initial Start...')
            self.cns_env.reset(file_name='cns_log', initial_nub=self.shmem.get_logic('Init_nub'))
            self._update_cnsenv_to_sharedmem()
            self.shmem.change_logic_val('Init_Call', False)
            self.shmem.change_logic_val('UpdateUI', True)
            self.pr_('Initial End!')

    def check_mal(self):
        sw, info_mal = self.shmem.get_shmem_malinfo()
        if sw:
            self.pr_('Mal Start...')
            self.shmem.change_logic_val('Mal_Call', False)
            for _ in info_mal:
                if not info_mal[_]['Mal_done']:     # mal history 중 입력이 안된 것을 찾아서 수행.
                    self.cns_env._send_malfunction_signal(info_mal[_]['Mal_nub'],
                                                          info_mal[_]['Mal_opt'],
                                                          info_mal[_]['Mal_time']
                                                          )
                    self.shmem.change_mal_list(_)
            self.pr_('Mal End!')

    def check_speed(self):
        if self.shmem.get_logic('Speed_Call'):
            self.cns_env.want_tick = self.shmem.get_logic('Speed')
            self.shmem.change_logic_val('Speed_Call', False)

    def run(self):
        # ==============================================================================================================
        # - 공유 메모리에서 logic 부분을 취득 후 사용되는 AI 네트워크 정보 취득
        local_logic = self.shmem.get_logic_info()
        if local_logic['Run_ec']:
            self.AIEM = AIEMSAC(input_shape=len(self.cns_env.input_info_EM),
                                output_shape=4, discrete_mode=False)
            self.AIEM.agent_load_model('./AI/AI_EM_SAC_Actor')

        if local_logic['Run_sv'] or local_logic['Run_abd']:
            from CNS_AIl_AI_module import Mainnet
            main_net__ = Mainnet()

            if local_logic['Run_sv']:
                from AI.AI_SV_Module import Signal_Validation
                SV_net = Signal_Validation(network=main_net__.EM_SV_net)
            if local_logic['Run_abd']:
                from AI.AI_AB_Module import Abnormal_dig_module
                AB_d_net = Abnormal_dig_module(network=main_net__.AB_DIG_Net)

        if local_logic['Run_rc']:
            pass

        while True:
            local_logic = self.shmem.get_logic_info()
            if local_logic['Run']:
                # Rod Control Part -------------------------------------------------------------------------------------
                if local_logic['Run_rc']:
                    """
                    TRICK -----------------------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    """
                    # One Step CNS -------------------------------------------------------------------------------------
                    self.cns_env.dumy_step()
                    if self.cns_env.ENVStep == 1607:
                        # Done
                        self.shmem.change_logic_val('Run', False)

                    # Update All mem -----------------------------------------------------------------------------------
                    self._update_cnsenv_to_sharedmem()
                    self.shmem.change_logic_val('UpdateUI', True)
                else:
                    # Make action from AI ------------------------------------------------------------------------------
                    # - 동작이 허가된 AI 모듈이 cns_env 에서 상태를 취득하여 액션을 계산함.
                    # TODO 향후 cns_env에서 노멀라이제이션까지 모두 처리 할 것.
                    # 1] 비상 냉각 및 감압 자율 운전 모듈
                    if local_logic['Run_ec']:
                        next_s, next_s_list = self.cns_env.get_state(self.cns_env.input_info_EM)
                        EM_action = self.AIEM.agent_select_action(next_s, evaluate=True)
                    else:
                        EM_action = None

                    # Rod Control Part ---------------------------------------------------------------------------------
                    if local_logic['Run_rc']:
                        pass

                    # State Monitoring Part ----------------------------------------------------------------------------
                    self._monitoring_state()

                    # Abnormal Net
                    if local_logic['Run_abd']:
                        result = AB_d_net.predict_action(self.cns_env.mem)
                        self.shmem.change_logic_val('AB_DIG', result)
                        for check_prob in result[1:]:   # 정상인 0 번째를 제외하고 순회
                            if check_prob > 0.9:
                                self.shmem.change_logic_val('Find_AB_DIG', True)

                    # Signal validation Part ---------------------------------------------------------------------------
                    if local_logic['Run_sv']:
                        result = SV_net.predict_action(self.cns_env.mem)
                        if self.cns_env.CMem.CTIME <= 515:
                            self.shmem.change_logic_val('SV_RES', result)

                    # One Step CNS -------------------------------------------------------------------------------------
                    Action_dict = {
                        'EM': EM_action
                    }
                    self.cns_env.step(Action_dict)

                    # Update All mem -----------------------------------------------------------------------------------
                    self._update_cnsenv_to_sharedmem()
                    self.shmem.change_logic_val('UpdateUI', True)
                    if local_logic['Run_ec'] and self.cns_env.mem['KCNTOMS']['Val'] > 50000:
                        """
                        50000 tick: 12, 10005, 30 malfunction 인 경우 50000 tick에서 멈춰야함.
                        """
                        self.shmem.change_logic_val('Run', False)
                    # --------------------------------------------------------------------------------------------------
                    # self.shmem.change_logic_val('Auto_re_man', True)
                    # self.shmem.change_logic_val('Auto_re_man', False)
            else:
                self.check_init()
                self.check_mal()
                self.check_speed()

    def _monitoring_state(self):
        # 1. 정상 or 비상 판별
        if self.cns_env.mem['KLAMPO9']['Val'] == 1:
            self.shmem.change_logic_val('Operation_Strategy', 'E')
        else:
            if self.shmem.get_logic('Find_AB_DIG'):
                self.shmem.change_logic_val('Operation_Strategy', 'A')
            else:
                self.shmem.change_logic_val('Operation_Strategy', 'N')

    def _rod_control(self):
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
