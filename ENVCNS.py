import numpy as np
from time import sleep
from TOOL.TOOL_CNS_UDP_FAST import CNS
from TOOL.TOOL_Cool import CoolingRATE
from TOOL import TOOL_etc, TOOL_PTCurve, TOOL_CSF

import pandas as pd

class CMem:
    def __init__(self, mem):
        self.m = mem  # Line CNSmem -> getmem
        self.CoolingRateSW = 0
        self.CoolingRateFixTemp = 0
        self.CoolingRateFixTime = 0

        self.CoolingRATE = CoolingRATE()

        self.StartRL = 0

        self.update()

    def update(self):
        self.CTIME = self.m['KCNTOMS']['Val']       # CNS Time

        # Physical
        self.SG1Nar = self.m['ZINST78']['Val']
        self.SG2Nar = self.m['ZINST77']['Val']
        self.SG3Nar = self.m['ZINST76']['Val']

        self.SG1Wid = self.m['ZINST72']['Val']
        self.SG2Wid = self.m['ZINST71']['Val']
        self.SG3Wid = self.m['ZINST70']['Val']

        self.SG1Pres = self.m['ZINST75']['Val']
        self.SG2Pres = self.m['ZINST74']['Val']
        self.SG3Pres = self.m['ZINST73']['Val']

        self.SG1Feed = self.m['WFWLN1']['Val']
        self.SG2Feed = self.m['WFWLN2']['Val']
        self.SG3Feed = self.m['WFWLN3']['Val']

        self.SG1FeedValveM = self.m['KLAMPO147']['Val']
        self.SG2FeedValveM = self.m['KLAMPO148']['Val']
        self.SG3FeedValveM = self.m['KLAMPO149']['Val']

        self.Aux1Flow = self.m['WAFWS1']['Val']
        self.Aux2Flow = self.m['WAFWS2']['Val']
        self.Aux3Flow = self.m['WAFWS3']['Val']

        self.SteamLine1 = self.m['BHV108']['Val']
        self.SteamLine2 = self.m['BHV208']['Val']
        self.SteamLine3 = self.m['BHV308']['Val']

        self.AVGTemp = self.m['UAVLEG2']['Val']
        self.PZRPres = self.m['ZINST65']['Val']         # display
        self.PZRPresRaw = self.m['PPRZ']['Val']         # raw
        self.PZRLevel = self.m['ZINST63']['Val']        # display
        self.PZRLevelRaw = self.m['ZPRZNO']['Val']      # raw

        # Signal
        self.Tavgref = self.m['ZINST15']['Val']
        self.Trip = self.m['KLAMPO9']['Val']
        self.SIS = self.m['KLAMPO6']['Val']
        self.MSI = self.m['KLAMPO3']['Val']
        self.NetBRK = self.m['KLAMPO224']['Val']

        # Comp
        self.RCP1 = self.m['KLAMPO124']['Val']
        self.RCP2 = self.m['KLAMPO125']['Val']
        self.RCP3 = self.m['KLAMPO126']['Val']

        self.TurningGear = self.m['KLAMPO165']['Val']
        self.OilSys = self.m['KLAMPO164']['Val']
        self.BHV311 = self.m['BHV311']['Val']

        self.SteamDumpPos = self.m['ZINST98']['Val']
        self.SteamDumpManAuto = self.m['KLAMPO150']['Val']

        self.PMSS = self.m['PMSS']['Val']

        # 강화학습을 위한 감시 변수
        self.PZRSprayManAuto = self.m['KLAMPO119']['Val']
        self.PZRSprayPos = self.m['ZINST66']['Val']
        self.PZRSprayPosControl = self.m['BPRZSP']['Val']

        self.PZRBackHeaterOnOff = self.m['KLAMPO118']['Val']
        self.PZRProHeaterManAuto = self.m['KLAMPO117']['Val']
        self.PZRProHeaterPos = self.m['QPRZH']['Val']

        self.SIValve = self.m['BHV22']['Val']

        self.ChargingManAUto = self.m['KLAMPO95']['Val']
        self.ChargingValvePos = self.m['BFV122']['Val']
        self.ChargingPump2State = self.m['KLAMPO70']['Val']

        self.LetdownLV459Pos = self.m['BLV459']['Val']
        self.LetdownHV1Pos = self.m['BHV1']['Val']
        self.LetdownHV2Pos = self.m['BHV2']['Val']
        self.LetdownHV3Pos = self.m['BHV3']['Val']

        # Logic
        if self.CTIME == 0:
            self.CoolingRateSW = 0
            self.CoolingRATE.reset_info()

            self.StartRL = 0

        if self.CoolingRateSW == 1:         # 2.0] Cooling rage 계산 시작
            self.CoolingRATE.save_info(self.AVGTemp, self.CTIME)
            self.CoolingRateSW += 1     # 값 2로 바뀜으로써 이 로직은 1번만 동작함.
        # --------------------------------------------------------------------------------------------------------------
        # 현재 발생 비정상 확인
        self.abnub = {
            'AB2101': True if self.m['cMALC']['Val'] == 19 and self.m['cMALO']['Val'] > 155 else False,
            'AB2102': True if self.m['cMALC']['Val'] == 19 and self.m['cMALO']['Val'] < 155 else False,
            'AB2001': True if self.m['cMALC']['Val'] == 20 and self.m['cMALO']['Val'] > 95 else False,
            'AB2004': True if self.m['cMALC']['Val'] == 20 and self.m['cMALO']['Val'] < 15 else False,
            'AB1507': True if self.m['cMALC']['Val'] == 30 and (1000 < self.m['cMALO']['Val'] < 1050 or
                                                                2000 < self.m['cMALO']['Val'] < 2050 or
                                                                3000 < self.m['cMALO']['Val'] < 3050) else False,
            'AB1508': True if self.m['cMALC']['Val'] == 30 and (1050 < self.m['cMALO']['Val'] < 1100 or
                                                                2050 < self.m['cMALO']['Val'] < 2100 or
                                                                3050 < self.m['cMALO']['Val'] < 3100) else False,
            'AB6304': True if self.m['cMALC']['Val'] == 2 else False,
            'AB2112': True if self.m['cMALC']['Val'] == 15 else False,
        }
        self.curab = ''
        for key in self.abnub.keys():
            if self.abnub[key]:
                self.curab = key

        # ab_normal operator
        if self.CTIME == 0:
            self.ab2101 = {'S1': True, 'S2': False, 'S3': False, 'S4': False, 'S5': False}
            self.ab2102 = {'S1': True, 'S2': False, 'S3': False}
            self.ab2001 = {'S1': True, 'S2': False}
            self.ab2004 = {'S1': True, 'S2': False}
            self.ab1507 = {'S1': True, 'S2': False, 'S3': False, 'S4': False}
            self.ab1508 = {'S1': True, 'S2': False, 'S3': False, 'S4': False}
            self.ab6304 = {'S1': True, 'S2': False}
            self.ab2112 = {'S1': True, 'S2': False, 'S3': False, 'S3Try': 0, 'S4': False, 'S4Try': 0, 'S5': False}
        else:
            if self.abnub['AB2101']:
                # 알람 인지
                if self.ab2101['S1'] and self.m['KLAMPO308']['Val'] == 1:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab2101['S1'], self.ab2101['S2'] = False, True
                elif self.ab2101['S2']:
                    if self.PZRProHeaterPos == 1:
                        self.ab2101['S2'], self.ab2101['S3'] = False, True
                elif self.ab2101['S3']:
                    if self.PZRPresRaw > 154 * 1e5:
                        self.ab2101['S3'], self.ab2101['S4'] = False, True
                elif self.ab2101['S4']:
                    if self.PZRProHeaterPos == 0:
                        self.ab2101['S4'], self.ab2101['S5'] = False, True
            if self.abnub['AB2102']:
                # 알람 인지
                if self.ab2102['S1'] and self.m['KLAMPO307']['Val'] == 1:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab2102['S1'], self.ab2102['S2'] = False, True
                elif self.ab2102['S2']:
                    if self.PZRProHeaterPos == 0:
                        self.ab2102['S2'], self.ab2102['S3'] = False, True
            if self.abnub['AB2001']:
                if self.ab2001['S1'] and self.m['KLAMPO266']['Val'] == 1:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab2001['S1'], self.ab2001['S2'] = False, True
            if self.abnub['AB2004']:
                if self.ab2004['S1'] and self.m['KLAMPO274']['Val'] == 1:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab2004['S1'], self.ab2004['S2'] = False, True
            if self.abnub['AB1507']:
                if self.ab1507['S1'] and self.m['KLAMPO320']['Val'] == 1:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab1507['S1'], self.ab1507['S2'] = False, True
                        if 1000 < self.m['cMALO']['Val'] < 1050:
                            self.abSG = 1
                        elif 2000 < self.m['cMALO']['Val'] < 2050:
                            self.abSG = 2
                        elif 3000 < self.m['cMALO']['Val'] < 3050:
                            self.abSG = 3
                        else:
                            self.abSG = 4 # error
                            print('Error AB 1507 SG')
                if self.ab1507['S2']:
                    if self.abSG == 1 and self.SG1FeedValveM == 1:
                        self.ab1507['S2'], self.ab1507['S3'] = False, True
                    if self.abSG == 2 and self.SG2FeedValveM == 1:
                        self.ab1507['S2'], self.ab1507['S3'] = False, True
                    if self.abSG == 3 and self.SG3FeedValveM == 1:
                        self.ab1507['S2'], self.ab1507['S3'] = False, True
                if self.ab1507['S3']:
                    targetBypass = self.m[{1: 'BFV479', 2: 'BFV489', 3: 'BFV499'}[self.abSG]]['Val']
                    if targetBypass < 0.44:
                        self.ab1507['S3'], self.ab1507['S4'] = False, True
            if self.abnub['AB1508']:
                if self.ab1508['S1'] and self.m['KLAMPO320']['Val'] == 1:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab1508['S1'], self.ab1508['S2'] = False, True
                        if 1050 < self.m['cMALO']['Val'] < 1100:
                            self.abSG = 1
                        elif 2050 < self.m['cMALO']['Val'] < 2100:
                            self.abSG = 2
                        elif 3050 < self.m['cMALO']['Val'] < 3100:
                            self.abSG = 3
                        else:
                            self.abSG = 4  # error
                            print('Error AB 1507 SG')
                if self.ab1508['S2']:
                    if self.abSG == 1 and self.SG1FeedValveM == 1:
                        self.ab1508['S2'], self.ab1508['S3'] = False, True
                    if self.abSG == 2 and self.SG2FeedValveM == 1:
                        self.ab1508['S2'], self.ab1508['S3'] = False, True
                    if self.abSG == 3 and self.SG3FeedValveM == 1:
                        self.ab1508['S2'], self.ab1508['S3'] = False, True
                if self.ab1508['S3']:
                    targetBypass = self.m[{1: 'BFV479', 2: 'BFV489', 3: 'BFV499'}[self.abSG]]['Val']
                    if targetBypass > 0.44:
                        self.ab1508['S3'], self.ab1508['S4'] = False, True
            if self.abnub['AB6304']:
                if self.ab6304['S1'] and (self.m['KLAMPO313']['Val'] == 1 or self.m['QPROREL']['Val'] < 0.99):
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab6304['S1'], self.ab6304['S2'] = False, True
            if self.abnub['AB2112']:
                if self.ab2112['S1'] and self.m['BPORV']['Val'] != 0:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab2112['S1'], self.ab2112['S2'] = False, True
                if self.ab2112['S2'] and self.m['KLAMPO110']['Val'] == 1:   # 메뉴얼 인지
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self.ab2112['S2'], self.ab2112['S3'] = False, True
                if self.ab2112['S3Try'] > 5:
                    self.ab2112['S3'], self.ab2112['S4'] = False, True
                if self.ab2112['S4Try'] > 5:
                    self.ab2112['S4'], self.ab2112['S5'] = False, True

