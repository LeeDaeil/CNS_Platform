import multiprocessing
import time
import pandas as pd
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler

class TSMS(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]
        self.TSMS_monitoring = TSMS_Monitoring(mem=mem)
        self.TSMS_Raw_data_monitoring = TSMS_Raw_data_monitoring(mem=mem)
        self.TSMS_Shutdown_margin_calculation = TSMS_Shutdown_margin_calculation(mem=mem)
        self.TSMS_Shutdown_margin_calculation_ab = TSMS_Shutdown_margin_calculation_abnormal(mem=mem)

        self.TSMS_mem = mem[-3]
        self.TSMS_PT_cal = TSMS_SVM_PTcurve(mem=mem)
        self.current_len = len(self.mem['QPROREL']['L'])

    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['L']) > 0 and self.current_len != len(self.mem['QPROREL']['L']):
                self.current_len = len(self.mem['QPROREL']['L'])
            # ==========================================================================================#
                self.TSMS_monitoring.run()
                # self.TSMS_Raw_data_monitoring.Detection()
                # self.TSMS_Raw_data_monitoring.ActionPlanning()
                # self.TSMS_Shutdown_margin_calculation.shutdown_margin_calculation()
                # self.TSMS_Shutdown_margin_calculation_ab.detect()
                # self.TSMS_PT_cal.predict_svm()
                # print(self.TSMS_mem)
                time.sleep(1)


class TSMS_Monitoring:
    '''
    Operability_2019-01-27 폴더의 test1.py 파일 구현
    RCS Operability 폴더의 test.py 와 동일
    '''

    def __init__(self, mem):
        self.mem = mem[0]
        self.TSMS_mem = mem[-3]

    def run(self):
        self.monitoring()
        print(self.TSMS_mem['Monitoring_result'])

    def monitoring(self):

        #KLAMPO124 KLAMPO125 KLAMPO126

        if [self.mem['KLAMPO124']['V'], self.mem['KLAMPO125']['V'], self.mem['KLAMPO126']['V']].count(0) >= 2:
            self.TSMS_mem['Monitoring_result'] = 0
        else:
            self.TSMS_mem['Monitoring_result'] = 1


class TSMS_Raw_data_monitoring:
    '''
    RawdataMonitoring 폴더의 test3.py 파일 구현
    '''

    def __init__(self, mem):
        self.mem = mem[0]
        self.TSMS_mem = mem[-3]

        # test3.py
        self.trigger = True
        self.Detection_signal = 0
        self.ActionPlanning_signal = 0
        self.timer1 = 0
        self.timer2 = 0
        self.timer1_signal = False
        self.timer2_signal = False

    def Detection(self):

        if self.trigger == True :

            if 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
                self.TSMS_mem['Raw_result'] = 1
                self.TSMS_mem['Raw_violation'] = 'X'
                self.TSMS_mem['Raw_text_result'] = 'LCO Satisfaction'
            else:
                self.TSMS_mem['Raw_result'] = 0
                self.Detection_signal = 1
                # print(self.ActionPlanning_signal)
                self.TSMS_mem['Raw_text_result'] = 'LCO Dissatisfaction'
                self.TSMS_mem['Raw_violation'] = 'LCO 3.4.1'
                # self.trigger.append(0)

        elif self.ActionPlanning_signal == 1:
            if self.timer1_signal == True:
                self.timer1 += 1

            if 154.7 < self.mem['ZINST65']['V'] <  161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
                if self.timer1 < 180 : #180 -> 7200으로 바꿀 것
                    # print('Action Success - 복구 성공, 제한시간 내 수행')
                    # print(self.timer1)
                    self.TSMS_mem['Raw_result'] = 1
                    self.trigger = True
                    # print('Detection1번 신호 발생')
                    self.TSMS_mem['Raw_action'] = 'Action Success - 복구 성공, 제한시간 내 수행'
                else :
                    # print('Action Fail - 복구 성공, 제한시간 초과')
                    # print(self.timer1)
                    self.TSMS_mem['Raw_result'] = 0
                    self.Detection_signal = 2
                    self.TSMS_mem['Raw_action'] = 'Action Fail - 복구 성공, 제한시간 초과'
            else:
                if self.timer1 < 180 :
                    # print('Action Ongoing')
                    self.TSMS_mem['Raw_result'] = 0
                    self.Detection_signal = 0
                    # print(self.timer1)
                    self.TSMS_mem['Raw_action'] = 'Action Ongoing'
                else:
                    # print('조치 실패 - 복구 실패, 제한시간 초과')
                    self.TSMS_mem['Raw_result'] = 0
                    self.Detection_signal = 2
                    self.TSMS_mem['Raw_action'] = 'Action Fail - 복구 실패, 제한시간 초과'

        elif self.ActionPlanning_signal == 2:

            # if self.timer2_signal == True :
            #     self.timer2 += 1

            self.Monitoring()
            print(self.Monitoring())
            print(self.mem['CRETIV']['V'])

            if self.Monitoring() == 2:
                self.TSMS_mem['Raw_result'] = 1
            else:   # elif self.Monitoring() == 1 or 3 or 4 or 5 or 6
                self.TSMS_mem['Raw_result'] = 0
                print('여기임?')

    def ActionPlanning(self):

        if self.Detection_signal == 1:
            # print('신호 잘옴.')
            self.trigger = False
            self.ActionPlanning_signal = 1
            self.timer1_signal = True

        elif self.Detection_signal == 2:
            # print('운전모드 신호 줘라')
            self.trigger = False
            self.ActionPlanning_signal = 2 # action signal을 2로 지정함. 'Detection'에서 운전모드 감시할 수 있도록.
            # self.timer2_signal = True
        else:
            print('pass')
            pass

    def Monitoring(self):

        # TermalPower = para.ThermalPower ZINST1
        # Reactivity = para.Reactivity self.mem['CRETIV']['Val']
        # AvgTemp = para.Reactivity UCOLEG1

        if self.mem['CRETIV']['V'] >= 0:
            if self.mem['ZINST1']['V'] > 5:
                return 1
            elif self.mem['ZINST1']['V'] <= 5:
                return 2
        elif self.mem['CRETIV']['V'] < 0:
            if self.mem['UCOLEG1']['V'] >= 350:
                return 3
            elif 200 < self.mem['UCOLEG1']['V'] < 350:
                return 4
            elif self.mem['UCOLEG1']['V'] <= 200:
                return 5
        else:
            return 6


