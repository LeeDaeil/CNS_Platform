from Interface.TSMS import Ui_Dialog as TSMS_UI
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class POP_TSMS(QDialog):
    def __init__(self, mem=None, auto_mem=None, strategy_mem=None):
        super().__init__()

        if mem != None:
            self.mem = mem
            self.auto_mem = auto_mem
            self.strategy_mem = strategy_mem

        self.TSMS_UI = TSMS_UI()
        self.TSMS_UI.setupUi(self)

        self.run_TSMS()

        self.show()

    def run_TSMS(self):
        if self.strategy_mem['operation_mode'] != []:
            if self.strategy_mem['operation_mode'][-1] == 2:
                self.Monitoring()
                print(self.strategy_mem['operation_mode'][-1])


    # def run_TSMS(self):
    #     # if self.mem['KCNTOMS']['V'] < 4:
    #     #     self.ui.Performace_Mn.clear()
    #     #     self.TSMS_State = {}
    #
    #     print(self.strategy_mem)
    #
    #     if self.strategy_mem['operation_mode'] != []:
    #         if self.strategy_mem['operation_mode'][-1] == 2:
    #             self.Monitoring()
    #             print(self.strategy_mem['operation_mode'][-1])

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
        print('22')
        # LCO 3.4.4
        if [self.mem['KLAMPO124']['V'], self.mem['KLAMPO125']['V'], self.mem['KLAMPO126']['V']].count(0) >= 2:
            if not 'LCO 3.4.4' in self.TSMS_State.keys():
                self.TSMS_State['LCO 3.4.4'] = {'Start_time': self.Call_CNS_time[1],
                                                'End_time': self.Call_CNS_time[1]+24000}
                end_time = self.calculate_time(self.Call_CNS_time[1]+24000)
                self.TSMS_UI.btn_alarm_1.setText('LCO 3.4.4')

        # LCO 3.4.1
        if not 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
            if not'LCO 3.4.1' in self.TSMS_State.keys():
                self.TSMS_State['LCO 3.4.1'] = {'Start_time': self.Call_CNS_time[1],
                                                'End_time': self.Call_CNS_time[1]+7200}
                end_time = self.calculate_time(self.Call_CNS_time[1]+7200)
                self.TSMS_UI.btn_alarm_2.setText('LCO 3.4.1')
                print('33')
        # # LCO 3.4.3
        # if self.predict_SVM(self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']) != 1:
        #     if not'LCO 3.4.3' in self.TSMS_State.keys():
        #         self.TSMS_State['LCO 3.4.3'] = {'Start_time': self.Call_CNS_time[1],
        #                                         'End_time': self.Call_CNS_time[1]+1800}
        #         end_time = self.calculate_time(self.Call_CNS_time[1]+1800)
        #         self.TSMS_UI.btn_alarm_3.setText('LCO 3.4.3')
        # LCO 3.1.1
        current_SDM = self.Calculator_SDM()
        if current_SDM < 1770:
            if not 'LCO 3.1.1' in self.TSMS_State.keys():
                self.TSMS_State['LCO 3.1.1'] = {'Start_time': self.Call_CNS_time[1],
                                                'End_time': self.Call_CNS_time[1] + 900}
                end_time = self.calculate_time(self.Call_CNS_time[1] + 900)
                self.TSMS_UI.btn_alarm_4.setText('LCO 3.1.1')

    # def Monitoring_Operation_Mode(self):
    #     if self.mem['CRETIV']['V'] >= 0:
    #         if self.mem['ZINST1']['V'] > 5:
    #             mode = 1
    #
    #         elif self.mem['ZINST1']['V'] <= 5:
    #             mode = 2
    #     elif self.mem['CRETIV']['V'] < 0:
    #         if self.mem['UCOLEG1']['V'] >= 177:
    #             mode = 3
    #         elif 93 < self.mem['UCOLEG1']['V'] < 177:
    #             mode = 4
    #         elif self.mem['UCOLEG1']['V'] <= 93:
    #             mode = 5
    #     else:
    #         mode = 6
    #     return mode
    #
    # def TSMS_LCO_info(self, item):
    #     LCO_name = item.text().split('\t')[1]
    #     if LCO_name == 'LCO 3.4.4':
    #         currnet_mode = self.Monitoring_Operation_Mode()
    #         cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
    #         cont += '=' * 50 + '\n'
    #         cont += 'Follow up action : Enter Mode 3\n'
    #         cont += '=' * 50 + '\n'
    #         cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
    #         cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
    #                                           self.calculate_time(self.Call_CNS_time[1]),
    #                                           self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
    #         cont += '=' * 50 + '\n'
    #         if currnet_mode == 3:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Success\n'
    #         elif currnet_mode == 1 or currnet_mode == 2:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Ongoing\n'
    #         cont += '=' * 50 + '\n'
    #         QMessageBox.information(self, "LCO 정보", cont)
    #
    #     elif LCO_name == 'LCO 3.4.1':
    #         currnet_mode = self.Monitoring_Operation_Mode()
    #         cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
    #         cont += '=' * 50 + '\n'
    #         cont += 'Follow up action :\n'
    #         cont += '  - 154.7 < RCS Pressure < 161.6 [kg/cm²]\n'
    #         cont += '  - 286.7 < RCS Cold-leg Temp < 293.3 [℃]\n'
    #         cont += '=' * 50 + '\n'
    #         cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
    #         cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
    #                                           self.calculate_time(self.Call_CNS_time[1]),
    #                                           self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
    #         cont += '=' * 50 + '\n'
    #         if 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Success\n'
    #         else:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Ongoing\n'
    #         cont += '=' * 50 + '\n'
    #         QMessageBox.information(self, "LCO 정보", cont)
    #
    #     elif LCO_name == 'LCO 3.4.3':
    #         currnet_mode = self.Monitoring_Operation_Mode()
    #         cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
    #         cont += '=' * 50 + '\n'
    #         cont += 'Follow up action :\n'
    #         cont += '  - Enter allowable operation region\n'
    #         cont += '  - Limit Time : 30 min\n'
    #         cont += '=' * 50 + '\n'
    #         cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
    #         cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
    #                                           self.calculate_time(self.Call_CNS_time[1]),
    #                                           self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
    #         cont += '=' * 50 + '\n'
    #         if self.predict_SVM(self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']) != 1:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Ongoing\n'
    #         else:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Success\n'
    #         cont += '=' * 50 + '\n'
    #         QMessageBox.information(self, "LCO 정보", cont)
    #
    #     elif LCO_name == 'LCO 3.1.1':
    #         currnet_mode = self.Monitoring_Operation_Mode()
    #         cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
    #         cont += '=' * 50 + '\n'
    #         cont += 'Follow up action :\n'
    #         cont += '  - Boron Injectionl\n'
    #         cont += '=' * 50 + '\n'
    #         cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
    #         cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
    #                                             self.calculate_time(self.Call_CNS_time[1]),
    #                                             self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
    #         cont += '=' * 50 + '\n'
    #         if self.Calculator_SDM() >= 1770:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Ongoing\n'
    #         else:
    #             if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
    #                 cont += '현재 운전 상태 : Action Fail\n'
    #             else:
    #                 cont += '현재 운전 상태 : Action Success\n'
    #         cont += '=' * 50 + '\n'
    #         QMessageBox.information(self, "LCO 정보", cont)
    #
    #     else:
    #         pass
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
    # #
    # def predict_SVM(self, Temp, Pressure):
    #     temp = self.scaler.transform([[Temp, Pressure]])
    #     return self.model_svm.predict(temp)[0]



