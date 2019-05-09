import multiprocessing
import time

class TSMS(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]
        self.TSMS_monitoring = TSMS_Monitoring(mem=mem)
        self.TSMS_Raw_data_monitoring = TSMS_Raw_data_monitoring(mem=mem)

    def run(self):
        while True:
            #==========================================================================================#
            # CNS 초기 조건 발생시 대기하는 부분
            if len(self.mem['QPROREL']['L']) >= 1:
            # ==========================================================================================#
                self.TSMS_monitoring.monitoring()
                self.TSMS_Raw_data_monitoring.Detection()
                self.TSMS_Raw_data_monitoring.ActionPlanning()

                time.sleep(1)

class TSMS_Monitoring:
    '''
    Operability_2019-01-27 폴더의 test1.py 파일 구현
    '''

    def __init__(self, mem):
        self.mem = mem[0]
        self.TSMS_mem = mem[-3]

    def monitoring(self):

        #KLAMPO124 KLAMPO125 KLAMPO126

        if self.mem['KLAMPO124']['V'] == 1:
            if self.mem['KLAMPO125']['V'] == 1:
                self.TSMS_mem['Monitoring_result'] = 1
            elif self.mem['KLAMPO126']['Val'] == 1:
                self.TSMS_mem['Monitoring_result'] = 1
            else:
                self.TSMS_mem['Monitoring_result'] = 0

        elif self.mem['KLAMPO125']['Val'] == 1:
            if self.mem['KLAMPO126']['Val'] == 1:
                self.TSMS_mem['Monitoring_result'] = 1
            else:
                self.TSMS_mem['Monitoring_result'] = 0

        else:
            self.TSMS_mem['Monitoring_result'] = 0


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
        self.action = []

    def Detection(self):

        if self.trigger == True :

            if 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
                self.TSMS_mem['Raw_result'] = 1
                self.TSMS_mem['Raw_violation'] = 'X'
                self.TSMS_mem['Raw_text_result'] = 'LCO Satisfaction'
            else:
                self.TSMS_mem['Raw_result'] = 0
                self.Detection_signal = 1
                print(self.ActionPlanning_signal)
                self.TSMS_mem['Raw_text_result'] = 'LCO Dissatisfaction'
                self.TSMS_mem['Raw_violation'] = 'LCO 3.4.1'
                # self.trigger.append(0)

        elif self.ActionPlanning_signal == 1:
            if self.timer1_signal == True:
                self.timer1 += 1

            if 154.7 < self.mem['ZINST65']['V'] <  161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
                if self.timer1 < 180 : #180 -> 7200으로 바꿀 것
                    print('Action Success - 복구 성공, 제한시간 내 수행')
                    print(self.timer1)
                    self.TSMS_mem['Raw_result'] = 1
                    self.trigger = True
                    print('Detection1번 신호 발생')
                    self.TSMS_mem['Raw_action'] = 'Action Success - 복구 성공, 제한시간 내 수행'
                else :
                    print('Action Fail - 복구 성공, 제한시간 초과')
                    print(self.timer1)
                    self.TSMS_mem['Raw_result'] = 0
                    self.Detection_signal = 2
                    self.TSMS_mem['Raw_action'] = 'Action Fail - 복구 성공, 제한시간 초과'
            else:
                if self.timer1 < 180 :
                    print('Action Ongoing')
                    self.TSMS_mem['Raw_result'] = 0
                    self.Detection_signal = 0
                    print(self.timer1)
                    self.TSMS_mem['Raw_action'] = 'Action Ongoing'
                else:
                    print('조치 실패 - 복구 실패, 제한시간 초과')
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
            print('신호 잘옴.')
            self.trigger = False
            self.ActionPlanning_signal = 1
            self.timer1_signal = True

        elif self.Detection_signal == 2:
            print('운전모드 신호 줘라')
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