class ENVCNS(CNS):
    def __init__(self, Name, IP, PORT):
        super(ENVCNS, self).__init__(threrad_name=Name,
                                     CNS_IP=IP, CNS_Port=PORT,
                                     Remote_IP='192.168.0.29', Remote_Port=PORT, Max_len=10)
        self.Name = Name  # = id
        self.ENVStep = 0
        self.LoggerPath = 'DB'
        self.want_tick = 5  # 1sec

        self.Loger_txt = ''

        self.CMem = CMem(self.mem)

        self.input_info_EM = [
            # (para, x_round, x_min, x_max), (x_min=0, x_max=0 is not normalized.)
            ('ZINST98', 1, 0, 100),  # SteamDumpPos
            ('ZINST87', 1, 0, 50),  # Steam Flow 1
            ('ZINST86', 1, 0, 50),  # Steam Flow 2
            ('ZINST85', 1, 0, 50),  # Steam Flow 3
            ('KLAMPO70', 1, 0, 1),  # Charging Pump2 State
            ('BHV22', 1, 0, 1),  # SI Valve State
            ('ZINST66', 1, 0, 25),  # PZRSprayPos
            ('UAVLEG2', 1, 150, 320),  # PTTemp
            ('ZINST65', 1, 0, 160),  # PTPressure
            ('ZINST78', 1, 0, 70),  # SG1Nar
            ('ZINST77', 1, 0, 70),  # SG2Nar
            ('ZINST76', 1, 0, 70),  # SG3Nar
            ('ZINST75', 1, 0, 80),  # SG1Pres
            ('ZINST74', 1, 0, 80),  # SG2Pres
            ('ZINST73', 1, 0, 80),  # SG3Pres
            ('ZINST72', 1, 0, 100),  # SG1Wid
            ('ZINST71', 1, 0, 100),  # SG2Wid
            ('ZINST70', 1, 0, 100),  # SG3Wid
            ('UUPPPL', 1, 100, 350),  # CoreExitTemp
            ('WFWLN1', 1, 0, 25),  # SG1Feed
            ('WFWLN2', 1, 0, 25),  # SG2Feed
            ('WFWLN3', 1, 0, 25),  # SG3Feed
            ('UCOLEG1', 1, 0, 100),  # RCSColdLoop1
            ('UCOLEG2', 1, 0, 100),  # RCSColdLoop2
            ('UCOLEG3', 1, 0, 100),  # RCSColdLoop3
            ('ZINST65', 1, 0, 160),  # RCSPressure
            ('ZINST63', 1, 0, 100),  # PZRLevel
        ]

        # --------------------------------------------------------------------------------------------------------------
        self.dumy_db = pd.read_csv('DUMY_ALL_ROD2.csv')
        self.Nob_db = pd.read_csv('AI/AI_NoB_His.csv')

    def normalize(self, x, x_round, x_min, x_max):
        if x_max == 0 and x_min == 0:
            # It means X value is not normalized.
            x = x / x_round
        else:
            x = x_max if x >= x_max else x
            x = x_min if x <= x_min else x
            x = (x - x_min) / (x_max - x_min)
        return x

    def get_state(self, input_info):
        state = []
        for para, x_round, x_min, x_max in input_info:
            if para in self.mem.keys():
                _ = self.mem[para]['Val']
            else:
                if para == 'DSetPoint':
                    _ = 0
                else:
                    _ = None
                # ------------------------------------------------------------------------------------------------------
                if _ is None:
                    raise ValueError(f'{para} is not in self.input_info')
                # ------------------------------------------------------------------------------------------------------
            state.append(self.normalize(_, x_round, x_min, x_max))
        return np.array(state), state

    def _send_control_save(self, zipParaVal):
        super(ENVCNS, self)._send_control_save(para=zipParaVal[0], val=zipParaVal[1])

    def _send_act_EM_Module(self, A):
        def a_log_f(s=''):
            pass

        ActOrderBook = {
            'StopAllRCP': (['KSWO132', 'KSWO133', 'KSWO134'], [0, 0, 0]),
            'StopRCP1': (['KSWO132'], [0]),
            'StopRCP2': (['KSWO133'], [0]),
            'StopRCP3': (['KSWO134'], [0]),
            'NetBRKOpen': (['KSWO244'], [0]),
            'OilSysOff': (['KSWO190'], [0]),
            'TurningGearOff': (['KSWO191'], [0]),
            'CutBHV311': (['BHV311', 'FKAFWPI'], [0, 0]),

            'PZRSprayMan': (['KSWO128'], [1]), 'PZRSprayAuto': (['KSWO128'], [0]),

            'PZRSprayClose': (['BPRZSP'], [self.mem['BPRZSP']['Val'] + 0.015 * -1]),
            'PZRSprayOpen': (['BPRZSP'], [self.mem['BPRZSP']['Val'] + 0.015 * 1]),

            'PZRBackHeaterOff': (['KSWO125'], [0]), 'PZRBackHeaterOn': (['KSWO125'], [1]),

            'SteamDumpMan': (['KSWO176'], [1]), 'SteamDumpAuto': (['KSWO176'], [0]),

            'IFLOGIC_SteamDumpUp': (['PMSS'], [self.CMem.PMSS + 2.0E5 * 3 * 0.2]),
            'IFLOGIC_SteamDumpDown': (['PMSS'], [self.CMem.PMSS + 2.0E5 * (-3) * 0.2]),

            'DecreaseAux1Flow': (['KSWO142', 'KSWO143'], [1, 0]),
            'IncreaseAux1Flow': (['KSWO142', 'KSWO143'], [0, 1]),
            'DecreaseAux2Flow': (['KSWO151', 'KSWO152'], [1, 0]),
            'IncreaseAux2Flow': (['KSWO151', 'KSWO152'], [0, 1]),
            'DecreaseAux3Flow': (['KSWO154', 'KSWO155'], [1, 0]),
            'IncreaseAux3Flow': (['KSWO154', 'KSWO155'], [0, 1]),

            'SteamLine1Open': (['KSWO148', 'KSWO149'], [1, 0]),
            'SteamLine2Open': (['KSWO146', 'KSWO147'], [1, 0]),
            'SteamLine3Open': (['KSWO144', 'KSWO145'], [1, 0]),

            'ResetSI': (['KSWO7', 'KSWO5'], [1, 1]),

            'PZRProHeaterMan': (['KSWO120'], [1]), 'PZRProHeaterAuto': (['KSWO120'], [0]),
            'PZRProHeaterDown': (['KSWO121', 'KSWO122'], [1, 0]),
            'PZRProHeaterUp': (['KSWO121', 'KSWO122'], [0, 1]),

            'RL_IncreaseAux1Flow': (['WAFWS1'], [self.mem['WAFWS1']['Val'] + 0.04 * 1]),
            'RL_DecreaseAux1Flow': (['WAFWS1'], [self.mem['WAFWS1']['Val'] + 0.04 * (-1)]),
            'RL_IncreaseAux2Flow': (['WAFWS2'], [self.mem['WAFWS2']['Val'] + 0.04 * 1]),
            'RL_DecreaseAux2Flow': (['WAFWS2'], [self.mem['WAFWS2']['Val'] + 0.04 * (-1)]),
            'RL_IncreaseAux3Flow': (['WAFWS3'], [self.mem['WAFWS3']['Val'] + 0.04 * 1]),
            'RL_DecreaseAux3Flow': (['WAFWS3'], [self.mem['WAFWS3']['Val'] + 0.04 * (-1)]),

            'ChargingValveMan': (['KSWO100'], [1]), 'ChargingValveAUto': (['KSWO100'], [0]),
            'ChargingValveDown': (['KSWO101', 'KSWO102'], [1, 0]),
            'ChargingValveUp': (['KSWO101', 'KSWO102'], [0, 1]),

            'LetdownLV459Open': (['KSWO114', 'KSWO113'], [1, 0]),
            'LetdownLV459Close': (['KSWO114', 'KSWO113'], [0, 1]),

            'LetdownHV1Open': (['KSWO104', 'KSWO103'], [1, 0]),
            'LetdownHV1Close': (['KSWO104', 'KSWO103'], [0, 1]),
            'LetdownHV2Open': (['KSWO106', 'KSWO105'], [1, 0]),
            'LetdownHV2Close': (['KSWO106', 'KSWO105'], [0, 1]),
            'LetdownHV3Open': (['KSWO108', 'KSWO107'], [1, 0]),
            'LetdownHV3Close': (['KSWO108', 'KSWO107'], [0, 1]),

            'RunRCP2': (['KSWO130', 'KSWO133'], [1, 1]),
            'RunCHP2': (['KSWO70'], [1]), 'StopCHP2': (['KSWO70'], [0]),
            'OpenSI': (['KSWO81', 'KSWO82'], [1, 0]), 'CloseSI': (['KSWO81', 'KSWO82'], [0, 1]),
        }

        AMod = A
        print('[EM_Module]', self.CMem.CTIME)
        if self.CMem.Trip == 1:
            # 1.1] 원자로 Trip 이후 자동 제어 액션
            # 1.1.1] RCP 97 압력 이하에서 자동 정지
            if self.CMem.RCP1 == 1 and self.CMem.PZRPres < 97 and self.CMem.CTIME < 15 * 60 * 5:
                a_log_f(s=f'Pres [{self.CMem.PZRPres}] < 97 RCP 1 stop')
                self._send_control_save(ActOrderBook['StopRCP1'])
            if self.CMem.RCP2 == 1 and self.CMem.PZRPres < 97 and self.CMem.CTIME < 15 * 60 * 5:
                a_log_f(s=f'Pres [{self.CMem.PZRPres}] < 97 RCP 2 stop')
                self._send_control_save(ActOrderBook['StopRCP2'])
            if self.CMem.RCP3 == 1 and self.CMem.PZRPres < 97 and self.CMem.CTIME < 15 * 60 * 5:
                a_log_f(s=f'Pres [{self.CMem.PZRPres}] < 97 RCP 3 stop')
                self._send_control_save(ActOrderBook['StopRCP3'])
            # 1.1.2] 원자로 트립 후 Netbrk, turning gear, oil sys, BHV311 정지 및 패쇄
            if self.CMem.NetBRK == 1:
                a_log_f(s=f'NetBRK [{self.CMem.NetBRK}] Off')
                self._send_control_save(ActOrderBook['NetBRKOpen'])
            if self.CMem.TurningGear == 1:
                a_log_f(s=f'TurningGear [{self.CMem.TurningGear}] Off')
                self._send_control_save(ActOrderBook['TurningGearOff'])
            if self.CMem.OilSys == 1:
                a_log_f(s=f'OilSys [{self.CMem.OilSys}] Off')
                self._send_control_save(ActOrderBook['OilSysOff'])
            if self.CMem.BHV311 > 0:
                a_log_f(s=f'BHV311 [{self.CMem.BHV311}] Cut')
                self._send_control_save(ActOrderBook['CutBHV311'])
            # 1.2] 스팀 덤프벨브 현재 최대 압력을 기준으로 해당 부분까지 벨브 Set-up
            a_log_f(s=f'[Check][{self.CMem.SIS}][{self.CMem.MSI}][Check Main logic 1]')
            if self.CMem.SIS != 0 and self.CMem.MSI != 0:
                if max(self.CMem.SG1Pres, self.CMem.SG2Pres, self.CMem.SG3Pres) < self.CMem.SteamDumpPos:
                    a_log_f(s=f'StemDumpPos [{self.CMem.SteamDumpPos}] change')
                    self._send_control_save(ActOrderBook['IFLOGIC_SteamDumpDown'])
            # 1.2] SI reset 전에 Aux 평균화 [검증 완료 20200903]
                if self.CMem.SG1Feed == self.CMem.SG2Feed and self.CMem.SG1Feed == self.CMem.SG3Feed and \
                        self.CMem.SG2Feed == self.CMem.SG1Feed and self.CMem.SG2Feed == self.CMem.SG3Feed and \
                        self.CMem.SG3Feed == self.CMem.SG1Feed and self.CMem.SG3Feed == self.CMem.SG2Feed:
                    a_log_f(s=f'[{self.CMem.SG1Feed:10}, {self.CMem.SG2Feed:10}, {self.CMem.SG3Feed:10}] Feed water avg done')
                else:
                    # 1.2.1] 급수 일정화 수행
                    # 1.2.1.1] 가장 큰 급수 찾기
                    SGFeedList = [self.CMem.SG1Feed, self.CMem.SG2Feed, self.CMem.SG3Feed]
                    MaxSGFeed = SGFeedList.index(max(SGFeedList))  # 0, 1, 2
                    MinSGFeed = SGFeedList.index(min(SGFeedList))  # 0, 1, 2
                    self._send_control_save(ActOrderBook[f'DecreaseAux{MaxSGFeed + 1}Flow'])
                    self._send_control_save(ActOrderBook[f'IncreaseAux{MinSGFeed + 1}Flow'])
                    a_log_f(s=f'[{self.CMem.SG1Feed:10}, {self.CMem.SG2Feed:10}, {self.CMem.SG3Feed:10}] Feed water avg')
            # 1.3] 3000부터 SI reset
            if self.CMem.CTIME == 3000 + (18000 * 5):
                self._send_control_save(ActOrderBook['ResetSI'])
                a_log_f(s=f'ResetSI [{self.CMem.CTIME}]')
            # 2] SI reset 발생 시 냉각 운전 시작
            if self.CMem.SIS == 0 and self.CMem.MSI == 0 and self.CMem.CTIME > 5 * 60 * 5:
                # 2.0] Cooling rage 계산 시작
                if self.CMem.CoolingRateSW == 0:
                    self.CMem.CoolingRateSW = 1
                    a_log_f(s=f'CoolingRateSW')
                # 2.1] Press set-point 를 현재 최대 압력 기준까지 조절 ( not work )
                if self.CMem.SteamDumpManAuto == 0:
                    self._send_control_save(ActOrderBook['SteamDumpMan'])
                    a_log_f(s=f'SteamDumpMan [{self.CMem.SteamDumpManAuto}]')
                # 2.2] Steam Line Open
                if self.CMem.SteamLine1 == 0:
                    self._send_control_save(ActOrderBook['SteamLine1Open'])
                    a_log_f(s=f'SteamLine1 [{self.CMem.SteamLine1}] Open')
                if self.CMem.SteamLine2 == 0:
                    self._send_control_save(ActOrderBook['SteamLine2Open'])
                    a_log_f(s=f'SteamLine2 [{self.CMem.SteamLine2}] Open')
                if self.CMem.SteamLine3 == 0:
                    self._send_control_save(ActOrderBook['SteamLine3Open'])
                    a_log_f(s=f'SteamLine3 [{self.CMem.SteamLine3}] Open')
                # 2.3] Charging flow 최소화
                if self.CMem.ChargingManAUto == 0:
                    self._send_control_save(ActOrderBook['ChargingValveMan'])
                    a_log_f(s=f'ChargingMode [{self.CMem.ChargingManAUto}] Man')
                if self.CMem.ChargingValvePos != 0:
                    self._send_control_save(ActOrderBook['ChargingValveDown'])
                    a_log_f(s=f'ChargingPOS [{self.CMem.ChargingValvePos}] Close')
                # 2.3] PZR spray 수동 전환 [감압]
                if self.CMem.PZRSprayManAuto == 0:
                    self._send_control_save(ActOrderBook['PZRSprayMan'])
                    a_log_f(s=f'PZRSprayMan [{self.CMem.PZRSprayManAuto}] Man')
                # 2.4] RCP 2 동작
                if self.CMem.RCP2 == 0:
                    self._send_control_save(ActOrderBook['RunRCP2'])
                    a_log_f(s=f'RCP2 [{self.CMem.RCP2}] Start')
                # 2.5] PZR 감압을 위한 Heater 종료
                if self.CMem.PZRProHeaterManAuto == 0:
                    self._send_control_save(ActOrderBook['PZRProHeaterMan'])
                    a_log_f(s=f'PZR PRO heater [{self.CMem.PZRProHeaterManAuto}] Man')
                if self.CMem.PZRProHeaterPos >= 0:
                    self._send_control_save(ActOrderBook['PZRProHeaterDown'])
                    a_log_f(s=f'PZR PRO Pos [{self.CMem.PZRProHeaterPos}] Down')
                if self.CMem.PZRBackHeaterOnOff == 1:
                    self._send_control_save(ActOrderBook['PZRBackHeaterOff'])
                    a_log_f(s=f'PZRBackHeaterOff [{self.CMem.PZRBackHeaterOnOff}] Off')
                # 3.0] 강화학습 제어 시작
                if self.CMem.StartRL == 0:
                    self.CMem.StartRL = 1
                    a_log_f(s=f'StartRL [{self.CMem.StartRL}]')
                else:
                    # 3.1] 가압기 저수위에서 고수위로 복구시 인한 Letdown 차단 금지
                    if self.CMem.PZRLevel > 20:
                        pass
                        # if self.CMem.LetdownLV459Pos == 0:
                        #     self._send_control_save(ActOrderBook['LetdownLV459Open'])
                        # if self.CMem.LetdownHV1Pos == 0:
                        #     self._send_control_save(ActOrderBook['LetdownHV1Open'])
                        # if self.CMem.LetdownHV2Pos == 0:
                        #     self._send_control_save(ActOrderBook['LetdownHV2Open'])

                    # 3.1] Spray control
                    if True:
                        pos = self.CMem.PZRSprayPosControl + 0.015 * np.clip(AMod[0] * 2, -2, 2)
                        zip_spray_pos = (['BPRZSP'], [pos])
                        self._send_control_save(zip_spray_pos)
                        a_log_f(s=f'Change Spray Pos [{self.CMem.PZRSprayPosControl:10}|{pos:10}]')
                    # 3.2] Aux Feed
                    if True:
                        aux123 = 0
                        if AMod[1] < -0.3:
                            # Decrease
                            aux123 = -1
                        elif -0.3 <= AMod[1] < 0.3:
                            # Stay
                            aux123 = 0
                        elif 0.3 <= AMod[1]:
                            # Increase
                            aux123 = 1

                        if self.CMem.SG1Wid > 80:
                            aux123 = -1

                        pos1 = self.CMem.Aux1Flow + 0.04 * aux123
                        pos2 = self.CMem.Aux2Flow + 0.04 * aux123
                        pos3 = self.CMem.Aux3Flow + 0.04 * aux123
                        zip_aux_pos = (['WAFWS1', 'WAFWS2', 'WAFWS3'], [pos1, pos2, pos3])
                        self._send_control_save(zip_aux_pos)
                        a_log_f(s=f'AuxFlow'
                                  f'[{self.CMem.Aux1Flow:10}|{pos1:10}]'
                                  f'[{self.CMem.Aux2Flow:10}|{pos2:10}]'
                                  f'[{self.CMem.Aux3Flow:10}|{pos3:10}]')
                    # 3.3] SI Supply water
                    if True:
                        if AMod[2] < -0.8:
                            # self._send_control_save(ActOrderBook['CloseSI'])
                            a_log_f(s=f'CloseSI')
                        elif -0.8 <= AMod[2] < -0.6:
                            self._send_control_save(ActOrderBook['StopCHP2'])
                            a_log_f(s=f'StopCHP2')
                        elif -0.6 <= AMod[2] < 0.6:
                            #
                            pass
                        elif 0.6 <= AMod[2] < 0.8:
                            self._send_control_save(ActOrderBook['RunCHP2'])
                            a_log_f(s=f'RunCHP2')
                        elif 0.8 <= AMod[2]:
                            # self._send_control_save(ActOrderBook['OpenSI'])
                            a_log_f(s=f'OpenSI')

                        if self.CMem.CTIME > 30000 + (18000 * 5):     # TRICK
                            # SI logic <- 이를 통해서 압력 감압.
                            Updis, Botdis = TOOL_PTCurve.PTCureve()._check_distance(self.CMem.AVGTemp, self.CMem.PZRPres)
                            if Botdis > 12:
                                self._send_control_save(ActOrderBook['CloseSI'])
                            elif Botdis < 5:
                                self._send_control_save(ActOrderBook['OpenSI'])

                    # 3.4] Steam Dump
                    if True:
                        SteamDumpRate = 4
                        DumpPos = self.CMem.PMSS + 2.0E5 * np.clip(AMod[3] * SteamDumpRate,
                                                                   - SteamDumpRate, SteamDumpRate) * 0.2
                        zip_Dump_pos = (['PMSS'], [DumpPos])
                        self._send_control_save(zip_Dump_pos)
                        a_log_f(s=f'PMSS [{self.CMem.PMSS:10}|{DumpPos:10}]')

        return 0

    def _send_act_AB_DB_Module(self):
        ActOrderBook = {
            'StopAllRCP': (['KSWO132', 'KSWO133', 'KSWO134'], [0, 0, 0]),
            'StopRCP1': (['KSWO132'], [0]),
            'StopRCP2': (['KSWO133'], [0]),
            'StopRCP3': (['KSWO134'], [0]),
            'NetBRKOpen': (['KSWO244'], [0]),
            'OilSysOff': (['KSWO190'], [0]),
            'TurningGearOff': (['KSWO191'], [0]),
            'CutBHV311': (['BHV311', 'FKAFWPI'], [0, 0]),

            'PZRSprayMan': (['KSWO128'], [1]), 'PZRSprayAuto': (['KSWO128'], [0]),

            'PZRSprayClose': (['BPRZSP'], [self.mem['BPRZSP']['Val'] + 0.015 * -1]),
            'PZRSprayOpen': (['BPRZSP'], [self.mem['BPRZSP']['Val'] + 0.015 * 1]),

            'PZRBackHeaterOff': (['KSWO125'], [0]), 'PZRBackHeaterOn': (['KSWO125'], [1]),

            'SteamDumpMan': (['KSWO176'], [1]), 'SteamDumpAuto': (['KSWO176'], [0]),

            'IFLOGIC_SteamDumpUp': (['PMSS'], [self.CMem.PMSS + 2.0E5 * 3 * 0.2]),
            'IFLOGIC_SteamDumpDown': (['PMSS'], [self.CMem.PMSS + 2.0E5 * (-3) * 0.2]),

            'DecreaseAux1Flow': (['KSWO142', 'KSWO143'], [1, 0]),
            'IncreaseAux1Flow': (['KSWO142', 'KSWO143'], [0, 1]),
            'DecreaseAux2Flow': (['KSWO151', 'KSWO152'], [1, 0]),
            'IncreaseAux2Flow': (['KSWO151', 'KSWO152'], [0, 1]),
            'DecreaseAux3Flow': (['KSWO154', 'KSWO155'], [1, 0]),
            'IncreaseAux3Flow': (['KSWO154', 'KSWO155'], [0, 1]),

            'SteamLine1Open': (['KSWO148', 'KSWO149'], [1, 0]),
            'SteamLine2Open': (['KSWO146', 'KSWO147'], [1, 0]),
            'SteamLine3Open': (['KSWO144', 'KSWO145'], [1, 0]),

            'ResetSI': (['KSWO7', 'KSWO5'], [1, 1]),

            'PZRProHeaterMan': (['KSWO120'], [1]), 'PZRProHeaterAuto': (['KSWO120'], [0]),
            'PZRProHeaterDown': (['KSWO121', 'KSWO122'], [1, 0]),
            'PZRProHeaterUp': (['KSWO121', 'KSWO122'], [0, 1]),

            'RL_IncreaseAux1Flow': (['WAFWS1'], [self.mem['WAFWS1']['Val'] + 0.04 * 1]),
            'RL_DecreaseAux1Flow': (['WAFWS1'], [self.mem['WAFWS1']['Val'] + 0.04 * (-1)]),
            'RL_IncreaseAux2Flow': (['WAFWS2'], [self.mem['WAFWS2']['Val'] + 0.04 * 1]),
            'RL_DecreaseAux2Flow': (['WAFWS2'], [self.mem['WAFWS2']['Val'] + 0.04 * (-1)]),
            'RL_IncreaseAux3Flow': (['WAFWS3'], [self.mem['WAFWS3']['Val'] + 0.04 * 1]),
            'RL_DecreaseAux3Flow': (['WAFWS3'], [self.mem['WAFWS3']['Val'] + 0.04 * (-1)]),

            'ChargingValveMan': (['KSWO100'], [1]), 'ChargingValveAUto': (['KSWO100'], [0]),
            'ChargingValveDown': (['KSWO101', 'KSWO102'], [1, 0]),
            'ChargingValveUp': (['KSWO101', 'KSWO102'], [0, 1]),

            'LetdownLV459Open': (['KSWO114', 'KSWO113'], [1, 0]),
            'LetdownLV459Close': (['KSWO114', 'KSWO113'], [0, 1]),

            'LetdownHV1Open': (['KSWO104', 'KSWO103'], [1, 0]),
            'LetdownHV1Close': (['KSWO104', 'KSWO103'], [0, 1]),
            'LetdownHV2Open': (['KSWO106', 'KSWO105'], [1, 0]),
            'LetdownHV2Close': (['KSWO106', 'KSWO105'], [0, 1]),
            'LetdownHV3Open': (['KSWO108', 'KSWO107'], [1, 0]),
            'LetdownHV3Close': (['KSWO108', 'KSWO107'], [0, 1]),

            'RunRCP2': (['KSWO130', 'KSWO133'], [1, 1]),
            'RunCHP2': (['KSWO70'], [1]), 'StopCHP2': (['KSWO70'], [0]),
            'OpenSI': (['KSWO81', 'KSWO82'], [1, 0]), 'CloseSI': (['KSWO81', 'KSWO82'], [0, 1]),

            'Feed1Man': (['KSWO171', 'KSWO168'], [1, 1]),
            'Feed1ValveClose': (['KSWO172', 'KSWO173'], [1, 0]),
            'Feed1ValveStay': (['KSWO172', 'KSWO173'], [0, 0]),
            'Feed1ValveOpen': (['KSWO172', 'KSWO173'], [0, 1]),
            'Feed1BypassClose': (['KSWO169', 'KSWO170'], [1, 0]),
            'Feed1BypassStay': (['KSWO169', 'KSWO170'], [0, 0]),
            'Feed1BypassOpen': (['KSWO169', 'KSWO170'], [0, 1]),

            'Feed2Man': (['KSWO165', 'KSWO162'], [1, 1]),
            'Feed2ValveClose': (['KSWO166', 'KSWO167'], [1, 0]),
            'Feed2ValveStay': (['KSWO166', 'KSWO167'], [0, 0]),
            'Feed2ValveOpen': (['KSWO166', 'KSWO167'], [0, 1]),
            'Feed2BypassClose': (['KSWO163', 'KSWO164'], [1, 0]),
            'Feed2BypassStay': (['KSWO163', 'KSWO164'], [0, 0]),
            'Feed2BypassOpen': (['KSWO163', 'KSWO164'], [0, 1]),

            'Feed3Man': (['KSWO159', 'KSWO156'], [1, 1]),
            'Feed3ValveClose': (['KSWO160', 'KSWO161'], [1, 0]),
            'Feed3ValveStay': (['KSWO160', 'KSWO161'], [0, 0]),
            'Feed3ValveOpen': (['KSWO160', 'KSWO161'], [0, 1]),
            'Feed3BypassClose': (['KSWO157', 'KSWO158'], [1, 0]),
            'Feed3BypassStay': (['KSWO157', 'KSWO158'], [0, 0]),
            'Feed3BypassOpen': (['KSWO157', 'KSWO158'], [0, 1]),

            'LoadSetDown': (['KSWO225', 'KSWO224'], [0, 1]),
            'LoadSetUp': (['KSWO225', 'KSWO224'], [1, 0]),

            'PZRPORVMan': (['KSWO115'], [1]),
            'PZRPORVAuto': (['KSWO115'], [0]),
            'PZRPORVClose': (['KSWO119', 'KSWO118'], [1, 0]),
            'PZRPORVOpen': (['KSWO119', 'KSWO118'], [0, 1]),
            'HV6Open': (['KSWO124', 'KSWO123'], [0, 1]),
            'HV6Close': (['KSWO124', 'KSWO123'], [1, 0]),
        }
        if self.CMem.abnub['AB2101']:
            if self.CMem.ab2101['S2']:
                # 1. 알람 발생 인지 가압기 히터 On
                self._send_control_save(ActOrderBook['PZRProHeaterMan'])
                self._send_control_save(ActOrderBook['PZRBackHeaterOn'])
                self._send_control_save(ActOrderBook['PZRProHeaterUp'])
            if self.CMem.ab2101['S3']:
                # 2. 히터 모두 킴. 스프레이 잠그기
                self._send_control_save(ActOrderBook['PZRSprayMan'])
                self._send_control_save(ActOrderBook['PZRSprayClose'])
            if self.CMem.ab2101['S4']:
                # 3. 압력 처음으로 정상화 히터 잠그기
                self._send_control_save(ActOrderBook['PZRBackHeaterOff'])
                self._send_control_save(ActOrderBook['PZRProHeaterDown'])
            if self.CMem.ab2101['S5']:
                # 4. 목표 압력 내로 유지하도록 스프레이 조절
                if self.CMem.PZRPresRaw > 154.05 * 1e5 and int(np.random.choice(2, 1, p=[0.6, 0.4])[0]) == 1:
                    self._send_control_save(ActOrderBook['PZRSprayOpen'])
                if self.CMem.PZRPresRaw < 154.00 * 1e5 and int(np.random.choice(2, 1, p=[0.6, 0.4])[0]) == 1:
                    self._send_control_save(ActOrderBook['PZRSprayClose'])
        if self.CMem.abnub['AB2102']:
            if self.CMem.ab2102['S2']:
                # 1. 알람 발생 인지 가압기 히터 Off
                self._send_control_save(ActOrderBook['PZRProHeaterMan'])
                self._send_control_save(ActOrderBook['PZRBackHeaterOff'])
                self._send_control_save(ActOrderBook['PZRProHeaterDown'])
            if self.CMem.ab2102['S3']:
                # 2. 목표 압력 내로 유지하도록 스프레이 조절
                self._send_control_save(ActOrderBook['PZRSprayMan'])
                if self.CMem.PZRPresRaw > 154.05 * 1e5 and int(np.random.choice(2, 1, p=[0.6, 0.4])[0]) == 1:
                    self._send_control_save(ActOrderBook['PZRSprayOpen'])
                if self.CMem.PZRPresRaw < 154.00 * 1e5 and int(np.random.choice(2, 1, p=[0.6, 0.4])[0]) == 1:
                    self._send_control_save(ActOrderBook['PZRSprayClose'])
        if self.CMem.abnub['AB2001'] or self.CMem.abnub['AB2004']:
            if self.CMem.ab2001['S2'] or self.CMem.ab2004['S2']:
                # 1. 알람 발생 인지 Charging Man 및 조절
                self._send_control_save(ActOrderBook['ChargingValveMan'])
                if self.CMem.PZRLevelRaw < 0.54:
                    self._send_control_save(ActOrderBook['ChargingValveUp'])
                if self.CMem.PZRLevelRaw > 0.56:
                    self._send_control_save(ActOrderBook['ChargingValveDown'])
        if self.CMem.abnub['AB1507']:
            if self.CMem.ab1507['S2']:
                # 관련 밸브 Manual
                self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}Man'])
                for i in range(1, 4):
                    self._send_control_save(ActOrderBook[f'Feed{i}ValveStay'])
                    self._send_control_save(ActOrderBook[f'Feed{i}BypassStay'])
            if self.CMem.ab1507['S3'] or self.CMem.ab1507['S4']:
                # 선 Bypass 정상화 후 Main feed 조작
                targetBypass = self.CMem.m[{1: 'BFV479', 2: 'BFV489', 3: 'BFV499'}[self.CMem.abSG]]['Val']
                if targetBypass > 0.44:
                    self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}BypassClose'])
                else:
                    self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}BypassStay'])
                if self.CMem.ab1507['S4']:
                    # Main feed 조작
                    targetSGW = self.CMem.m[{1: 'ZINST72', 2: 'ZINST71', 3: 'ZINST70'}[self.CMem.abSG]]['Val']
                    if targetSGW > 89.5:
                        if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveClose'])
                        else:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveStay'])
                    elif targetSGW < 86.5:
                        if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveOpen'])
                        else:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveStay'])
                    else:
                        self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveStay'])
        if self.CMem.abnub['AB1508']:
            if self.CMem.ab1508['S2']:
                # 관련 밸브 Manual
                self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}Man'])
                for i in range(1, 4):
                    self._send_control_save(ActOrderBook[f'Feed{i}ValveStay'])
                    self._send_control_save(ActOrderBook[f'Feed{i}BypassStay'])
            if self.CMem.ab1508['S3'] or self.CMem.ab1508['S4']:
                # 선 Bypass 정상화 후 Main feed 조작
                targetBypass = self.CMem.m[{1: 'BFV479', 2: 'BFV489', 3: 'BFV499'}[self.CMem.abSG]]['Val']
                if targetBypass < 0.44:
                    self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}BypassOpen'])
                else:
                    self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}BypassStay'])
                if self.CMem.ab1508['S4']:
                    # Main feed 조작
                    targetSGW = self.CMem.m[{1: 'ZINST72', 2: 'ZINST71', 3: 'ZINST70'}[self.CMem.abSG]]['Val']
                    if targetSGW > 89.5:
                        if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveClose'])
                        else:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveStay'])
                    elif targetSGW < 86.5:
                        if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveOpen'])
                        else:
                            self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveStay'])
                    else:
                        self._send_control_save(ActOrderBook[f'Feed{self.CMem.abSG}ValveStay'])
        if self.CMem.abnub['AB6304']:
            if self.CMem.ab6304['S2']:
                # Tavg/ref +- 1 내로 터빈 출력 감소
                if self.CMem.Tavgref > 1:
                    if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                        self._send_control_save(ActOrderBook['LoadSetDown'])
        if self.CMem.abnub['AB2112']:
            if self.CMem.ab2112['S2']:
                # PZR PORV 개방 인지 후 매뉴얼 전환
                if int(np.random.choice(2, 1, p=[0.7, 0.3])[0]) == 1:
                    self._send_control_save(ActOrderBook['PZRPORVMan'])
            if self.CMem.ab2112['S3']:
                self.CMem.ab2112['S3Try'] += 1
                self._send_control_save(ActOrderBook['PZRPORVClose'])
            if self.CMem.ab2112['S4']:
                self.CMem.ab2112['S4Try'] += 1
                self._send_control_save(ActOrderBook['HV6Close'])

    def send_act(self, A):
        """
        A 에 해당하는 액션을 보내고 나머지는 자동
        E.x)
            self._send_control_save(['KSWO115'], [0])
            ...
            self._send_control_to_cns()
        :param A: A 액션 [0, 0, 0] <- act space에 따라서
        :return: AMod: 수정된 액션
        """
        AMod = A
        if isinstance(A, int):      # A=0 인경우
            pass
        elif isinstance(A, dict):   # A = { ... } 각 AI 모듈에 정보가 들어있는 경우
            if A['EM'] is not None:
                if self.CMem.CoolingRateSW == 0:
                    if self.CMem.CTIME % 100 == 0:
                        self._send_act_EM_Module(A['EM'])
                else:
                    if self.CMem.CTIME % 100 == 0:
                        self._send_act_EM_Module(A['EM'])
            if A['AB_DB'] is True:
                self._send_act_AB_DB_Module()

        else:
            print('Error')
        # Done Act
        self._send_control_to_cns()
        return AMod

    def step(self, A):
        """
        A를 받고 1 step 전진
        :param A: A -> dict
        :return: 최신 state와 reward done 반환
        """
        # Old Data (time t) ---------------------------------------
        AMod = self.send_act(A)

        # if self.CMem.CoolingRateSW == 0:
        #     if self.CMem.CTIME >= 800:
        #         # 강화학습 이전 시 5 tick
        #         self.want_tick = int(100)
        #     else:
        #         self.want_tick = int(100)
        # else:
        #     # Cooling 계산 시작 및 강화학습 진입 시 100 tick
        #     self.want_tick = int(100)
        print(self.CMem.curab, self.want_tick, self.CMem.CTIME, self.CMem.m['KLAMPO320']['Val'])

        # New Data (time t+1) -------------------------------------
        super(ENVCNS, self).step() # 전체 CNS mem run-Freeze 하고 mem 업데이트
        self.CMem.update()  # 선택 변수 mem 업데이트

        # 추가된 변수 고려
        self.mem['cCOOLRATE']['Val'] = self.CMem.CoolingRATE.get_temp(self.CMem.CTIME)

        self._append_val_to_list()
        self.ENVStep += 1

        # next_state, next_state_list = self.get_state(self.input_info)  # [s(t+1)] #
        # ----------------------------------------------------------
        return 0

    def dumy_step(self, Nob=False):
        # Old Data (time t) ---------------------------------------
        if Nob:
            get_one_line = self.Nob_db.iloc[self.ENVStep]
            get_one_col = self.Nob_db.columns.to_list()
        else:
            get_one_line = self.dumy_db.iloc[self.ENVStep]
            get_one_col = self.dumy_db.columns.to_list()

        for col in get_one_col:
            if col in self.mem.keys():
                self.mem[col]['Val'] = float(get_one_line[col])

        # New Data (time t+1) -------------------------------------
        sleep(0.2)
        self.CMem.update()  # 선택 변수 mem 업데이트

        # 추가된 변수 고려
        self.mem['cCOOLRATE']['Val'] = self.CMem.CoolingRATE.get_temp(self.CMem.CTIME)

        self._append_val_to_list()
        self.ENVStep += 1

        # next_state, next_state_list = self.get_state(self.input_info)  # [s(t+1)] #
        # ----------------------------------------------------------
        return 0

    def reset(self, file_name, initial_nub=1, mal=False, mal_case=1, mal_opt=0, mal_time=5):
        # 1] CNS 상태 초기화 및 초기화된 정보 메모리에 업데이트
        super(ENVCNS, self).reset(initial_nub=initial_nub, mal=False, mal_case=1, mal_opt=0, mal_time=5, file_name=file_name)
        # 2] 업데이트된 'Val'를 'List'에 추가 및 ENVLogging 초기화
        self._append_val_to_list()
        # 3] ENVStep 초기화
        self.ENVStep = 0
        return 0


if __name__ == '__main__':
    # ENVCNS TEST
    env = ENVCNS(Name='Env1', IP='192.168.0.103', PORT=int(f'7101'))
    # Run
    for _ in range(1, 4):
        env.reset(file_name=f'Ep{_}')
        for __ in range(500):
            A = 0
            env.step(A)