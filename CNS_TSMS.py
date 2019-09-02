# ======================================================================================================================
# Working (2019-08-29)
# 모듈을 만들어서 메모리를 채울거야!
# ======================================================================================================================

import multiprocessing
import time
import copy

class TSMS_module(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]           # main mem connection
        self.auto_mem = mem[-2]     # 자율 운전 메모리
        self.strategy_mem = mem[1]  # 전략 모듈 메모리
        self.trig_mem = mem[2]      # TSMS 모듈 메모리

        # self.dumy_mem = copy.deepcopy(self.trig_mem)

    def run(self):
        while True:
            # ==========================================
            # 추후 TSMS 모듈 작동 조건 로직 추가
            # if self.mem['KCNTOMS']['V'] < 4:
            #     self.ui.Performace_Mn.clear()
            #     self.TSMS_State = {}

            # if self.strategy_selection_mem['operation_mode'] != []:
            #     if self.strategy_selection_mem['operation_mode'][-1] == 2:
            # ==========================================
            self.dumy_mem = copy.deepcopy(self.trig_mem)
            self.Monitoring_Operation_Mode()
            self.Monitoring()
            self.update_timmer()
            self.action_monitoring()
            print(self.trig_mem)


    def Calculator_SDM(self):

        self.init_para = {
            'HFP': 100,  # H
            'ReatorPower': 90,  # T
            'BoronConcentration': 1318,  # T
            'Burnup': 4000,  # T
            'Burnup_BOL': 150,  # H
            'Burnup_EOL': 18850,  # H
            'TotalPowerDefect_BOL': 1780,  # H
            'TotalPowerDefect_EOL': 3500,  # H
            'VoidCondtent': 50,  # H
            'TotalRodWorth': 5790,  # H
            'WorstStuckRodWorth': 1080,  # H
            'InoperableRodNumber': 1,  # T
            'BankWorth_D': 480,  # H
            'BankWorth_C': 1370,  # H
            'BankWorth_B': 1810,  # H
            'BankWorth_A': 760,  # H
            'AbnormalRodName': 'C',  # T
            'AbnormalRodNumber': 1,  # T
            'ShutdownMarginValue': 1770,  # H
        }

        # 1. BOL, 현출력% -> 0% 하기위한 출력 결손량 계산
        ReactorPower = self.mem['QPROLD']['V'] * 100
        PowerDefect_BOL = self.init_para['TotalPowerDefect_BOL'] * ReactorPower / self.init_para['HFP']

        # 2. EOL, 현출력% -> 0% 하기위한 출력 결손량 계산
        PowerDefect_EOL = self.init_para['TotalPowerDefect_EOL'] * ReactorPower / self.init_para['HFP']

        # 3. 현재 연소도, 현출력% -> 0% 하기위한 출력 결손량 계산
        A = self.init_para['Burnup_EOL'] - self.init_para['Burnup_BOL']
        B = PowerDefect_EOL - PowerDefect_BOL
        C = self.init_para['Burnup'] - self.init_para['Burnup_EOL']

        PowerDefect_Burnup = B * C / A + PowerDefect_BOL

        # 4. 반응도 결손량을 계산
        PowerDefect_Final = PowerDefect_Burnup + self.init_para['VoidCondtent']

        # 5. 운전불가능 제어봉 제어능을 계산
        InoperableRodWorth = self.init_para['InoperableRodNumber'] * self.init_para['WorstStuckRodWorth']

        # 6. 비정상 제어봉 제어능을 계산
        AbnormalRodWorth = self.init_para['BankWorth_{}'.format(
            self.init_para['AbnormalRodName'])] / 8 * self.init_para['AbnormalRodNumber']

        # 7. 운전 불능, 비정상 제어봉 제어능의 합 계산
        InoperableAbnormal_RodWorth = InoperableRodWorth + AbnormalRodWorth

        # 8. 현 출력에서의 정지여유도 계산
        ShutdownMargin = self.init_para['TotalRodWorth'] - InoperableAbnormal_RodWorth - PowerDefect_Final

        return ShutdownMargin

    def Monitoring(self):
        # LCO 3.4.4
        if [self.mem['KLAMPO124']['V'], self.mem['KLAMPO125']['V'], self.mem['KLAMPO126']['V']].count(0) >= 2:
            # if not 'LCO 3.4.4' in self.TSMS_State.keys():
            self.dumy_mem['LCO3.4.4']['alarm'].append(1)
            self.dumy_mem['LCO3.4.4']['start_time'] = self.Call_CNS_time[1]
            self.dumy_mem['LCO3.4.4']['end_time'] = self.Call_CNS_time[1]+24000

        # LCO 3.4.1
        if not 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
            # if not 'LCO 3.4.1' in self.TSMS_State.keys():
            self.dumy_mem['LCO3.4.1']['alarm'].append(1)
            self.dumy_mem['LCO3.4.1']['start_time'] = self.Call_CNS_time[1]
            self.dumy_mem['LCO3.4.1']['end_time'] = self.Call_CNS_time[1] + 7200

        # LCO 3.1.1
        current_SDM = self.Calculator_SDM()
        if current_SDM < 1770:
            # if not 'LCO 3.1.1' in self.TSMS_State.keys():
            self.dumy_mem['LCO3.1.1']['alarm'].append(1)
            self.dumy_mem['LCO3.1.1']['start_time'] = self.Call_CNS_time[1]
            self.dumy_mem['LCO3.1.1']['end_time'] = self.Call_CNS_time[1] + 900

        # # LCO 3.4.3
        # if self.predict_SVM(self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']) != 1:
        #     if not 'LCO 3.4.3' in self.TSMS_State.keys():
        #         self.TSMS_State['LCO 3.4.3'] = {'Start_time': self.Call_CNS_time[1],
        #                                         'End_time': self.Call_CNS_time[1] + 1800}
        #         end_time = self.calculate_time(self.Call_CNS_time[1] + 1800)
        #         self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.4.3\tDissatisfaction'.format(self.Call_CNS_time[0],
        #                                                                                   end_time))

        for key_val in self.trig_mem.keys():
                self.trig_mem[key_val] = self.dumy_mem[key_val]


    def Monitoring_Operation_Mode(self):
        if self.mem['CRETIV']['V'] >= 0:
            if self.mem['ZINST1']['V'] > 5:
                self.dumy_mem['operation_mode'].append(1)
            elif self.mem['ZINST1']['V'] <= 5:
                self.dumy_mem['operation_mode'].append(2)
        elif self.mem['CRETIV']['V'] < 0:
            if self.mem['UCOLEG1']['V'] >= 177:
                self.dumy_mem['operation_mode'].append(3)
            elif 93 < self.mem['UCOLEG1']['V'] < 177:
                self.dumy_mem['operation_mode'].append(4)
            elif self.mem['UCOLEG1']['V'] <= 93:
                self.dumy_mem['operation_mode'].append(5)
        else:
            self.dumy_mem['operation_mode'].append(6)

        for key_val in self.trig_mem.keys():
                self.trig_mem[key_val] = self.dumy_mem[key_val]


    # ==========================================================
    # 아.. 이 로직이 돌아가려면 무조건! 시간이 필요하구나.. 메모리에 시간도 올리도록 하자.
    # 아니다 메모리에 까지 올려야하나?? 일단 올려보지뭐.
    def update_timmer(self):
        Time_val = self.mem['KCNTOMS']['V'] // 5
        t_sec = Time_val % 60   # x sec
        t_min = Time_val // 60  # x min
        t_hour = t_min // 60
        t_min = t_min % 60

        if t_min >= 10:
            t_min = '{}'.format(t_min)
        else:
            t_min = '0{}'.format(t_min)

        if t_sec >= 10:
            t_sec = '{}'.format(t_sec)
        else:
            t_sec = '0{}'.format(t_sec)

        if t_hour >= 10:
            t_hour = '{}'.format(t_hour)
        else:
            t_hour = '0{}'.format(t_hour)

        self.Call_CNS_time = ['[{}:{}:{}]'.format(t_hour, t_min, t_sec), Time_val]

    def action_monitoring(self):
        if self.trig_mem['LCO3.4.4']['alarm'] !=[]:
            if self.trig_mem['LCO3.4.4']['alarm'][-1] == 1:
                if self.trig_mem['operation_mode'][-1] == 3:
                    if self.trig_mem['LCO3.4.4']['end_time'] <= self.Call_CNS_time[1]:
                        self.dumy_mem['LCO3.4.4']['alarm_action'].append(1)
                    else:
                        self.dumy_mem['LCO3.4.4']['alarm_action'].append(0)
                elif self.trig_mem['operation_mode'][-1] == 1 or self.trig_mem['operation_mode'][-1] == 2:
                    if self.trig_mem['LCO3.4.4']['end_time'] <= self.Call_CNS_time[1]:
                        self.dumy_mem['LCO3.4.4']['alarm_action'].append(1)
                    else:
                        self.dumy_mem['LCO3.4.4']['alarm_action'].append(2)

        elif self.trig_mem['LCO3.4.1']['alarm'] !=[]:
            if self.trig_mem['LCO3.4.1']['alarm'][-1] ==1:
                if 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
                    if self.trig_mem['LCO3.4.1']['end_time'] <= self.Call_CNS_time[1]:
                        self.dumy_mem['LCO3.4.1']['alarm_action'].append(1)
                    else:
                        self.dumy_mem['LCO3.4.1']['alarm_action'].append(0)
                else:
                    if self.trig_mem['LCO3.4.1']['end_time'] <= self.Call_CNS_time[1]:
                        self.dumy_mem['LCO3.4.1']['alarm_action'].append(1)
                    else:
                        self.dumy_mem['LCO3.4.1']['alarm_action'].append(2)

        elif self.trig_mem['LCO3.1.1']['alarm'] != []:
            if self.trig_mem['LCO3.1.1']['alarm'][-1] ==1:
                if self.Calculator_SDM() >= 1770:
                    if self.trig_mem['LCO3.1.1']['end_time'] <= self.Call_CNS_time[1]:
                        self.dumy_mem['LCO3.1.1']['alarm_action'].append(1)
                    else:
                        self.dumy_mem['LCO3.1.1']['alarm_action'].append(2)
                else:
                    if self.trig_mem['LCO3.1.1']['end_time'] <= self.Call_CNS_time[1]:
                        self.dumy_mem['LCO3.1.1']['alarm_action'].append(1)
                    else:
                        self.dumy_mem['LCO3.1.1']['alarm_action'].append(0)
        else:
            pass

        for key_val in self.trig_mem.keys():
                self.trig_mem[key_val] = self.dumy_mem[key_val]


        # elif LCO_name == 'LCO 3.4.3':
        #     currnet_mode = self.Monitoring_Operation_Mode()
        #     cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
        #     cont += '=' * 50 + '\n'
        #     cont += 'Follow up action :\n'
        #     cont += '  - Enter allowable operation region\n'
        #     cont += '  - Limit Time : 30 min\n'
        #     cont += '=' * 50 + '\n'
        #     cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
        #     cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
        #                                         self.calculate_time(self.Call_CNS_time[1]),
        #                                         self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
        #     cont += '=' * 50 + '\n'
        #     if self.predict_SVM(self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']) != 1:
        #         if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
        #             cont += '현재 운전 상태 : Action Fail\n'
        #         else:
        #             cont += '현재 운전 상태 : Action Ongoing\n'
        #     else:
        #         if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
        #             cont += '현재 운전 상태 : Action Fail\n'
        #         else:
        #             cont += '현재 운전 상태 : Action Success\n'

    #
    # def Make_P_T_SVM(self):
    #     # print('SVM 모델 훈련 시작')
    #     data = pd.read_csv('SVM_PT_DATA.csv', header=None)
    #
    #     X = data.loc[:, 0:1].values
    #     y = data[2].values
    #
    #     # 데이터 전처리
    #     self.scaler.fit(X)
    #     X = self.scaler.transform(X)
    #     # SVM 훈련
    #     svc = svm.SVC(kernel='rbf', gamma='auto', C=1000)
    #     svc.fit(X, y)
    #     # print("훈련 세트 정확도 : {: .3f}".format(svc.score(X_train_scaled, y_train)))
    #     # print("테스트 세트 정확도 : {: .3f}".format(svc.score(X_test_scaled, y_test)))
    #     return svc
    #
    # def predict_SVM(self, Temp, Pressure):
    #     temp = self.scaler.transform([[Temp, Pressure]])
    #     return self.model_svm.predict(temp)[0]
