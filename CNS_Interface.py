import sys
import multiprocessing
import pandas as pd
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler

import PyQt5
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5 import QtCore

# ------------------------------------------------------
from Interface.gui_study_9 import Ui_Dialog as Main_ui
from Interface.resource import Study_9_re_rc
# ------------------------------------------------------
from Interface.Trend_window import Ui_Dialog as Trend_ui

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class interface_function(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem

    def run(self):
        app = QApplication(sys.argv)
        w = MyForm(self.mem)
        w.exec()
        sys.exit(app.exec_())


class MyForm(QDialog):
    def __init__(self, mem):
        super().__init__()

        self.scaler = MinMaxScaler()
        self.model_svm = self.Make_P_T_SVM()
        print('SVM 시작 완료')

        self.ui = Main_ui()
        self.ui.setupUi(self)
        if True: # 메인 메모리와 연결된 부분
            self.mem = mem[0]
            self.Auto_mem = mem[-2]

        self.color_setting()

        # self.draw_power_gp()
        # self.draw_turbin_gp()

        # self.blick_switch = True
        self.CSF_test_mode = True
        if self.CSF_test_mode:
            self.CSF_upcont = 0

        self.Alarm_test_mode = True
        if self.Alarm_test_mode:
            self.Alarm_upcont = 0

        # x msec마다 업데이트
        update_module = [self.update_comp, self.update_CSF, self.update_display, self.update_alarm, self.update_timmer,
                         self.run_TSMS, self.run_AUTO]
        timer = QtCore.QTimer(self)
        for _ in update_module:
            timer.timeout.connect(_)
        timer.start(500)
        self.ui.Open_GP_Window.clicked.connect(self.call_trend_window)
        self.ui.Performace_Mn.itemClicked.connect(self.TSMS_LCO_info)

        # Autonomous controller ==========================================
        self.ui.pushButton_4.clicked.connect(self.Auto_Alarm_Click_Man)
        self.ui.pushButton_5.clicked.connect(self.Auto_Alarm_Click_Auto)
        # ================================================================
        self.show()

    # ======================= Trend Popup===============================

    def call_trend_window(self):
        self.trend_window = sub_tren_window(self.mem)

    # ======================= Initial_coloe=============================

    def color_setting(self):
        self.back_color = {
            'gray': "background-color: rgb(229, 229, 229);",
            'green': "background-color: rgb(0, 170, 0);",
            'yellow': "background-color: rgb(255, 255, 0);",
            'orange': "background-color: rgb(255, 85, 0);",
            'red': "background-color: rgb(255, 0, 0);",
        }
        self.back_img = {
            'P_1_ON': "image: url(:/Sys/Pump_1_ON.png);",  # P_1~6
            'P_1_OFF': "image: url(:/Sys/Pump_1_OFF.png);",  # P_1~6
            'P_2_ON': "image: url(:/Sys/Pump_2_ON.png);",  # P_7~9
            'P_2_OFF': "image: url(:/Sys/Pump_2_OFF.png);",  # P_7~9
            'P_3_ON': "image: url(:/Sys/Pump_3_ON.png);",  # P_7~9
            'P_3_OFF': "image: url(:/Sys/Pump_3_OFF.png);",  # P_7~9
            'V_1_OPEN': "image: url(:/Sys/Valve_1_OPEN.png);",
            'V_1_HALF': "image: url(:/Sys/Valve_1_HALF.png);",
            'V_1_CLOSE': "image: url(:/Sys/Valve_1_CLOSE.png);",
            'V_2_OPEN': "image: url(:/Sys/Valve_2_OPEN.png);",
            'V_2_HALF': "image: url(:/Sys/Valve_2_HALF.png);",
            'V_2_CLOSE': "image: url(:/Sys/Valve_2_CLOSE.png);",
        }

    # ======================= Dis ======================================

    def update_display(self):
        self.ui.D_50.setText('{:0.2f}'.format(self.mem['UHOLEG1']['V']))    # Hot leg temp loop 1
        self.ui.D_48.setText('{:0.2f}'.format(self.mem['UHOLEG2']['V']))    # Hot leg temp loop 2
        self.ui.D_45.setText('{:0.2f}'.format(self.mem['UHOLEG3']['V']))    # Hot leg temp loop 3
        self.ui.D_15.setText('{:0.2f}'.format(self.mem['UCOLEG1']['V']))  # Cold leg temp loop 1
        self.ui.D_18.setText('{:0.2f}'.format(self.mem['UCOLEG2']['V']))  # Cold leg temp loop 2
        self.ui.D_44.setText('{:0.2f}'.format(self.mem['UCOLEG3']['V']))  # Cold leg temp loop 3
        self.ui.D_21.setText('{:0.2f}'.format(self.mem['ZINST58']['V']))  # PZR pressure
        self.ui.D_9.setText('{:0.2f}'.format(self.mem['ZINST46']['V']))  # CORE outtemp
        self.ui.D_31.setText('{:0.2f}'.format(self.mem['ZINST78']['V']))  # S/G1 level
        self.ui.D_32.setText('{:0.2f}'.format(self.mem['ZINST75']['V']))  # S/G1 pressure
        self.ui.D_36.setText('{:0.2f}'.format(self.mem['ZINST77']['V']))  # S/G2 level
        self.ui.D_35.setText('{:0.2f}'.format(self.mem['ZINST74']['V']))  # S/G2 pressure
        self.ui.D_42.setText('{:0.2f}'.format(self.mem['ZINST76']['V']))  # S/G3 level
        self.ui.D_40.setText('{:0.2f}'.format(self.mem['ZINST73']['V']))  # S/G3 pressure

        self.ui.D_20.setText('{:0.2f}'.format(self.mem['ZINST63']['V']))  # PZR REAL LEVEL
        self.ui.D_12.setText('{:0.2f}'.format(self.mem['ZREAC']['V']))  # CORE_LEVEL
        self.ui.D_14.setText('{:0.2f}'.format(self.mem['KBCDO16']['V']))  # CORE_BORON
        self.ui.D_1.setText('{:0.2f}'.format(self.mem['URHRRE']['V']))  # RHR_TEMP
        self.ui.D_4.setText('{:0.2f}'.format(self.mem['WRHRRE']['V']))  # RHR_FLOW
        self.ui.D_5.setText('{:0.2f}'.format(self.mem['PVCT']['V']))  # VCT_PRESSURE
        self.ui.D_7.setText('{:0.2f}'.format(self.mem['ZVCT']['V']))  # VCT_LEVEL
        self.ui.D_27.setText('{:0.2f}'.format(self.mem['UCOND']['V']))  # COND_TEMP
        self.ui.D_30.setText('{:0.2f}'.format(self.mem['ZCOND']['V']))  # COND_PRESSURE
        self.ui.D_24.setText('{:0.2f}'.format(self.mem['ZCNDTK']['V']))  # CST1_LEVEL
        self.ui.D_25.setText('{:0.2f}'.format(self.mem['ZAFWTK']['V']))  # CST2_LEVEL

        self.ui.D_power.setText('{:0.2f} [%]'.format(self.mem['QPROREL']['V']*100))  # POWER
        self.ui.D_elec.setText('{:0.2f} [MWe]'.format(self.mem['ZINST124']['V']))  # POWER
        pass

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

        self.ui.CNS_Time.setText('CNS TIME : {}:{}:{}'.format(t_hour, t_min, t_sec))
        self.Call_CNS_time = ['[{}:{}:{}]'.format(t_hour, t_min, t_sec), Time_val]

    def calculate_time(self, time_val):
        t_sec = time_val % 60  # x sec
        t_min = time_val // 60  # x min
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
        return '[{}:{}:{}]'.format(t_hour, t_min, t_sec)

    # ======================= Alarm ======================================

    def update_alarm(self):
        if self.Alarm_test_mode:
            ui = self.ui
            ui = [ui.A_01, ui.A_02, ui.A_03, ui.A_04,
                  ui.A_05, ui.A_06, ui.A_07, ui.A_08,
                  ui.A_09, ui.A_10, ui.A_11, ui.A_12,
                  ui.A_13, ui.A_14, ui.A_15, ui.A_16,
                  ui.A_17, ui.A_18, ui.A_19, ui.A_20,
                  ui.A_21, ui.A_22, ui.A_23, ui.A_24,
                  ui.A_25, ui.A_26, ui.A_27, ui.A_EM,
                  ui.A_28, ui.A_29, ui.A_30, ui.A_31,
                  ui.A_32, ui.A_33, ui.A_34, ui.A_35,
                  ui.A_36, ui.A_37, ui.A_38, ui.A_39,
                  ui.A_40, ui.A_41, ui.A_42, ui.A_43,
                  ui.A_44, ui.A_45, ui.A_46, ui.A_47,
                  ui.A_48, ui.A_49, ui.A_50, ui.A_51,
                  ui.A_52, ui.A_53, ui.A_54, ui.A_55,
                  ui.A_56, ui.A_57, ui.A_58, ui.A_59,
                  ui.A_60, ui.A_61, ui.A_62, ui.A_63,
                  ui.A_64, ui.A_65, ui.A_66, ui.A_67,
                  ui.A_68, ui.A_69, ui.A_70, ui.A_71,
                  ui.A_72, ui.A_73, ui.A_74, ui.A_75,
                  ui.A_76, ui.A_77, ui.A_78, ui.A_79,
                  ui.A_80, ui.A_81, ui.A_82, ui.A_83]
            if self.Alarm_upcont > 96:
                self.Alarm_upcont = 1
                self.Alarm_test_mode = False
            elif self.Alarm_upcont == 0:
                for _ in ui[self.Alarm_upcont:self.Alarm_upcont+12]:
                    self.Alarm_initial(_, True)
            elif self.Alarm_upcont == 96:
                for _ in ui[self.Alarm_upcont-12:self.Alarm_upcont]:
                    self.Alarm_initial(_, False)
            else:
                for _ in ui[self.Alarm_upcont-12:self.Alarm_upcont]:
                    self.Alarm_initial(_, False)
                for _ in ui[self.Alarm_upcont:self.Alarm_upcont+12]:
                    self.Alarm_initial(_, True)
            self.Alarm_upcont += 12

            # Autonomous control part
            self.ui.pushButton.setStyleSheet(self.back_color['gray'])
            self.ui.pushButton_2.setStyleSheet(self.back_color['gray'])
            self.ui.pushButton_3.setStyleSheet(self.back_color['gray'])
            self.ui.pushButton_4.setStyleSheet(self.back_color['gray'])
            self.ui.pushButton_5.setStyleSheet(self.back_color['gray'])
            self.ui.pushButton_6.setStyleSheet(self.back_color['gray'])
            self.ui.pushButton_7.setStyleSheet(self.back_color['gray'])

        else:
            if True:
                self.Alarm_dis(self.ui.A_01, 'KLAMPO251')
                self.Alarm_dis(self.ui.A_02, 'KLAMPO252')
                self.Alarm_dis(self.ui.A_03, 'KLAMPO253')
                self.Alarm_dis(self.ui.A_04, 'KLAMPO254')

                self.Alarm_dis(self.ui.A_05, 'KLAMPO255')
                self.Alarm_dis(self.ui.A_06, 'KLAMPO256')
                self.Alarm_dis(self.ui.A_07, 'KLAMPO257')
                self.Alarm_dis(self.ui.A_08, 'KLAMPO258')

                self.Alarm_dis(self.ui.A_09, 'KLAMPO259')
                self.Alarm_dis(self.ui.A_10, 'KLAMPO260')
                self.Alarm_dis(self.ui.A_11, 'KLAMPO261')
                self.Alarm_dis(self.ui.A_12, 'KLAMPO262')

                self.Alarm_dis(self.ui.A_13, 'KLAMPO263')
                self.Alarm_dis(self.ui.A_14, 'KLAMPO264')
                self.Alarm_dis(self.ui.A_15, 'KLAMPO265')
                self.Alarm_dis(self.ui.A_16, 'KLAMPO266')

                self.Alarm_dis(self.ui.A_17, 'KLAMPO268')
                self.Alarm_dis(self.ui.A_18, 'KLAMPO269')
                self.Alarm_dis(self.ui.A_19, 'KLAMPO270')
                self.Alarm_dis(self.ui.A_20, 'KLAMPO271')

                self.Alarm_dis(self.ui.A_21, 'KLAMPO272')
                self.Alarm_dis(self.ui.A_22, 'KLAMPO273')
                self.Alarm_dis(self.ui.A_23, 'KLAMPO274')
                self.Alarm_dis(self.ui.A_24, 'KLAMPO295')

                self.Alarm_dis(self.ui.A_25, 'KLAMPO296')
                self.Alarm_dis(self.ui.A_26, 'KLAMPO297')
                self.Alarm_dis(self.ui.A_27, 'KLAMPO298')

                self.Alarm_dis(self.ui.A_28, 'KLAMPO275')
                self.Alarm_dis(self.ui.A_29, 'KLAMPO276')
                self.Alarm_dis(self.ui.A_30, 'KLAMPO277')
                self.Alarm_dis(self.ui.A_31, 'KLAMPO278')

                self.Alarm_dis(self.ui.A_32, 'KLAMPO279')
                self.Alarm_dis(self.ui.A_33, 'KLAMPO280')
                self.Alarm_dis(self.ui.A_34, 'KLAMPO281')
                self.Alarm_dis(self.ui.A_35, 'KLAMPO282')

                self.Alarm_dis(self.ui.A_36, 'KLAMPO283')
                self.Alarm_dis(self.ui.A_37, 'KLAMPO284')
                self.Alarm_dis(self.ui.A_38, 'KLAMPO285')
                self.Alarm_dis(self.ui.A_39, 'KLAMPO286')

                self.Alarm_dis(self.ui.A_40, 'KLAMPO287')
                self.Alarm_dis(self.ui.A_41, 'KLAMPO288')
                self.Alarm_dis(self.ui.A_42, 'KLAMPO289')
                self.Alarm_dis(self.ui.A_43, 'KLAMPO290')

                self.Alarm_dis(self.ui.A_44, 'KLAMPO301')       #alram2
                self.Alarm_dis(self.ui.A_45, 'KLAMPO302')
                self.Alarm_dis(self.ui.A_46, 'KLAMPO303')
                self.Alarm_dis(self.ui.A_47, 'KLAMPO304')

                self.Alarm_dis(self.ui.A_48, 'KLAMPO305')
                self.Alarm_dis(self.ui.A_49, 'KLAMPO306')
                self.Alarm_dis(self.ui.A_50, 'KLAMPO307')
                self.Alarm_dis(self.ui.A_51, 'KLAMPO308')

                self.Alarm_dis(self.ui.A_52, 'KLAMPO309')
                self.Alarm_dis(self.ui.A_53, 'KLAMPO310')
                self.Alarm_dis(self.ui.A_54, 'KLAMPO311')
                self.Alarm_dis(self.ui.A_55, 'KLAMPO312')

                self.Alarm_dis(self.ui.A_56, 'KLAMPO313')
                self.Alarm_dis(self.ui.A_57, 'KLAMPO314')
                self.Alarm_dis(self.ui.A_58, 'KLAMPO315')
                self.Alarm_dis(self.ui.A_59, 'KLAMPO316')

                self.Alarm_dis(self.ui.A_60, 'KLAMPO317')
                self.Alarm_dis(self.ui.A_61, 'KLAMPO318')
                self.Alarm_dis(self.ui.A_62, 'KLAMPO319')
                self.Alarm_dis(self.ui.A_63, 'KLAMPO320')

                self.Alarm_dis(self.ui.A_64, 'KLAMPO321')
                self.Alarm_dis(self.ui.A_65, 'KLAMPO322')
                self.Alarm_dis(self.ui.A_66, 'KLAMPO323')
                self.Alarm_dis(self.ui.A_67, 'KLAMPO324')

                self.Alarm_dis(self.ui.A_68, 'KLAMPO325')
                self.Alarm_dis(self.ui.A_69, 'KLAMPO326')
                self.Alarm_dis(self.ui.A_70, 'KLAMPO327')
                self.Alarm_dis(self.ui.A_71, 'KLAMPO328')

                self.Alarm_dis(self.ui.A_72, 'KLAMPO329')
                self.Alarm_dis(self.ui.A_73, 'KLAMPO330')
                self.Alarm_dis(self.ui.A_74, 'KLAMPO331')
                self.Alarm_dis(self.ui.A_75, 'KLAMPO332')

                self.Alarm_dis(self.ui.A_76, 'KLAMPO333')
                self.Alarm_dis(self.ui.A_77, 'KLAMPO335')
                self.Alarm_dis(self.ui.A_78, 'KLAMPO336')
                self.Alarm_dis(self.ui.A_79, 'KLAMPO337')

                self.Alarm_dis(self.ui.A_80, 'KLAMPO338')
                self.Alarm_dis(self.ui.A_81, 'KLAMPO339')
                self.Alarm_dis(self.ui.A_82, 'KLAMPO340')
                self.Alarm_dis(self.ui.A_83, 'KLAMPO341')

            pass
        pass

    def Alarm_initial(self, ui, on_off):

        if on_off:
            ui.setStyleSheet(self.back_color['red'])
        else:
            ui.setStyleSheet(self.back_color['gray'])

    def Alarm_dis(self, ui, para):
        if self.mem[para]['V'] == 1: # on signal
            if ui.styleSheet() == self.back_color['gray']:
                ui.setStyleSheet(self.back_color['red'])
            else:
                ui.setStyleSheet(self.back_color['gray'])
        else:
            ui.setStyleSheet(self.back_color['gray'])
        pass

    # ======================= Comp ======================================

    def update_comp(self):
        # Aux Feed Water Pump
        self.Comp_on_off(1, self.ui.P_1, 'KLAMPO134')
        self.Comp_on_off(1, self.ui.P_2, 'KLAMPO135')
        self.Comp_on_off(1, self.ui.P_3, 'KLAMPO136')
        # Main Feed Water Pump
        self.Comp_on_off(1, self.ui.P_4, 'KLAMPO241')
        self.Comp_on_off(1, self.ui.P_5, 'KLAMPO242')
        self.Comp_on_off(1, self.ui.P_6, 'KLAMPO243')
        # Condensor pump
        self.Comp_on_off(3, self.ui.P_7, 'KLAMPO181')
        self.Comp_on_off(3, self.ui.P_8, 'KLAMPO182')
        self.Comp_on_off(3, self.ui.P_9, 'KLAMPO183')
        # Charging pump
        self.Comp_on_off(2, self.ui.P_10, 'KLAMPO71')
        self.Comp_on_off(2, self.ui.P_11, 'KLAMPO70')
        self.Comp_on_off(2, self.ui.P_12, 'KLAMPO69')
        # RHR Pump
        self.Comp_on_off(2, self.ui.P_13, 'KLAMPO55')
        # RCP
        self.Comp_on_off(4, self.ui.D_51, 'KLAMPO124')
        self.Comp_on_off(4, self.ui.D_52, 'KLAMPO125')
        self.Comp_on_off(4, self.ui.D_53, 'KLAMPO126')
        # Main steam line
        self.Comp_on_off(6, self.ui.V_37, 'BHV108')
        self.Comp_on_off(6, self.ui.V_38, 'BHV208')
        self.Comp_on_off(6, self.ui.V_39, 'BHV308')
        # Feedwater valve
        self.Comp_on_off(5, self.ui.V_12, 'BFV478')
        self.Comp_on_off(5, self.ui.V_13, 'BFV479')
        self.Comp_on_off(5, self.ui.V_14, 'BFV488')
        self.Comp_on_off(5, self.ui.V_15, 'BFV489')
        self.Comp_on_off(5, self.ui.V_16, 'BFV498')
        self.Comp_on_off(5, self.ui.V_17, 'BFV499')
        # AUX FEED VALVE
        self.Comp_on_off(7, self.ui.V_48, 'WAFWS1')
        self.Comp_on_off(7, self.ui.V_49, 'WAFWS2')
        self.Comp_on_off(7, self.ui.V_50, 'WAFWS3')
        # VALVE
        self.Comp_on_off(5, self.ui.V_1, 'BHV22')
        self.Comp_on_off(6, self.ui.V_40, 'BHSV')
        self.Comp_on_off(6, self.ui.V_41, 'BHSV')
        self.Comp_on_off(6, self.ui.V_42, 'BHSV')
        self.Comp_on_off(6, self.ui.V_43, 'BHSV')
        self.Comp_on_off(6, self.ui.V_44, 'BHTV')
        self.Comp_on_off(6, self.ui.V_45, 'BHTV')
        self.Comp_on_off(6, self.ui.V_46, 'BHTV')
        self.Comp_on_off(6, self.ui.V_47, 'BHTV')
        self.Comp_on_off(6, self.ui.V_36, 'BHV40')
        self.Comp_on_off(6, self.ui.V_35, 'BHV201')
        self.Comp_on_off(6, self.ui.V_51, 'BHV302')
        self.Comp_on_off(6, self.ui.V_52, 'BHV301')
        self.Comp_on_off(6, self.ui.V_19, 'BHV301')

        self.Comp_on_off(5, self.ui.V_19, 'BHV8')
        self.Comp_on_off(5, self.ui.V_5, 'BHV1')
        self.Comp_on_off(5, self.ui.V_6, 'BHV1')
        self.Comp_on_off(5, self.ui.V_7, 'BHV1')
        self.Comp_on_off(5, self.ui.V_8, 'BLV615')
        self.Comp_on_off(5, self.ui.V_9, 'BLV616')
        self.Comp_on_off(5, self.ui.V_11, 'BLV459')

        self.Comp_on_off(5, self.ui.V_2, 'BHV101')
        self.Comp_on_off(5, self.ui.V_3, 'BHV102')
        self.Comp_on_off(5, self.ui.V_10, 'BHV39')

        self.Comp_on_off(5, self.ui.V_24, 'BLTV')
        self.Comp_on_off(5, self.ui.V_23, 'BLTV')
        self.Comp_on_off(5, self.ui.V_27, 'BLTV')
        self.Comp_on_off(5, self.ui.V_28, 'BLTV')
        self.Comp_on_off(5, self.ui.V_31, 'BLTV')
        self.Comp_on_off(5, self.ui.V_32, 'BLTV')

        self.Comp_on_off(5, self.ui.V_25, 'BLSV')
        self.Comp_on_off(5, self.ui.V_26, 'BLSV')
        self.Comp_on_off(5, self.ui.V_30, 'BLSV')
        self.Comp_on_off(5, self.ui.V_22, 'BLSV')
        self.Comp_on_off(5, self.ui.V_29, 'BLSV')
        self.Comp_on_off(5, self.ui.V_33, 'BLSV')

        self.Comp_on_off(5, self.ui.V_19, 'BFV13')
        self.Comp_on_off(5, self.ui.V_18, 'BLV177')

        pass

    def Comp_on_off(self, ui_type, ui_pump, para):
        if ui_type == 1:
            if self.mem[para]['V'] == 1:
                ui_pump.setStyleSheet(self.back_img['P_1_ON'])
            else:
                ui_pump.setStyleSheet(self.back_img['P_1_OFF'])
        elif ui_type == 2:
            if self.mem[para]['V'] == 1:
                ui_pump.setStyleSheet(self.back_img['P_2_ON'])
            else:
                ui_pump.setStyleSheet(self.back_img['P_2_OFF'])
        elif ui_type == 3:
            if self.mem[para]['V'] == 1:
                ui_pump.setStyleSheet(self.back_img['P_3_ON'])
            else:
                ui_pump.setStyleSheet(self.back_img['P_3_OFF'])
        elif ui_type == 4:
            if self.mem[para]['V'] == 1:
                ui_pump.setStyleSheet(self.back_color['red'])
            else:
                ui_pump.setStyleSheet(self.back_color['gray'])
        elif ui_type == 5:
            if self.mem[para]['V'] == 1:
                ui_pump.setStyleSheet(self.back_img['V_1_OPEN'])
            elif self.mem[para]['V'] == 0:
                ui_pump.setStyleSheet(self.back_img['V_1_CLOSE'])
            else:
                ui_pump.setStyleSheet(self.back_img['V_1_HALF'])
        elif ui_type == 6:
            if self.mem[para]['V'] == 1:
                ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
            elif self.mem[para]['V'] == 0:
                ui_pump.setStyleSheet(self.back_img['V_2_CLOSE'])
            else:
                ui_pump.setStyleSheet(self.back_img['V_2_HALF'])
        elif ui_type == 7:
            if para == 'WAFWS1':
                if self.mem['KLAMPO134']['V'] == 1:
                    if self.mem[para]['V'] == 25:
                        ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                    elif self.mem[para]['V'] == 0:
                        ui_pump.setStyleSheet(self.back_img['V_2_CLOSE'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                    else:
                        ui_pump.setStyleSheet(self.back_img['V_2_HALF'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                else:
                    ui_pump.setStyleSheet(self.back_img['V_2_CLOSE'])
                    self.ui.V_20.setStyleSheet(self.back_img['V_1_CLOSE'])
                    self.ui.V_21.setStyleSheet(self.back_img['V_1_CLOSE'])
            elif para == 'WAFWS2':
                if self.mem['KLAMPO135']['V'] == 1:
                    if self.mem[para]['V'] == 25:
                        ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                    elif self.mem[para]['V'] == 0:
                        ui_pump.setStyleSheet(self.back_img['V_2_CLOSE'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                    else:
                        ui_pump.setStyleSheet(self.back_img['V_2_HALF'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                else:
                    ui_pump.setStyleSheet(self.back_img['V_2_CLOSE'])
                    self.ui.V_20.setStyleSheet(self.back_img['V_1_CLOSE'])
                    self.ui.V_21.setStyleSheet(self.back_img['V_1_CLOSE'])
            elif para == 'WAFWS3':
                if self.mem['KLAMPO136']['V'] == 1:
                    if self.mem[para]['V'] == 25:
                        ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                    elif self.mem[para]['V'] == 0:
                        ui_pump.setStyleSheet(self.back_img['V_2_CLOSE'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                    else:
                        ui_pump.setStyleSheet(self.back_img['V_2_HALF'])
                        self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                        self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                else:
                    ui_pump.setStyleSheet(self.back_img['V_2_CLOSE'])
                    self.ui.V_20.setStyleSheet(self.back_img['V_2_CLOSE'])
                    self.ui.V_21.setStyleSheet(self.back_img['V_2_CLOSE'])
            else:
                pass
        else:
            pass

    # ======================= CSF ======================================

    def update_CSF(self):

        # test module CSF
        if self.CSF_test_mode:
            if self.CSF_upcont >= 5:
                self.CSF_upcont = 1
                self.CSF_test_mode = False

            self.CSF_switch('React', self.CSF_upcont)
            self.CSF_switch('Coreheat', self.CSF_upcont)
            self.CSF_switch('RCSheat', self.CSF_upcont)
            self.CSF_switch('RCSpressure', self.CSF_upcont)
            self.CSF_switch('CTMTp_t', self.CSF_upcont)
            self.CSF_switch('RCS_Inven', self.CSF_upcont)

            self.CSF_upcont += 1

        else:
            # logic hear!!
            try:
                self.CSF_switch('Coreheat', self.CSF_CORE_HEAT())
                self.CSF_switch('RCSheat', self.CSF_RCS_Heat())
                self.CSF_switch('CTMTp_t', self.CSF_CTMT())
                self.CSF_switch('React', self.CSF_REA())
                self.CSF_switch('RCS_Inven', self.CSF_RCS_Inven())
                self.CSF_switch('RCSpressure', self.CSF_RCS_integrate())
            except:
                pass
                # print('err')

    def CSF_switch(self, safety_function, level):

        if safety_function == 'React':
            if level == 0:
                self.ui.CSF_1_1.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_2.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_3.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_4.setStyleSheet(self.back_color['gray'])
            elif level == 1:
                self.ui.CSF_1_1.setStyleSheet(self.back_color['green'])
                self.ui.CSF_1_2.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_3.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_4.setStyleSheet(self.back_color['gray'])
            elif level == 2:
                self.ui.CSF_1_1.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_2.setStyleSheet(self.back_color['yellow'])
                self.ui.CSF_1_3.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_4.setStyleSheet(self.back_color['gray'])
            elif level == 3:
                self.ui.CSF_1_1.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_2.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_3.setStyleSheet(self.back_color['orange'])
                self.ui.CSF_1_4.setStyleSheet(self.back_color['gray'])
            elif level == 4:
                self.ui.CSF_1_1.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_2.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_3.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_4.setStyleSheet(self.back_color['red'])
            else:
                pass
        elif safety_function == 'Coreheat':
            if level == 0:
                self.ui.CSF_1_5.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_6.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_7.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_8.setStyleSheet(self.back_color['gray'])
            elif level == 1:
                self.ui.CSF_1_5.setStyleSheet(self.back_color['green'])
                self.ui.CSF_1_6.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_7.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_8.setStyleSheet(self.back_color['gray'])
            elif level == 2:
                self.ui.CSF_1_5.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_6.setStyleSheet(self.back_color['yellow'])
                self.ui.CSF_1_7.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_8.setStyleSheet(self.back_color['gray'])
            elif level == 3:
                self.ui.CSF_1_5.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_6.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_7.setStyleSheet(self.back_color['orange'])
                self.ui.CSF_1_8.setStyleSheet(self.back_color['gray'])
            elif level == 4:
                self.ui.CSF_1_5.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_6.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_7.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_8.setStyleSheet(self.back_color['red'])
            else:
                pass
        elif safety_function == 'RCSheat':
            if level == 0:
                self.ui.CSF_1_9.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_10.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_11.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_12.setStyleSheet(self.back_color['gray'])
            elif level == 1:
                self.ui.CSF_1_9.setStyleSheet(self.back_color['green'])
                self.ui.CSF_1_10.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_11.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_12.setStyleSheet(self.back_color['gray'])
            elif level == 2:
                self.ui.CSF_1_9.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_10.setStyleSheet(self.back_color['yellow'])
                self.ui.CSF_1_11.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_12.setStyleSheet(self.back_color['gray'])
            elif level == 3:
                self.ui.CSF_1_9.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_10.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_11.setStyleSheet(self.back_color['orange'])
                self.ui.CSF_1_12.setStyleSheet(self.back_color['gray'])
            elif level == 4:
                self.ui.CSF_1_9.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_10.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_11.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_12.setStyleSheet(self.back_color['red'])
            else:
                pass
        elif safety_function == 'RCSpressure':
            if level == 0:
                self.ui.CSF_1_13.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_14.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_15.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_16.setStyleSheet(self.back_color['gray'])
            elif level == 1:
                self.ui.CSF_1_13.setStyleSheet(self.back_color['green'])
                self.ui.CSF_1_14.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_15.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_16.setStyleSheet(self.back_color['gray'])
            elif level == 2:
                self.ui.CSF_1_13.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_14.setStyleSheet(self.back_color['yellow'])
                self.ui.CSF_1_15.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_16.setStyleSheet(self.back_color['gray'])
            elif level == 3:
                self.ui.CSF_1_13.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_14.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_15.setStyleSheet(self.back_color['orange'])
                self.ui.CSF_1_16.setStyleSheet(self.back_color['gray'])
            elif level == 4:
                self.ui.CSF_1_13.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_14.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_15.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_16.setStyleSheet(self.back_color['red'])
            else:
                pass
        elif safety_function == 'CTMTp_t':
            if level == 0:
                self.ui.CSF_1_17.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_18.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_19.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_20.setStyleSheet(self.back_color['gray'])
            elif level == 1:
                self.ui.CSF_1_17.setStyleSheet(self.back_color['green'])
                self.ui.CSF_1_18.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_19.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_20.setStyleSheet(self.back_color['gray'])
            elif level == 2:
                self.ui.CSF_1_17.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_18.setStyleSheet(self.back_color['yellow'])
                self.ui.CSF_1_19.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_20.setStyleSheet(self.back_color['gray'])
            elif level == 3:
                self.ui.CSF_1_17.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_18.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_19.setStyleSheet(self.back_color['orange'])
                self.ui.CSF_1_20.setStyleSheet(self.back_color['gray'])
            elif level == 4:
                self.ui.CSF_1_17.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_18.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_19.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_20.setStyleSheet(self.back_color['red'])
            else:
                pass
        elif safety_function == 'RCS_Inven':
            if level == 0:
                self.ui.CSF_1_21.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_22.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_23.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_24.setStyleSheet(self.back_color['gray'])
            elif level == 1:
                self.ui.CSF_1_21.setStyleSheet(self.back_color['green'])
                self.ui.CSF_1_22.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_23.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_24.setStyleSheet(self.back_color['gray'])
            elif level == 2:
                self.ui.CSF_1_21.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_22.setStyleSheet(self.back_color['yellow'])
                self.ui.CSF_1_23.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_24.setStyleSheet(self.back_color['gray'])
            elif level == 3:
                self.ui.CSF_1_21.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_22.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_23.setStyleSheet(self.back_color['orange'])
                self.ui.CSF_1_24.setStyleSheet(self.back_color['gray'])
            elif level == 4:
                self.ui.CSF_1_21.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_22.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_23.setStyleSheet(self.back_color['gray'])
                self.ui.CSF_1_24.setStyleSheet(self.back_color['red'])
            else:
                pass
        else:
            pass

    def CSF_CORE_HEAT(self):

        # self.mem['QPROLD']['V'] * 100
        if len(self.mem['KCNTOMS']['L']) >= 1:
            ## CSF 감시 가능 상태

            HLT1_Past = self.mem['UHOLEG1']['L'][-2]  # UHOLEG1 Column 첫번째 행
            HLT2_Past = self.mem['UHOLEG2']['L'][-2]  # UHOLEG2 Column 첫번째 행
            HLT3_Past = self.mem['UHOLEG3']['L'][-2]  # UHOLEG3 Column 첫번째 행
            HLT1 = self.mem['UHOLEG1']['V']  # UHOLEG1 Column 111 - 4
            HLT2 = self.mem['UHOLEG2']['V']  # UHOLEG2 Column 112 - 5
            HLT3 = self.mem['UHOLEG3']['V']  # UHOLEG3 Column 113 - 6
            PRZ = self.mem['ZINST58']['V']  # ZINST58 Column 132 - 9
            EXCT = self.mem['ZINST46']['V']  # ZINST46 Column 167 - 22

            if EXCT < 649:
                if HLT1_Past - HLT1 <= 11.1 or HLT2_Past - HLT2 <= 11.1 or HLT3_Past - HLT3 <= 11.1:  # 0냉각률
                    if (
                            0.0123 * HLT1 ** 2 - 0.4899 * HLT1 + 34.291 - PRZ > 0 and 0.0058 * HLT1 ** 2 - 2.114 * HLT1 + 211.27 - PRZ < 0) and (
                            0.0123 * HLT2 ** 2 - 0.4899 * HLT2 + 34.291 - PRZ > 0 and 0.0058 * HLT2 ** 2 - 2.114 * HLT2 + 211.27 - PRZ < 0) and (
                            0.0123 * HLT3 ** 2 - 0.4899 * HLT3 + 34.291 - PRZ > 0 and 0.0058 * HLT3 ** 2 - 2.114 * HLT3 + 211.27 - PRZ < 0):
                        CC = 1
                    elif EXCT < 371:
                        CC = 2
                    else:
                        CC = 3
                elif 11.1 < HLT1_Past - HLT1 <= 22.2 or 11.1 < HLT2_Past - HLT2 <= 22.2 or 11.1 < HLT3_Past - HLT3 <= 22.2:  # 11.1냉각률
                    if (
                            0.0125 * HLT1 ** 2 - 0.5714 * HLT1 + 40.475 - PRZ > 0 and 0.0058 * HLT1 ** 2 - 2.114 * HLT1 + 211.27 - PRZ < 0) and (
                            0.0125 * HLT2 ** 2 - 0.5714 * HLT2 + 40.475 - PRZ > 0 and 0.0058 * HLT2 ** 2 - 2.114 * HLT2 + 211.27 - PRZ < 0) and (
                            0.0125 * HLT3 ** 2 - 0.5714 * HLT3 + 40.475 - PRZ > 0 and 0.0058 * HLT3 ** 2 - 2.114 * HLT3 + 211.27 - PRZ < 0):
                        CC = 1
                    elif EXCT < 371:
                        CC = 2
                    else:
                        CC = 3
                elif 22.2 < HLT1_Past - HLT1 <= 33.3 or 22.2 < HLT2_Past - HLT2 <= 33.3 or 22.2 < HLT3_Past - HLT3 <= 33.3:  # 22.2냉각률
                    if (
                            0.0129 * HLT1 ** 2 - 0.6579 * HLT1 + 44.421 - PRZ > 0 and 0.0058 * HLT1 ** 2 - 2.114 * HLT1 + 211.27 - PRZ < 0) and (
                            0.0129 * HLT2 ** 2 - 0.6579 * HLT2 + 44.421 - PRZ > 0 and 0.0058 * HLT2 ** 2 - 2.114 * HLT2 + 211.27 - PRZ < 0) and (
                            0.0129 * HLT3 ** 2 - 0.6579 * HLT3 + 44.421 - PRZ > 0 and 0.0058 * HLT3 ** 2 - 2.114 * HLT3 + 211.27 - PRZ < 0):
                        CC = 1
                    elif EXCT < 371:
                        CC = 2
                    else:
                        CC = 3
                elif 33.3 < HLT1_Past - HLT1 <= 55.5 or 33.3 < HLT2_Past - HLT2 <= 55.5 or 33.3 < HLT3_Past - HLT3 <= 55.5:  # 33.3냉각률
                    if (
                            0.0131 * HLT1 ** 2 - 0.7006 * HLT1 + 47.231 - PRZ > 0 and 0.0058 * HLT1 ** 2 - 2.114 * HLT1 + 211.27 - PRZ < 0) and (
                            0.0131 * HLT2 ** 2 - 0.7006 * HLT2 + 47.231 - PRZ > 0 and 0.0058 * HLT2 ** 2 - 2.114 * HLT2 + 211.27 - PRZ < 0) and (
                            0.0131 * HLT3 ** 2 - 0.7006 * HLT3 + 47.231 - PRZ > 0 and 0.0058 * HLT3 ** 2 - 2.114 * HLT3 + 211.27 - PRZ < 0):
                        CC = 1
                    elif EXCT < 371:
                        CC = 2
                    else:
                        CC = 3
                elif 55.5 < HLT1_Past - HLT1 or 55.5 < HLT2_Past - HLT2 or 55.5 < HLT3_Past - HLT3:  # 55.5냉각률
                    if (
                            0.013 * HLT1 ** 2 - 0.7178 * HLT1 + 50.03 - PRZ > 0 and 0.0058 * HLT1 ** 2 - 2.114 * HLT1 + 211.27 - PRZ < 0) and (
                            0.013 * HLT2 ** 2 - 0.7178 * HLT2 + 50.03 - PRZ > 0 and 0.0058 * HLT2 ** 2 - 2.114 * HLT2 + 211.27 - PRZ < 0) and (
                            0.013 * HLT3 ** 2 - 0.7178 * HLT3 + 50.03 - PRZ > 0 and 0.0058 * HLT3 ** 2 - 2.114 * HLT3 + 211.27 - PRZ < 0):
                        CC = 1
                    elif EXCT < 371:
                        CC = 2
                    else:
                        CC = 3
            else:
                CC = 4
            return CC
        else:
            # initial
            return 0

    def CSF_RCS_integrate(self):

        if len(self.mem['KCNTOMS']['L']) >= 1:

            CLT1_Past = self.mem['UCOLEG1']['L'][-2]  # UCOLEG1 Column 첫번째 행 108 - 1
            CLT2_Past = self.mem['UCOLEG2']['L'][-2]  # UCOLEG2 Column 첫번째 행 109 - 2
            CLT3_Past = self.mem['UCOLEG3']['L'][-2]  # UCOLEG3 Column 첫번째 행 110 - 3
            CLT1 = self.mem['UCOLEG1']['V']  # UCOLEG1 Column
            CLT2 = self.mem['UCOLEG2']['V']  # UCOLEG2 Column
            CLT3 = self.mem['UCOLEG3']['V']  # UCOLEG3 Column
            PRZ = self.mem['ZINST58']['V']  # ZINST58 Column 132 - 9
            minCLT = min(CLT1, CLT2, CLT3)

            if CLT1_Past - CLT1 < 55.5 and CLT2_Past - CLT2 < 55.5 and CLT3_Past - CLT3 < 55.5:
                if CLT1 > 135 and CLT2 > 135 and CLT3 > 135:
                    RIF = 1
                else:
                    if 0 <= minCLT and minCLT <= 48.91:
                        if PRZ <= 34.1:
                            RIF = 1
                    elif 48.91 < minCLT and minCLT <= 65.56:
                        if PRZ <= 34.81:
                            RIF = 1
                        elif CLT1 >= 115 and CLT2 >= 115 and CLT3 >= 115:
                            RIF = 2
                        else:
                            RIF = 3
                    elif 65.56 < minCLT and minCLT <= 93.33:
                        if PRZ <= 37.27:
                            RIF = 1
                        elif CLT1 >= 115 and CLT2 >= 115 and CLT3 >= 115:
                            RIF = 2
                        else:
                            RIF = 3
                    elif 93.33 < minCLT and minCLT <= 193.28:
                        if PRZ <= 42.90:
                            RIF = 1
                        elif CLT1 >= 115 and CLT2 >= 115 and CLT3 >= 115:
                            RIF = 2
                        else:
                            RIF = 3
                    elif 193.28 < minCLT and minCLT <= 237.80:
                        if PRZ <= 165.29:
                            RIF = 1
                        elif CLT1 >= 115 and CLT2 >= 115 and CLT3 >= 115:
                            RIF = 2
                        else:
                            RIF = 3
                    elif minCLT > 237.80:
                        if PRZ <= 165.29:
                            RIF = 1
                        elif CLT1 >= 115 and CLT2 >= 115 and CLT3 >= 115:
                            RIF = 2
                        else:
                            RIF = 3
            elif CLT1 < 110 and CLT2 < 110 and CLT3 < 110:
                if 7.175 * CLT1 - 645.75 - PRZ > 0 and 7.175 * CLT2 - 645.75 - PRZ > 0 and 7.175 * CLT3 - 645.75 - PRZ > 0:
                    if CLT1 > 115 and CLT2 > 115 and CLT3 > 115:
                        if CLT1 > 131 and CLT2 > 131 and CLT3 > 131:
                            RIF = 1
                        else:
                            RIF = 2
                    else:
                        RIF = 3
                else:
                    RIF = 4
            elif CLT1 >= 110 or CLT2 >= 110 or CLT3 >= 110:
                if 7.14 * CLT1 - 641.9 - PRZ > 0 and 7.14 * CLT2 - 641.9 - PRZ > 0 and 7.14 * CLT3 - 641.9 - PRZ > 0:
                    if CLT1 > 115 and CLT2 > 115 and CLT3 > 115:
                        if CLT1 > 131 and CLT2 > 131 and CLT3 > 131:
                            RIF = 1
                        else:
                            RIF = 2
                    else:
                        RIF = 3
                else:
                    RIF = 4

            return RIF
        else:
            return 0

    def CSF_CTMT(self):

        if len(self.mem['KCNTOMS']['L']) >= 1:
            CMIP_ = self.mem['ZINST26']['V']  # ZINST26 Column 8
            CMSUMPL_ = self.mem['ZINST17']['V']  # ZINST17 Column 단위M 0.xx형식 19
            CMRAD_ = self.mem['ZINST22']['V']  # ZINST22 Column 7
            CMSPRAY_ = self.mem['KCTMTSP']['V'] # KCTMTSP Column 47
            if CMIP_ < 4.2:
                if CMIP_ < 1.55:
                    if CMSUMPL_ < 0.36:  # 0.XX형식으로 변환 (%느낌)
                        if CMRAD_ < 10e4:
                            C_I_F = 1
                        else:
                            C_I_F = 2
                    else:
                        C_I_F = 3
                elif CMSPRAY_ == 1:
                    C_I_F = 2
                else:
                    C_I_F = 3
            else:
                C_I_F = 4
            return C_I_F
        else:
            return 0

    def CSF_REA(self):

        if len(self.mem['KCNTOMS']['L']) >= 1:
            PR = self.mem['ZINST1']['V']  # ZINST1 Column 출력영역 검출기 단위:% 163
            IR = self.mem['ZINST2']['V']  # ZINST2 Column 중간영역 검출기 지시치:A 165
            IRA = self.mem['FSRMDPM']['V']  # FSRMDPM Column 중간영역 기동율 단위:DPM 161
            SR = self.mem['ZINST3']['V']  # ZINST3 Column 선원영역 기동율 단위:CPS 166
            Trip = self.mem['KLAMPO9']['V']  # ZINST3 Column 선원영역 기동율 단위:CPS 166
            if Trip == 0:
                SF = 1
            else:
                if PR < 5:
                    if IR <= 0:
                        if IRA < 10e-9:
                            if SR <= 0:
                                SF = 1
                            else:
                                SF = 2
                        elif IR <= -0.2:
                            SF = 1
                        else:
                            SF = 2
                    else:
                        SF = 3
                else:
                    SF = 4
            return SF
        else:
            return 0

    def CSF_RCS_Inven(self):

        if len(self.mem['KCNTOMS']['L']) >= 1:
            PRZL = self.mem['ZPRZNO']['V']  # ZPRZNO Column PZR Water Lvl(0.0-1.0) 153 - 16
            if PRZL < 0.92:
                if PRZL > 0.17:
                    if 0.50 < PRZL and 0.60 > PRZL:
                        RInf = 1
                    else:
                        RInf = 2
                else:
                    RInf = 2
            else:
                RInf = 2
            return RInf
        else:
            return 0

    def CSF_RCS_Heat(self):

        if len(self.mem['KCNTOMS']['L']) >= 1:
            SG1NRL = self.mem['ZINST78']['V']  # ZINST78 Column SG1 Lvl NR 13
            SG2NRL = self.mem['ZINST77']['V']  # ZINST77 Column SG2 Lv1 NR 14
            SG3NRL = self.mem['ZINST76']['V']  # ZINST76 Column SG3 Lv1 NR 15
            FtoSG1 = 1000
            FtoSG2 = 1000
            FtoSG3 = 1000
            AFtoSG1 = 33
            AFtoSG2 = 33
            AFtoSG3 = 33
            SG1P = self.mem['ZINST75']['V']  # ZINST75 Column S/G1 Pressure 12
            SG2P = self.mem['ZINST74']['V']  # ZINST74 Column S/G2 Pressure 11
            SG3P = self.mem['ZINST73']['V']  # ZINST73 Column S/G3 Pressure 10
            CMIP = self.mem['ZINST26']['V']  # ZINST26 Column 128 - 8
            CMRAD = self.mem['ZINST22']['V']  # ZINST22 Column 126 - 7
            if CMIP <= 0.35 and CMRAD <= 10e8:
                if SG1NRL >= 7 or SG2NRL >= 7 or SG3NRL >= 7:
                    if SG1P < 86 and SG2P < 86 and SG3P < 86:
                        if SG1NRL < 78 and SG2NRL < 78 and SG3NRL < 78:
                            if SG1P < 83.3 and SG2P < 83.3 and SG3P < 83.3:
                                if SG1NRL >= 7 and SG2NRL >= 7 and SG3NRL >= 7:
                                    HS = 1
                                else:
                                    HS = 2
                            else:
                                HS = 2
                        else:
                            HS = 2
                    else:
                        HS = 2
                elif FtoSG1 + AFtoSG1 > 32.5 or FtoSG2 + AFtoSG2 > 32.5 or FtoSG3 + AFtoSG3 > 32.5:
                    if SG1P < 86 and SG2P < 86 and SG3P < 86:
                        if SG1NRL < 78 and SG2NRL < 78 and SG3NRL < 78:
                            if SG1P < 83.3 and SG2P < 83.3 and SG3P < 83.3:
                                if SG1NRL >= 7 and SG2NRL >= 7 and SG3NRL >= 7:
                                    HS = 1
                                else:
                                    HS = 2
                            else:
                                HS = 2
                        else:
                            HS = 2
                    else:
                        HS = 2
                else:
                    HS = 4
            else:
                if SG1NRL >= 19 or SG2NRL >= 19 or SG3NRL >= 19:
                    if SG1P < 86 and SG2P < 86 and SG3P < 86:
                        if SG1NRL < 78 and SG2NRL < 78 and SG3NRL < 78:
                            if SG1P < 83.3 and SG2P < 83.3 and SG3P < 83.3:
                                if SG1NRL >= 7 and SG2NRL >= 7 and SG3NRL >= 7:
                                    HS = 1
                                else:
                                    HS = 2
                            else:
                                HS = 2
                        else:
                            HS = 2
                    else:
                        HS = 2
                elif FtoSG1 + AFtoSG1 > 32.5 or FtoSG2 + AFtoSG2 > 32.5 or FtoSG3 + AFtoSG3 > 32.5:
                    if SG1P < 86 and SG2P < 86 and SG3P < 86:
                        if SG1NRL < 78 and SG2NRL < 78 and SG3NRL < 78:
                            if SG1P < 83.3 and SG2P < 83.3 and SG3P < 83.3:
                                if SG1NRL >= 19 and SG2NRL >= 19 and SG3NRL >= 19:
                                    HS = 1
                                else:
                                    HS = 2
                            else:
                                HS = 2
                        else:
                            HS = 2
                    else:
                        HS = 2
                else:
                    HS = 4
            return HS
        else:
            return 0

    # ======================= Autonomous DIS==============================

    def run_AUTO(self):
        if self.mem['KCNTOMS']['V'] < 4:
            self.ui.Strategy_out.clear()
            self.ui.Auto_list.clear()
            self.AUTO_State = {
                'Histoty': {}   # {Start_time: '', Content: ''
            }
            self.Auto_Alarm_Click_Auto() # 실행 초기 입력

        # Autonomous state alram
        self.Auto_Alarm_dis()
        self.Autonomous_operation_strategy()
        self.Autonomous_controller()

    def Auto_Alarm_dis(self):
        if self.Auto_mem['Auto_state']:     # True
            self.ui.pushButton_2.setStyleSheet(self.back_color['gray']) # man dis
            self.ui.pushButton_4.setStyleSheet(self.back_color['gray']) # man on botton
            self.ui.pushButton_5.setStyleSheet(self.back_color['green'])  # man off botton

            self.ui.pushButton.setStyleSheet(self.back_color['red'])    #auto_dis
            self.ui.pushButton_6.setStyleSheet(self.back_color['red'])  #auto_on
            self.ui.pushButton_7.setStyleSheet(self.back_color['gray']) #auto_off

        elif self.Auto_mem['Man_state']:     # True
            self.ui.pushButton_2.setStyleSheet(self.back_color['red'])  # man dis
            self.ui.pushButton_4.setStyleSheet(self.back_color['red'])  # man on botton
            self.ui.pushButton_5.setStyleSheet(self.back_color['gray'])  # man off botton

            self.ui.pushButton.setStyleSheet(self.back_color['gray'])  # auto_dis
            self.ui.pushButton_6.setStyleSheet(self.back_color['gray'])  # auto_on
            self.ui.pushButton_7.setStyleSheet(self.back_color['green'])  # auto_off
        else:
            pass
        if self.Auto_mem['Man_require']:     # True
            if self.ui.pushButton_3.styleSheet() == self.back_color['red']:
                self.ui.pushButton_3.setStyleSheet(self.back_color['gray'])
            else:
                self.ui.pushButton_3.setStyleSheet(self.back_color['red'])
        else:
            self.ui.pushButton_3.setStyleSheet(self.back_color['gray'])

    def Auto_Alarm_Click_Man(self):
        self.Auto_mem['Auto_state'] = False
        self.Auto_mem['Man_state'] = True
        self.ui.Strategy_out.append('{} Manual Operaion'.format(self.Call_CNS_time[0]))

    def Auto_Alarm_Click_Auto(self):
        self.Auto_mem['Auto_state'] = True
        self.Auto_mem['Man_state'] = False
        self.ui.Strategy_out.append('{} Autonomous Operaion'.format(self.Call_CNS_time[0]))

    def Autonomous_controller(self):
        if self.mem['KLAMPO9']['V'] == 1: self.add_list_signal('Reactor trip')
        if self.mem['KLAMPO6']['V'] == 1: self.add_list_signal('SI valve open')
        if self.mem['KLAMPO4']['V'] == 1: self.add_list_signal('Containment ISO')
        if self.mem['KLAMPO2']['V'] == 1: self.add_list_signal('Feedwater ISO')
        if self.mem['KLAMPO3']['V'] == 1: self.add_list_signal('Main steam line ISO')
        if self.mem['KLAMPO134']['V'] == 1: self.add_list_signal('Aux feed pump 1 start')
        if self.mem['KLAMPO135']['V'] == 1: self.add_list_signal('Aux feed pump 2 start')
        if self.mem['KLAMPO136']['V'] == 1: self.add_list_signal('Aux feed pump 3 start')

        if self.mem['KLAMPO70']['V'] == 1: self.add_list_signal('Charging pump 2 start')
        if self.mem['KLAMPO124']['V'] == 0: self.add_list_signal('RCP 1 stop')
        if self.mem['KLAMPO125']['V'] == 0: self.add_list_signal('RCP 2 stop')
        if self.mem['KLAMPO126']['V'] == 0: self.add_list_signal('RCP 3 stop')

        pass

    def add_list_signal(self, content):
        if len(self.ui.Auto_list.findItems('{}'.format(content), QtCore.Qt.MatchContains)) == 0:
            self.ui.Auto_list.addItem('{} {}'.format(self.Call_CNS_time[0], content))

    def Autonomous_operation_strategy(self):
        # =========================================================================
        # 운전 전략을 보여주는 부분
        if self.Auto_mem['Auto_state']:
            self.Auto_mem['Current_op'] = 'LSTM-based Operation'
        else:
            self.Auto_mem['Current_op'] = 'Manual Operation'

        self.ui.Current_op.setText('{}'.format(self.Auto_mem['Current_op']))

    # ======================= Monitorin DIS ==============================

    def run_TSMS(self):
        if self.mem['KCNTOMS']['V'] < 4:
            self.ui.Performace_Mn.clear()
            self.TSMS_State = {}
        self.Monitoring()

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
            if not 'LCO 3.4.4' in self.TSMS_State.keys():
                self.TSMS_State['LCO 3.4.4'] = {'Start_time': self.Call_CNS_time[1],
                                                'End_time': self.Call_CNS_time[1]+24000}
                end_time = self.calculate_time(self.Call_CNS_time[1]+24000)
                self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.4.4\tDissatisfaction'.format(self.Call_CNS_time[0],
                                                                                         end_time))
        # LCO 3.4.1
        if not 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
            if not'LCO 3.4.1' in self.TSMS_State.keys():
                self.TSMS_State['LCO 3.4.1'] = {'Start_time': self.Call_CNS_time[1],
                                                'End_time': self.Call_CNS_time[1]+7200}
                end_time = self.calculate_time(self.Call_CNS_time[1]+7200)
                self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.4.1\tDissatisfaction'.format(self.Call_CNS_time[0],
                                                                                          end_time))
        # LCO 3.4.3
        if self.predict_SVM(self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']) != 1:
            if not'LCO 3.4.3' in self.TSMS_State.keys():
                self.TSMS_State['LCO 3.4.3'] = {'Start_time': self.Call_CNS_time[1],
                                                'End_time': self.Call_CNS_time[1]+1800}
                end_time = self.calculate_time(self.Call_CNS_time[1]+1800)
                self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.4.3\tDissatisfaction'.format(self.Call_CNS_time[0],
                                                                                          end_time))

        # LCO 3.1.1
        current_SDM = self.Calculator_SDM()
        if current_SDM < 1770:
            if not 'LCO 3.1.1' in self.TSMS_State.keys():
                self.TSMS_State['LCO 3.1.1'] = {'Start_time': self.Call_CNS_time[1],
                                                'End_time': self.Call_CNS_time[1] + 900}
                end_time = self.calculate_time(self.Call_CNS_time[1] + 900)
                self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.1.1\tDissatisfaction'.format(self.Call_CNS_time[0],
                                                                                          end_time))

    def Monitoring_Operation_Mode(self):
        if self.mem['CRETIV']['V'] >= 0:
            if self.mem['ZINST1']['V'] > 5:
                mode = 1
            elif self.mem['ZINST1']['V'] <= 5:
                mode = 2
        elif self.mem['CRETIV']['V'] < 0:
            if self.mem['UCOLEG1']['V'] >= 177:
                mode = 3
            elif 93 < self.mem['UCOLEG1']['V'] < 177:
                mode = 4
            elif self.mem['UCOLEG1']['V'] <= 93:
                mode = 5
        else:
            mode = 6
        return mode

    def TSMS_LCO_info(self, item):
        LCO_name = item.text().split('\t')[1]
        if LCO_name == 'LCO 3.4.4':
            currnet_mode = self.Monitoring_Operation_Mode()
            cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
            cont += '=' * 50 + '\n'
            cont += 'Follow up action : Enter Mode 3\n'
            cont += '=' * 50 + '\n'
            cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
            cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
                                              self.calculate_time(self.Call_CNS_time[1]),
                                              self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
            cont += '=' * 50 + '\n'
            if currnet_mode == 3:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Success\n'
            elif currnet_mode == 1 or currnet_mode == 2:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Ongoing\n'
            cont += '=' * 50 + '\n'
            QMessageBox.information(self, "LCO 정보", cont)

        elif LCO_name == 'LCO 3.4.1':
            currnet_mode = self.Monitoring_Operation_Mode()
            cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
            cont += '=' * 50 + '\n'
            cont += 'Follow up action :\n'
            cont += '  - 154.7 < RCS Pressure < 161.6 [kg/cm²]\n'
            cont += '  - 286.7 < RCS Cold-leg Temp < 293.3 [℃]\n'
            cont += '=' * 50 + '\n'
            cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
            cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
                                              self.calculate_time(self.Call_CNS_time[1]),
                                              self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
            cont += '=' * 50 + '\n'
            if 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Success\n'
            else:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Ongoing\n'
            cont += '=' * 50 + '\n'
            QMessageBox.information(self, "LCO 정보", cont)

        elif LCO_name == 'LCO 3.4.3':
            currnet_mode = self.Monitoring_Operation_Mode()
            cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
            cont += '=' * 50 + '\n'
            cont += 'Follow up action :\n'
            cont += '  - Enter allowable operation region\n'
            cont += '  - Limit Time : 30 min\n'
            cont += '=' * 50 + '\n'
            cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
            cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
                                              self.calculate_time(self.Call_CNS_time[1]),
                                              self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
            cont += '=' * 50 + '\n'
            if self.predict_SVM(self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']) != 1:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Ongoing\n'
            else:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Success\n'
            cont += '=' * 50 + '\n'
            QMessageBox.information(self, "LCO 정보", cont)

        elif LCO_name == 'LCO 3.1.1':
            currnet_mode = self.Monitoring_Operation_Mode()
            cont = '[{}] 현재 운전 모드 : [Mode-{}]\n'.format(LCO_name, currnet_mode)
            cont += '=' * 50 + '\n'
            cont += 'Follow up action :\n'
            cont += '  - Boron Injectionl\n'
            cont += '=' * 50 + '\n'
            cont += '시작 시간\t:\t현재 시간\t:\t종료 시간\n'
            cont += '{}\t:\t{}\t:\t{}\n'.format(self.calculate_time(self.TSMS_State[LCO_name]['Start_time']),
                                                self.calculate_time(self.Call_CNS_time[1]),
                                                self.calculate_time(self.TSMS_State[LCO_name]['End_time']))
            cont += '=' * 50 + '\n'
            if self.Calculator_SDM() >= 1770:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Ongoing\n'
            else:
                if self.TSMS_State[LCO_name]['End_time'] <= self.Call_CNS_time[1]:
                    cont += '현재 운전 상태 : Action Fail\n'
                else:
                    cont += '현재 운전 상태 : Action Success\n'
            cont += '=' * 50 + '\n'
            QMessageBox.information(self, "LCO 정보", cont)

        else:
            pass

    def Make_P_T_SVM(self):
        # print('SVM 모델 훈련 시작')
        data = pd.read_csv('SVM_PT_DATA.csv', header=None)

        X = data.loc[:, 0:1].values
        y = data[2].values

        # 데이터 전처리
        self.scaler.fit(X)
        X = self.scaler.transform(X)
        # SVM 훈련
        svc = svm.SVC(kernel='rbf', gamma='auto', C=1000)
        svc.fit(X, y)
        # print("훈련 세트 정확도 : {: .3f}".format(svc.score(X_train_scaled, y_train)))
        # print("테스트 세트 정확도 : {: .3f}".format(svc.score(X_test_scaled, y_test)))
        return svc

    def predict_SVM(self, Temp, Pressure):
        temp = self.scaler.transform([[Temp, Pressure]])
        return self.model_svm.predict(temp)[0]


class sub_tren_window(QDialog):

    def __init__(self, mem):
        super().__init__()
        self.mem = mem

        self.Trend_ui = Trend_ui()
        self.Trend_ui.setupUi(self)
        # ===============================================================
        # rod gp
        self.draw_rod_his_gp()

        # self.Trend_ui.listWidget.addItem('[00:00:01]\tLCO 1.1.1')
        #  ==============================================================
        self.Trend_ui.listWidget.addItem('RCS_DNBR_1')
        self.Trend_ui.listWidget.addItem('RCS_DNBR_2')
        #  ==============================================================

        timer = QtCore.QTimer(self)
        for _ in [self.update_window, self.update_rod_his_gp]:
            timer.timeout.connect(_)
        timer.start(500)

        self.Trend_ui.listWidget.itemClicked.connect(self.print_out)
        # self.Trend_ui.listWidget.itemClicked(self.print_out)

        self.show()

    def update_window(self):
        self.Trend_ui.Test_label.setText('{:0.2f}'.format(self.mem['ZINST58']['V']))
        self.Trend_ui.Rod_1.setGeometry(30, 100, 41, abs(self.mem['KBCDO10']['V'] - 228))
        self.Trend_ui.Rod_2.setGeometry(90, 100, 41, abs(self.mem['KBCDO9']['V'] - 228))
        self.Trend_ui.Rod_3.setGeometry(150, 100, 41, abs(self.mem['KBCDO8']['V'] - 228))
        self.Trend_ui.Rod_4.setGeometry(210, 100, 41, abs(self.mem['KBCDO7']['V'] - 228))
        self.Trend_ui.Dis_Rod_4.setText(str(self.mem['KBCDO7']['V']))
        self.Trend_ui.Dis_Rod_3.setText(str(self.mem['KBCDO8']['V']))
        self.Trend_ui.Dis_Rod_2.setText(str(self.mem['KBCDO9']['V']))
        self.Trend_ui.Dis_Rod_1.setText(str(self.mem['KBCDO10']['V']))

    def draw_rod_his_gp(self):
        self.rod_fig = plt.figure()
        self.rod_ax = self.rod_fig.add_subplot(111)
        self.rod_canvas = FigureCanvasQTAgg(self.rod_fig)
        self.Trend_ui.Rod_his.addWidget(self.rod_canvas)

    def update_rod_his_gp(self):
        self.rod_ax.clear()
        temp = []
        for _ in range(len(self.mem['KSWO33']['L'])):
            if self.mem['KSWO33']['L'][_] == 0 and self.mem['KSWO32']['L'][_] == 0:
                temp.append(0)
            elif self.mem['KSWO33']['L'][_] == 1 and self.mem['KSWO32']['L'][_] == 0:
                temp.append(1)
            elif self.mem['KSWO33']['L'][_] == 0 and self.mem['KSWO32']['L'][_] == 1:
                temp.append(-1)
        self.rod_ax.plot(temp)
        self.rod_ax.set_ylim(-1.2, 1.2)
        self.rod_ax.set_xlim(len(self.mem['KSWO33']['L']) - 100, len(self.mem['KSWO33']['L']))
        self.rod_ax.set_yticks([-1, 0, 1])
        self.rod_ax.set_yticklabels(['Down', 'Stay', 'UP'])
        self.rod_ax.grid()
        self.rod_canvas.draw()


    #  ==============================================================
    def print_out(self, item):
        # LCO_name = item.text().split('\t')[1]
        # if LCO_name == 'LCO 1.1.1':
        #     content = 'LCO 1.1.1\n불만족 조건: 가압기 압력이 150km/cm^2 이 되면 안됨.\n 현재 가압기 압력 상태:{}'.format(self.mem['ZINST58']['V'])
        #     QMessageBox.information(self, "LCO 정보", content)

        self.r = 30

        if item.text() == 'RCS_DNBR_1':
            QMessageBox.information(self, "LCO 정보", self.RCS_DNBR_Parameter_1())
        elif item.text() == 'RCS_DNBR_2':
            QMessageBox.information(self, "LCO 정보", self.RCS_DNBR_Parameter_2())

    def RCS_DNBR_Parameter_1(self):
        return str(self.r)

    def RCS_DNBR_Parameter_2(self):
        if self.mem['ZINST58']['V'] > 155:
            return str('불만족 {} {}'.format(self.r, self.mem['ZINST58']['V']))
        elif self.mem['ZINST58']['V'] < 154:
            return str('만족 {} {}'.format(self.r, self.mem['ZINST58']['V']))
    #  ==============================================================