if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = POP_TSMS()
    w.exec()
    sys.exit(app.exec_())





# class sub_tren_window(QDialog):
#     def __init__(self, mem=None, auto_mem = None, strage_mem=None):
#         super().__init__()
#         # ===============================================================
#         # 메모리 호출 부분 없으면 Test
#         if mem != None:
#             self.mem = mem
#             self.auto_mem = auto_mem
#             self.strage_mem = strage_mem
#         else:
#             print('TEST_interface')
#         # ===============================================================
#         # CNS 정보 읽기
#         with open('pro.txt', 'r') as f:
#             self.cns_ip, self.cns_port = f.read().split('\t') # [cns ip],[cns port]
#         self.CNS_udp = CNS_Send_UDP.CNS_Send_Signal(self.cns_ip, int(self.cns_port))
#         # ===============================================================
#         self.Trend_ui = Rod_UI()
#         self.Trend_ui.setupUi(self)
#         # ===============================================================
#         # rod gp
#         self.draw_rod_his_gp()
#         # ===============================================================
#         # rod control
#         self.Trend_ui.rodup.clicked.connect(self.rod_up)
#         self.Trend_ui.roddown.clicked.connect(self.rod_down)
#         # ===============================================================
#
#         timer = QtCore.QTimer(self)
#         for _ in [self.update_window, self.update_rod_his_gp]:
#             timer.timeout.connect(_)
#         timer.start(600)
#
#         self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
#         self.show()
#
#     def rod_up(self):
#         self.CNS_udp._send_control_signal(['KSWO33', 'KSWO32'], [1, 0])
#
#     def rod_down(self):
#         self.CNS_udp._send_control_signal(['KSWO33', 'KSWO32'], [0, 1])
#
#     def update_window(self):
#         self.Trend_ui.Rod_1.setGeometry(10, 70, 41, abs(self.mem['KBCDO10']['V'] - 228))
#         self.Trend_ui.Rod_2.setGeometry(70, 70, 41, abs(self.mem['KBCDO9']['V'] - 228))
#         self.Trend_ui.Rod_3.setGeometry(130, 70, 41, abs(self.mem['KBCDO8']['V'] - 228))
#         self.Trend_ui.Rod_4.setGeometry(190, 70, 41, abs(self.mem['KBCDO7']['V'] - 228))
#         self.Trend_ui.Dis_Rod_4.setText(str(self.mem['KBCDO7']['V']))
#         self.Trend_ui.Dis_Rod_3.setText(str(self.mem['KBCDO8']['V']))
#         self.Trend_ui.Dis_Rod_2.setText(str(self.mem['KBCDO9']['V']))
#         self.Trend_ui.Dis_Rod_1.setText(str(self.mem['KBCDO10']['V']))
#
#         # 아래 자율/수동 패널
#         if self.strage_mem['strategy'][-1] == 'NA':
#             self.Trend_ui.label_5.setStyleSheet('background-color: rgb(255, 144, 146);'
#                                                 'border-style: outset;'
#                                                 'border-width: 0.5px;'
#                                                 'border-color: black;'
#                                                 'font: bold 14px;')
#             self.Trend_ui.label_3.setStyleSheet('background-color: rgb(255, 255, 255);'
#                                                 'border-style: outset;'
#                                                 'border-width: 0.5px;'
#                                                 'border-color: black;'
#                                                 'font: bold 14px;')
#         else:
#             self.Trend_ui.label_5.setStyleSheet('background-color: rgb(255, 255, 255);'
#                                                 'border-style: outset;'
#                                                 'border-width: 0.5px;'
#                                                 'border-color: black;'
#                                                 'font: bold 14px;')
#             self.Trend_ui.label_3.setStyleSheet('background-color: rgb(255, 144, 146);'
#                                                 'border-style: outset;'
#                                                 'border-width: 0.5px;'
#                                                 'border-color: black;'
#                                                 'font: bold 14px;')
#
#
#     def draw_rod_his_gp(self):
#         # 위 그래프
#         self.rod_cond = plt.figure()
#         self.rod_cond_ax = self.rod_cond.add_subplot(111)
#         self.rod_cond_canv = FigureCanvasQTAgg(self.rod_cond)
#         self.Trend_ui.Rod_his_cond.addWidget(self.rod_cond_canv)
#
#         # 아래 제어신호
#         self.rod_fig = plt.figure()
#         self.rod_ax = self.rod_fig.add_subplot(111)
#         self.rod_canvas = FigureCanvasQTAgg(self.rod_fig)
#         self.Trend_ui.Rod_his.addWidget(self.rod_canvas)
#
#     def update_rod_his_gp(self):
#         try:
#             self.rod_ax.clear()
#             temp = []
#             cns_time = []
#             for _ in range(len(self.mem['KSWO33']['D'])):
#                 if self.mem['KSWO33']['D'][_] == 0 and self.mem['KSWO32']['D'][_] == 0:
#                     temp.append(0)
#                     cns_time.append(self.mem['KCNTOMS']['D'][_]/5)
#                 elif self.mem['KSWO33']['D'][_] == 1 and self.mem['KSWO32']['D'][_] == 0:
#                     temp.append(1)
#                     cns_time.append(self.mem['KCNTOMS']['D'][_] / 5)
#                 elif self.mem['KSWO33']['D'][_] == 0 and self.mem['KSWO32']['D'][_] == 1:
#                     temp.append(-1)
#                     cns_time.append(self.mem['KCNTOMS']['D'][_] / 5)
#             self.rod_ax.plot(cns_time, temp)
#             self.rod_ax.set_ylim(-1.2, 1.2)
#             # self.rod_ax.set_xlim(0, 50)
#             self.rod_ax.set_yticks([-1, 0, 1])
#             self.rod_ax.set_yticklabels(['Down', 'Stay', 'UP'])
#             self.rod_ax.grid()
#             self.rod_canvas.draw()
#
#             self.rod_cond_ax.clear()
#             rod_cond_time = self.auto_mem['Start_up_operation_his']['time']
#             self.rod_cond_ax.plot(rod_cond_time, self.auto_mem['Start_up_operation_his']['power'])
#             self.rod_cond_ax.plot(rod_cond_time, self.auto_mem['Start_up_operation_his']['up_cond'])
#             self.rod_cond_ax.plot(rod_cond_time, self.auto_mem['Start_up_operation_his']['low_cond'])
#             self.rod_cond_ax.grid()
#             self.rod_cond_canv.draw()
#         except Exception as e:
#             print(self, e)