class TSMS_Shutdown_margin_calculation:
    '''
    ShutdownMarginCalculation.py 파일 구현
    '''

    def __init__(self, mem):
        self.mem = mem[0]
        self.TSMS_mem = mem[-3]

        # 계산을 위한 초기 파라메터
        self.init_para = {
            'HFP': 100,  # H
            'ReatorPower': 90,              # T
            'BoronConcentration': 1318,     # T
            'Burnup': 4000,                 # T
            'Burnup_BOL': 150,              # H
            'Burnup_EOL': 18850,            # H
            'TotalPowerDefect_BOL': 1780,   # H
            'TotalPowerDefect_EOL': 3500,   # H
            'VoidCondtent': 50,             # H
            'TotalRodWorth': 5790,          # H
            'WorstStuckRodWorth': 1080,     # H
            'InoperableRodNumber': 1,       # T
            'BankWorth_D': 480,             # H
            'BankWorth_C': 1370,            # H
            'BankWorth_B': 1810,            # H
            'BankWorth_A': 760,             # H
            'AbnormalRodName': 'C',         # T
            'AbnormalRodNumber': 1,         # T
            'ShutdownMarginValue': 1770,    # H
        }

    def shutdown_margin_calculation(self):
        # 1. BOL, 현출력% -> 0% 하기위한 출력 결손량 계산
        ReactorPower = self.mem['QPROLD']['V'] * 100
        self.TSMS_mem['Shut_BOL'] = self.init_para['TotalPowerDefect_BOL'] * ReactorPower / self.init_para['HFP']

        # 2. EOL, 현출력% -> 0% 하기위한 출력 결손량 계산
        self.TSMS_mem['Shut_EOL'] = self.init_para['TotalPowerDefect_EOL'] * ReactorPower / self.init_para['HFP']

        # 3. 현재 연소도, 현출력% -> 0% 하기위한 출력 결손량 계산
        A = self.init_para['Burnup_EOL'] - self.init_para['Burnup_BOL']
        B = self.TSMS_mem['Shut_EOL'] - self.TSMS_mem['Shut_BOL']
        C = self.init_para['Burnup'] - self.init_para['Burnup_EOL']

        self.TSMS_mem['Shut_Burn_up'] = B * C / A + self.TSMS_mem['Shut_BOL']

        # 4. 반응도 결손량을 계산
        self.TSMS_mem['Shut_Fin'] = self.TSMS_mem['Shut_Burn_up'] + self.init_para['VoidCondtent']

        # 5. 운전불가능 제어봉 제어능을 계산
        self.TSMS_mem['Shut_Inoper_rod'] = self.init_para['InoperableRodNumber'] * self.init_para['WorstStuckRodWorth']

        # 6. 비정상 제어봉 제어능을 계산
        self.TSMS_mem['Shut_Abnormal_rod_worth'] = self.init_para['BankWorth_{}'.format(
            self.init_para['AbnormalRodName'])] / 8 * self.init_para['AbnormalRodNumber']

        # 7. 운전 불능, 비정상 제어봉 제어능의 합 계산
        self.TSMS_mem['Shut_Inoper_ableAbnormal_RodWorth'] = self.TSMS_mem['Shut_Inoper_rod'] \
                                                             + self.TSMS_mem['Shut_Abnormal_rod_worth']

        # 8. 현 출력에서의 정지여유도 계산
        self.TSMS_mem['Shut_ShutdownMargin'] = self.init_para['TotalRodWorth'] - \
                                               self.TSMS_mem['Shut_Inoper_ableAbnormal_RodWorth'] - \
                                               self.TSMS_mem['Shut_Fin']

        # 9. 결과 출력
        self.TSMS_mem['Shut_Result'] = '만족' if self.TSMS_mem['Shut_ShutdownMargin'] \
                                               >= self.init_para['ShutdownMarginValue'] else '불만족'


class TSMS_Shutdown_margin_calculation_abnormal:
    '''
    ShutdownMarginCalculation_abnormal.py 파일 구현
    '''

    def __init__(self, mem):
        self.mem = mem[0]
        self.TSMS_mem = mem[-3]

    def detect(self):
        if self.TSMS_mem['Shut_Result'] == '불만족':
            # ex. self.TSMS_mem['Raw_violation'] = 'LCO 3.4.1'
            detected_bin = self.diagnosis(self.TSMS_mem['Raw_violation'])
            self.TSMS_mem['Shut_ab_comment'], t = self.suggest(diagnosis_bin=detected_bin,
                                                               raw_violation=self.TSMS_mem['Raw_violation'],
                                                               shutdown_margin=self.TSMS_mem['Shut_ShutdownMargin'])
        else: pass # 만족 조건으로 pass

    def diagnosis(self, Raw_violation):

        if Raw_violation == 'LCO 3.1.1':
            return 0 # detected_bin
        else:
            print('?')

    def suggest(self, diagnosis_bin, raw_violation, shutdown_margin):

        A = shutdown_margin
        B = 1770
        C = -5.9
        time_limit, suggested_comment = 0, ''

        if diagnosis_bin == 0:  # LCO 3.1.1

            parameter = 'KBCDO16'
            current_value = self.mem[parameter]['V']
            boron = (A - B) / C
            target_value = current_value + boron
            time_limit = 900

            suggested_comment = '위반사항: {}, 파라메터: {}, 현재 보론: {}, 목표 보론: {} 제한시간:{}'.format(
                raw_violation, parameter, current_value, target_value, time_limit)

        else:
            print('?')

        return suggested_comment, time_limit


class TSMS_SVM_PTcurve:

    def __init__(self, mem):
        self.mem = mem[0]
        self.TSMS_mem = mem[-3]

        self.scaler = MinMaxScaler()

        self.model_svm = self.train_model_svm()

    def train_model_svm(self):
        # print('SVM 모델 훈련 시작')
        data = pd.read_csv('SVM_PT_DATA.csv', header=None)

        X = data.loc[:, 0:1].values
        y = data[2].values

        # 데이터 전처리
        self.scaler.fit(X)
        X = self.scaler.transform(X)
        # SVM 훈련
        svc = svm.SVC(kernel='linear', gamma='auto', C=1000)
        svc.fit(X, y)
        # print("훈련 세트 정확도 : {: .3f}".format(svc.score(X_train_scaled, y_train)))
        # print("테스트 세트 정확도 : {: .3f}".format(svc.score(X_test_scaled, y_test)))
        return svc

    def predict_svm(self):
        # [온도, 압력] # svc.predict([[0, 0.5]]) 쌍괄호 사용
        import numpy as np
        temp = self.scaler.transform([[self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']]])
        self.TSMS_mem['PT_Result'] = self.model_svm.predict(temp)[0]
