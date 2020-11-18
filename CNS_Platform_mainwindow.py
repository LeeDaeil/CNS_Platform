# from PySide2.QtWidgets import QApplication, QWidget
# from PySide2.QtWidgets import QDialog, QApplication, QMessageBox, QWidget
# from PySide2 import QtCore, QtWidgets
from copy import deepcopy
from time import time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
import pickle
from Interface import CNS_Platform_mainwindow as CNS_Main_window
from TOOL import TOOL_etc, TOOL_PTCurve, TOOL_CSF
# from CNS_Platform_rod_controller import rod_controller_interface
# from CNS_Platform_pzr_controller import pzr_controller_interface
# from CNS_Platform_Strategy import Strategy_interface
# from CNS_Platform_EventDig import Event_dig_model
# import CNS_Platform_PARA as PARA


class CNS_mw(QWidget):
    def __init__(self, mem):
        super().__init__()
        # Mother mem
        self.mem = mem
        #
        self.dbmem = mem[0]  # main mem connection
        self.copy_mem_structure = deepcopy(self.dbmem)
        self.trig_mem = mem[-1]  # main mem connection
        self.copy_trig_mem = deepcopy(self.trig_mem)
        # ---- UI 호출
        print('Main_interface UI 호출')
        self.ui = CNS_Main_window.Ui_Dialog()
        self.ui.setupUi(self)
        # ---- UI 초기 세팅
        # ---- 초기함수 호출
        self.init_color_setting()
        # ---- 버튼 명령
        self.ui.Auto_op.clicked.connect(self._call_auto_dis_click_auto)
        self.ui.Manual_op.clicked.connect(self._call_auto_dis_click_man)
        # TSMS 리스트 누르면 정보 나옴
        # self.ui.Performace_Mn.itemClicked.connect(self.TSMS_LCO_info)
        # EVENT_DIG 모듈
        # self.ui.Event_DIG.clicked.connect(self.call_event_window)
        # 제어봉 인터페이스 모듈
        # self.ui.Open_GP_Window.clicked.connect(self.call_rod_controller)
        # PZR 인터페이스 모듈
        # self.ui.PZR_GP.clicked.connect(self.call_pzr_controller)
        # 전략설정 인터페이스 모듈 - 리스트 누르면 인터페이스 호출됨.
        # self.ui.listWidget.itemClicked.connect(self.call_strategy_inter)
        # ======================= 타이머 동작 ================================
        # update_module = [self.update_display, self.update_timmer, self.update_alarm, self.update_comp, self.update_CSF,
        #                  self.update_Auto_DIS, self.update_OPStrategy_DIS, self.update_TSMS_DIS,
        #                  ] #self.run_TSMS, self.run_AUTO]
        # timer = QtCore.QTimer(self)
        # for _ in update_module:
        #     timer.timeout.connect(_)
        # timer.start(600)
        '''-'''
        # ---- Qtimer
        self.st = time()
        timer = QTimer(self)
        for _ in [self._update_test, self._update_main_display]:
            timer.timeout.connect(_)
        timer.start(600)
        # ----
        self.show()

    def _update_test(self):
        # print(self.dbmem['KCNTOMS'], f'MainUI {time() - self.st}')
        print(self.dbmem['cWFWLN1']['Val'], self.dbmem['WFWLN1']['Val'], f'MainUI {time() - self.st}')
        # self.st = time()
        pass

    #
    #
    # # ======================= 새롭게 열리는 윈도우 들 ====================
    # def call_event_window(self):
    #     self.event_window = Event_dig_model(self.mem, self.trig_mem)
    #
    # def call_rod_controller(self):
    #     self.rod_controller_module = rod_controller_interface(self.mem, self.trig_mem)
    #
    # def call_pzr_controller(self):
    #     self.pzr_controller_module = pzr_controller_interface(self.mem, self.trig_mem)
    #
    # def call_strategy_inter(self):
    #     self.call_st = Strategy_interface(trig_mem=self.trig_mem)
    #
    # ======================= Call_ =============================================
    #

    # ======================= Initial_color======================================
    #
    def init_color_setting(self):
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

    # ======================= Call_ =============================================
    #
    def _call_auto_dis_click_man(self):
        self.trig_mem['Auto_Call'] = False

    def _call_auto_dis_click_auto(self):
        self.trig_mem['Auto_Call'] = True

    # ======================= Main Display ======================================
    #
    def _update_main_display(self):
        self._update_main_display_indicator()
        self._update_main_display_time()
        self._update_main_display_alarm()
        self._update_main_display_comp()
        self._update_main_display_csf()
        self._update_main_display_op_strategy()
        self._update_main_display_autonomous()

    def _update_main_display_indicator(self):
        self.ui.D_50.setText('{:0.2f}'.format(self.dbmem['UHOLEG1']['Val']))    # Hot leg temp loop 1
        self.ui.D_48.setText('{:0.2f}'.format(self.dbmem['UHOLEG2']['Val']))    # Hot leg temp loop 2
        self.ui.D_45.setText('{:0.2f}'.format(self.dbmem['UHOLEG3']['Val']))    # Hot leg temp loop 3
        self.ui.D_15.setText('{:0.2f}'.format(self.dbmem['UCOLEG1']['Val']))  # Cold leg temp loop 1
        self.ui.D_18.setText('{:0.2f}'.format(self.dbmem['UCOLEG2']['Val']))  # Cold leg temp loop 2
        self.ui.D_44.setText('{:0.2f}'.format(self.dbmem['UCOLEG3']['Val']))  # Cold leg temp loop 3
        self.ui.D_21.setText('{:0.2f}'.format(self.dbmem['ZINST58']['Val']))  # PZR pressure
        self.ui.D_9.setText('{:0.2f}'.format(self.dbmem['ZINST46']['Val']))  # CORE outtemp
        self.ui.D_31.setText('{:0.2f}'.format(self.dbmem['ZINST78']['Val']))  # S/G1 level
        self.ui.D_32.setText('{:0.2f}'.format(self.dbmem['ZINST75']['Val']))  # S/G1 pressure
        self.ui.D_36.setText('{:0.2f}'.format(self.dbmem['ZINST77']['Val']))  # S/G2 level
        self.ui.D_35.setText('{:0.2f}'.format(self.dbmem['ZINST74']['Val']))  # S/G2 pressure
        self.ui.D_42.setText('{:0.2f}'.format(self.dbmem['ZINST76']['Val']))  # S/G3 level
        self.ui.D_40.setText('{:0.2f}'.format(self.dbmem['ZINST73']['Val']))  # S/G3 pressure

        self.ui.D_20.setText('{:0.2f}'.format(self.dbmem['ZINST63']['Val']))  # PZR REAL LEVEL
        self.ui.D_12.setText('{:0.2f}'.format(self.dbmem['ZREAC']['Val']))  # CORE_LEVEL
        self.ui.D_14.setText('{:0.2f}'.format(self.dbmem['KBCDO16']['Val']))  # CORE_BORON
        self.ui.D_1.setText('{:0.2f}'.format(self.dbmem['URHRRE']['Val']))  # RHR_TEMP
        self.ui.D_4.setText('{:0.2f}'.format(self.dbmem['WRHRRE']['Val']))  # RHR_FLOW
        self.ui.D_5.setText('{:0.2f}'.format(self.dbmem['PVCT']['Val']))  # VCT_PRESSURE
        self.ui.D_7.setText('{:0.2f}'.format(self.dbmem['ZVCT']['Val']))  # VCT_LEVEL
        self.ui.D_27.setText('{:0.2f}'.format(self.dbmem['UCOND']['Val']))  # COND_TEMP
        self.ui.D_30.setText('{:0.2f}'.format(self.dbmem['ZCOND']['Val']))  # COND_PRESSURE
        self.ui.D_24.setText('{:0.2f}'.format(self.dbmem['ZCNDTK']['Val']))  # CST1_LEVEL
        self.ui.D_25.setText('{:0.2f}'.format(self.dbmem['ZAFWTK']['Val']))  # CST2_LEVEL
        self.ui.D_power.setText('{:0.2f} [%]'.format(self.dbmem['QPROREL']['Val']*100))  # POWER
        self.ui.D_elec.setText('{:0.2f} [MWe]'.format(self.dbmem['ZINST124']['Val']))  # POWER
        pass

    def _update_main_display_time(self):
        get_sec = int(self.dbmem["KCNTOMS"]["Val"]/5)
        self.ui.CNS_Time.setText(f'CNS TIME : {TOOL_etc.ToolEtc.get_calculated_time(get_sec)}')

    def _update_main_display_alarm(self):
        def Alarm_dis(ui, para):
            if self.dbmem[para]['Val'] == 1:  # on signal
                ui.setStyleSheet(self.back_color['red'])
            else:
                ui.setStyleSheet(self.back_color['gray'])

        Alarm_dis(self.ui.A_01, 'KLAMPO251')
        Alarm_dis(self.ui.A_02, 'KLAMPO252')
        Alarm_dis(self.ui.A_03, 'KLAMPO253')
        Alarm_dis(self.ui.A_04, 'KLAMPO254')

        Alarm_dis(self.ui.A_05, 'KLAMPO255')
        Alarm_dis(self.ui.A_06, 'KLAMPO256')
        Alarm_dis(self.ui.A_07, 'KLAMPO257')
        Alarm_dis(self.ui.A_08, 'KLAMPO258')

        Alarm_dis(self.ui.A_09, 'KLAMPO259')
        Alarm_dis(self.ui.A_10, 'KLAMPO260')
        Alarm_dis(self.ui.A_11, 'KLAMPO261')
        Alarm_dis(self.ui.A_12, 'KLAMPO262')

        Alarm_dis(self.ui.A_13, 'KLAMPO263')
        Alarm_dis(self.ui.A_14, 'KLAMPO264')
        Alarm_dis(self.ui.A_15, 'KLAMPO265')
        Alarm_dis(self.ui.A_16, 'KLAMPO266')

        Alarm_dis(self.ui.A_17, 'KLAMPO268')
        Alarm_dis(self.ui.A_18, 'KLAMPO269')
        Alarm_dis(self.ui.A_19, 'KLAMPO270')
        Alarm_dis(self.ui.A_20, 'KLAMPO271')

        Alarm_dis(self.ui.A_21, 'KLAMPO272')
        Alarm_dis(self.ui.A_22, 'KLAMPO273')
        Alarm_dis(self.ui.A_23, 'KLAMPO274')
        Alarm_dis(self.ui.A_24, 'KLAMPO295')

        Alarm_dis(self.ui.A_25, 'KLAMPO296')
        Alarm_dis(self.ui.A_26, 'KLAMPO297')
        Alarm_dis(self.ui.A_27, 'KLAMPO298')

        Alarm_dis(self.ui.A_28, 'KLAMPO275')
        Alarm_dis(self.ui.A_29, 'KLAMPO276')
        Alarm_dis(self.ui.A_30, 'KLAMPO277')
        Alarm_dis(self.ui.A_31, 'KLAMPO278')

        Alarm_dis(self.ui.A_32, 'KLAMPO279')
        Alarm_dis(self.ui.A_33, 'KLAMPO280')
        Alarm_dis(self.ui.A_34, 'KLAMPO281')
        Alarm_dis(self.ui.A_35, 'KLAMPO282')

        Alarm_dis(self.ui.A_36, 'KLAMPO283')
        Alarm_dis(self.ui.A_37, 'KLAMPO284')
        Alarm_dis(self.ui.A_38, 'KLAMPO285')
        Alarm_dis(self.ui.A_39, 'KLAMPO286')

        Alarm_dis(self.ui.A_40, 'KLAMPO287')
        Alarm_dis(self.ui.A_41, 'KLAMPO288')
        Alarm_dis(self.ui.A_42, 'KLAMPO289')
        Alarm_dis(self.ui.A_43, 'KLAMPO290')

        Alarm_dis(self.ui.A_44, 'KLAMPO301')       #alram2
        Alarm_dis(self.ui.A_45, 'KLAMPO302')
        Alarm_dis(self.ui.A_46, 'KLAMPO303')
        Alarm_dis(self.ui.A_47, 'KLAMPO304')

        Alarm_dis(self.ui.A_48, 'KLAMPO305')
        Alarm_dis(self.ui.A_49, 'KLAMPO306')
        Alarm_dis(self.ui.A_50, 'KLAMPO307')
        Alarm_dis(self.ui.A_51, 'KLAMPO308')

        Alarm_dis(self.ui.A_52, 'KLAMPO309')
        Alarm_dis(self.ui.A_53, 'KLAMPO310')
        Alarm_dis(self.ui.A_54, 'KLAMPO311')
        Alarm_dis(self.ui.A_55, 'KLAMPO312')

        Alarm_dis(self.ui.A_56, 'KLAMPO313')
        Alarm_dis(self.ui.A_57, 'KLAMPO314')
        Alarm_dis(self.ui.A_58, 'KLAMPO315')
        Alarm_dis(self.ui.A_59, 'KLAMPO316')

        Alarm_dis(self.ui.A_60, 'KLAMPO317')
        Alarm_dis(self.ui.A_61, 'KLAMPO318')
        Alarm_dis(self.ui.A_62, 'KLAMPO319')
        Alarm_dis(self.ui.A_63, 'KLAMPO320')

        Alarm_dis(self.ui.A_64, 'KLAMPO321')
        Alarm_dis(self.ui.A_65, 'KLAMPO322')
        Alarm_dis(self.ui.A_66, 'KLAMPO323')
        Alarm_dis(self.ui.A_67, 'KLAMPO324')

        Alarm_dis(self.ui.A_68, 'KLAMPO325')
        Alarm_dis(self.ui.A_69, 'KLAMPO326')
        Alarm_dis(self.ui.A_70, 'KLAMPO327')
        Alarm_dis(self.ui.A_71, 'KLAMPO328')

        Alarm_dis(self.ui.A_72, 'KLAMPO329')
        Alarm_dis(self.ui.A_73, 'KLAMPO330')
        Alarm_dis(self.ui.A_74, 'KLAMPO331')
        Alarm_dis(self.ui.A_75, 'KLAMPO332')

        Alarm_dis(self.ui.A_76, 'KLAMPO333')
        Alarm_dis(self.ui.A_77, 'KLAMPO335')
        Alarm_dis(self.ui.A_78, 'KLAMPO336')
        Alarm_dis(self.ui.A_79, 'KLAMPO337')

        Alarm_dis(self.ui.A_80, 'KLAMPO338')
        Alarm_dis(self.ui.A_81, 'KLAMPO339')
        Alarm_dis(self.ui.A_82, 'KLAMPO340')
        Alarm_dis(self.ui.A_83, 'KLAMPO341')

    def _update_main_display_comp(self):
        def Comp_on_off(ui_type, ui_pump, para):
            if ui_type == 1 or ui_type == 2 or ui_type == 3:
                if self.dbmem[para]['Val'] == 1:
                    ui_pump.setStyleSheet(self.back_img[f'P_{ui_type}_ON'])
                else:
                    ui_pump.setStyleSheet(self.back_img[f'P_{ui_type}_OFF'])
            elif ui_type == 4:
                if self.dbmem[para]['Val'] == 1:
                    ui_pump.setStyleSheet(self.back_color['red'])
                else:
                    ui_pump.setStyleSheet(self.back_color['gray'])
            elif ui_type == 5 or ui_type == 6:
                if self.dbmem[para]['Val'] == 1:
                    ui_pump.setStyleSheet(self.back_img[f'V_{ui_type - 4}_OPEN'])
                elif self.dbmem[para]['Val'] == 0:
                    ui_pump.setStyleSheet(self.back_img[f'V_{ui_type - 4}_CLOSE'])
                else:
                    ui_pump.setStyleSheet(self.back_img[f'V_{ui_type - 4}_HALF'])
            elif ui_type == 7:
                if para == 'WAFWS1':
                    if self.dbmem['KLAMPO134']['Val'] == 1:
                        if self.dbmem[para]['Val'] == 25:
                            ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                            self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                            self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                        elif self.dbmem[para]['Val'] == 0:
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
                    if self.dbmem['KLAMPO135']['Val'] == 1:
                        if self.dbmem[para]['Val'] == 25:
                            ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                            self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                            self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                        elif self.dbmem[para]['Val'] == 0:
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
                    if self.dbmem['KLAMPO136']['Val'] == 1:
                        if self.dbmem[para]['Val'] == 25:
                            ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                            self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                            self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                        elif self.dbmem[para]['Val'] == 0:
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
        # Aux Feed Water Pump
        Comp_on_off(1, self.ui.P_1, 'KLAMPO134')
        Comp_on_off(1, self.ui.P_2, 'KLAMPO135')
        Comp_on_off(1, self.ui.P_3, 'KLAMPO136')
        # Main Feed Water Pump
        Comp_on_off(1, self.ui.P_4, 'KLAMPO241')
        Comp_on_off(1, self.ui.P_5, 'KLAMPO242')
        Comp_on_off(1, self.ui.P_6, 'KLAMPO243')
        # Condensor pump
        Comp_on_off(3, self.ui.P_7, 'KLAMPO181')
        Comp_on_off(3, self.ui.P_8, 'KLAMPO182')
        Comp_on_off(3, self.ui.P_9, 'KLAMPO183')
        # Charging pump
        Comp_on_off(2, self.ui.P_10, 'KLAMPO71')
        Comp_on_off(2, self.ui.P_11, 'KLAMPO70')
        Comp_on_off(2, self.ui.P_12, 'KLAMPO69')
        # RHR Pump
        Comp_on_off(2, self.ui.P_13, 'KLAMPO55')
        # RCP
        Comp_on_off(4, self.ui.D_51, 'KLAMPO124')
        Comp_on_off(4, self.ui.D_52, 'KLAMPO125')
        Comp_on_off(4, self.ui.D_53, 'KLAMPO126')
        # Main steam line
        Comp_on_off(6, self.ui.V_37, 'BHV108')
        Comp_on_off(6, self.ui.V_38, 'BHV208')
        Comp_on_off(6, self.ui.V_39, 'BHV308')
        # Feedwater valve
        Comp_on_off(5, self.ui.V_12, 'BFV478')
        Comp_on_off(5, self.ui.V_13, 'BFV479')
        Comp_on_off(5, self.ui.V_14, 'BFV488')
        Comp_on_off(5, self.ui.V_15, 'BFV489')
        Comp_on_off(5, self.ui.V_16, 'BFV498')
        Comp_on_off(5, self.ui.V_17, 'BFV499')
        # AUX FEED VALVE
        Comp_on_off(7, self.ui.V_48, 'WAFWS1')
        Comp_on_off(7, self.ui.V_49, 'WAFWS2')
        Comp_on_off(7, self.ui.V_50, 'WAFWS3')
        # VALVE
        Comp_on_off(5, self.ui.V_1, 'BHV22')
        Comp_on_off(6, self.ui.V_40, 'BHSV')
        Comp_on_off(6, self.ui.V_41, 'BHSV')
        Comp_on_off(6, self.ui.V_42, 'BHSV')
        Comp_on_off(6, self.ui.V_43, 'BHSV')
        Comp_on_off(6, self.ui.V_44, 'BHTV')
        Comp_on_off(6, self.ui.V_45, 'BHTV')
        Comp_on_off(6, self.ui.V_46, 'BHTV')
        Comp_on_off(6, self.ui.V_47, 'BHTV')
        Comp_on_off(6, self.ui.V_36, 'BHV40')
        Comp_on_off(6, self.ui.V_35, 'BHV201')
        Comp_on_off(6, self.ui.V_51, 'BHV302')
        Comp_on_off(6, self.ui.V_52, 'BHV301')
        Comp_on_off(6, self.ui.V_19, 'BHV301')

        Comp_on_off(5, self.ui.V_19, 'BHV8')
        Comp_on_off(5, self.ui.V_5, 'BHV1')
        Comp_on_off(5, self.ui.V_6, 'BHV1')
        Comp_on_off(5, self.ui.V_7, 'BHV1')
        Comp_on_off(5, self.ui.V_8, 'BLV615')
        Comp_on_off(5, self.ui.V_9, 'BLV616')
        Comp_on_off(5, self.ui.V_11, 'BLV459')

        Comp_on_off(5, self.ui.V_2, 'BHV101')
        Comp_on_off(5, self.ui.V_3, 'BHV102')
        Comp_on_off(5, self.ui.V_10, 'BHV39')

        Comp_on_off(5, self.ui.V_24, 'BLTV')
        Comp_on_off(5, self.ui.V_23, 'BLTV')
        Comp_on_off(5, self.ui.V_27, 'BLTV')
        Comp_on_off(5, self.ui.V_28, 'BLTV')
        Comp_on_off(5, self.ui.V_31, 'BLTV')
        Comp_on_off(5, self.ui.V_32, 'BLTV')

        Comp_on_off(5, self.ui.V_25, 'BLSV')
        Comp_on_off(5, self.ui.V_26, 'BLSV')
        Comp_on_off(5, self.ui.V_30, 'BLSV')
        Comp_on_off(5, self.ui.V_22, 'BLSV')
        Comp_on_off(5, self.ui.V_29, 'BLSV')
        Comp_on_off(5, self.ui.V_33, 'BLSV')

        Comp_on_off(5, self.ui.V_19, 'BFV13')
        Comp_on_off(5, self.ui.V_18, 'BLV177')
        pass

    def _update_main_display_csf(self):
        V = {
            'Trip': self.dbmem['KLAMPO9']['Val'],
            # CSF 1 Value 미임계 상태 추적도
            'PowerRange': self.dbmem['ZINST1']['Val'], 'IntermediateRange': self.dbmem['ZINST2']['Val'],
            'SourceRange': self.dbmem['ZINST3']['Val'],
            # CSF 2 Value 노심냉각 상태 추적도
            'CoreExitTemp': self.dbmem['UUPPPL']['Val'],
            'PTCurve': TOOL_PTCurve.PTCureve().Check(Temp=self.dbmem['UAVLEG2']['Val'],
                                                     Pres=self.dbmem['ZINST65']['Val']),
            # CSF 3 Value 열제거원 상태 추적도
            'SG1Nar': self.dbmem['ZINST78']['Val'], 'SG2Nar': self.dbmem['ZINST77']['Val'],
            'SG3Nar': self.dbmem['ZINST76']['Val'],
            'SG1Pres': self.dbmem['ZINST75']['Val'], 'SG2Pres': self.dbmem['ZINST74']['Val'],
            'SG3Pres': self.dbmem['ZINST73']['Val'],
            'SG1Feed': self.dbmem['WFWLN1']['Val'], 'SG2Feed': self.dbmem['WFWLN2']['Val'],
            'SG3Feed': self.dbmem['WFWLN3']['Val'],

            'AllSGFeed': self.dbmem['WFWLN1']['Val'] +
                         self.dbmem['WFWLN2']['Val'] +
                         self.dbmem['WFWLN3']['Val'],
            'SG1Wid': self.dbmem['ZINST72']['Val'], 'SG2Wid': self.dbmem['ZINST71']['Val'],
            'SG3Wid': self.dbmem['ZINST70']['Val'],
            'SG123Wid': [self.dbmem['ZINST72']['Val'], self.dbmem['ZINST71']['Val'], self.dbmem['ZINST70']['Val']],

            # CSF 4 Value RCS 건전성 상태 추적도
            'RCSColdLoop1': self.dbmem['UCOLEG1']['List'], 'RCSColdLoop2': self.dbmem['UCOLEG2']['List'],
            'RCSColdLoop3': self.dbmem['UCOLEG3']['List'], 'RCSPressure': self.dbmem['ZINST65']['Val'],
            'CNSTimeL': self.dbmem['KCNTOMS']['List'],  # PTCurve: ...
            # CSF 5 Value 격납용기 건전성 상태 추적도
            'CTMTPressre': self.dbmem['ZINST26']['Val'], 'CTMTSumpLevel': self.dbmem['ZSUMP']['Val'],
            'CTMTRad': self.dbmem['ZINST22']['Val'],
            # CSF 6 Value RCS 재고량 상태 추적도
            'PZRLevel': self.dbmem['ZINST63']['Val']
        }
        CSF = {
            'CSF1': TOOL_CSF.CSFTree.CSF1(V['Trip'], V['PowerRange'], V['IntermediateRange'], V['SourceRange'])['L'],
            'CSF2': TOOL_CSF.CSFTree.CSF2(V['Trip'], V['CoreExitTemp'], V['PTCurve'])['L'],
            'CSF3': TOOL_CSF.CSFTree.CSF3(V['Trip'], V['SG1Nar'], V['SG2Nar'], V['SG3Nar'],
                                          V['SG1Pres'], V['SG2Pres'], V['SG3Pres'],
                                          V['SG1Feed'], V['SG2Feed'], V['SG3Feed'])['L'],
            'CSF4': TOOL_CSF.CSFTree.CSF4(V['Trip'], V['RCSColdLoop1'], V['RCSColdLoop2'], V['RCSColdLoop3'],
                                          V['RCSPressure'], V['PTCurve'], V['CNSTimeL'])['L'],
            'CSF5': TOOL_CSF.CSFTree.CSF5(V['Trip'], V['CTMTPressre'], V['CTMTSumpLevel'], V['CTMTRad'])['L'],
            'CSF6': TOOL_CSF.CSFTree.CSF6(V['Trip'], V['PZRLevel'])['L']
        }
        # CSF = {'CSF1':0, ..}
        # 'L': 0 만족, 1: 노랑, 2: 주황, 3: 빨강
        def CSF_switch(level=0, display=[0,0,0,0]):
            if level == 0:
                display[0].setStyleSheet(self.back_color['green'])
                display[1].setStyleSheet(self.back_color['gray'])
                display[2].setStyleSheet(self.back_color['gray'])
                display[3].setStyleSheet(self.back_color['gray'])
            elif level == 1:
                display[0].setStyleSheet(self.back_color['gray'])
                display[1].setStyleSheet(self.back_color['yellow'])
                display[2].setStyleSheet(self.back_color['gray'])
                display[3].setStyleSheet(self.back_color['gray'])
            elif level == 2:
                display[0].setStyleSheet(self.back_color['gray'])
                display[1].setStyleSheet(self.back_color['gray'])
                display[2].setStyleSheet(self.back_color['orange'])
                display[3].setStyleSheet(self.back_color['gray'])
            elif level == 3:
                display[0].setStyleSheet(self.back_color['gray'])
                display[1].setStyleSheet(self.back_color['gray'])
                display[2].setStyleSheet(self.back_color['gray'])
                display[3].setStyleSheet(self.back_color['red'])
            else:
                pass
            return 0

        CSF_switch(CSF['CSF1'], [self.ui.CSF_1_1, self.ui.CSF_1_2, self.ui.CSF_1_3, self.ui.CSF_1_4])
        CSF_switch(CSF['CSF2'], [self.ui.CSF_1_5, self.ui.CSF_1_6, self.ui.CSF_1_7, self.ui.CSF_1_8])
        CSF_switch(CSF['CSF3'], [self.ui.CSF_1_9, self.ui.CSF_1_10, self.ui.CSF_1_11, self.ui.CSF_1_12])
        CSF_switch(CSF['CSF4'], [self.ui.CSF_1_13, self.ui.CSF_1_14, self.ui.CSF_1_15, self.ui.CSF_1_16])
        CSF_switch(CSF['CSF5'], [self.ui.CSF_1_17, self.ui.CSF_1_18, self.ui.CSF_1_19, self.ui.CSF_1_20])
        CSF_switch(CSF['CSF6'], [self.ui.CSF_1_21, self.ui.CSF_1_22, self.ui.CSF_1_23, self.ui.CSF_1_24])
        pass

    def _update_main_display_op_strategy(self):
        light = ['', '', '']
        if self.trig_mem['Operation_Strategy'] == 'N': light = ['green',    'gray',     'gray']
        if self.trig_mem['Operation_Strategy'] == 'A': light = ['gray',     'yellow',   'gray']
        if self.trig_mem['Operation_Strategy'] == 'E': light = ['gray',     'gray',     'red']
        self.ui.Normal_dis.setStyleSheet(self.back_color[light[0]])
        self.ui.Abnormal_dis.setStyleSheet(self.back_color[light[1]])
        self.ui.Emergen_dis.setStyleSheet(self.back_color[light[2]])

    def _update_main_display_autonomous(self):
        if self.trig_mem['Auto_Call']:                                      # True - autonomouse
            self.ui.Manual_op.setStyleSheet(self.back_color['gray'])
            self.ui.Auto_op.setStyleSheet(self.back_color['red'])
        else:                                                               # False - Manual
            self.ui.Manual_op.setStyleSheet(self.back_color['red'])
            self.ui.Auto_op.setStyleSheet(self.back_color['gray'])

        if self.trig_mem['Auto_re_man']:     # True 사람 필요
            self.ui.Operator_need.setStyleSheet(self.back_color['red'])
        else:
            self.ui.Operator_need.setStyleSheet(self.back_color['gray'])

    # # ======================= Autonomous condition DIS =================
    # def update_Auto_DIS(self):
    #     # =================== 비상 시 자율 제어 수행 여부 확인 부분 =======
    #     if self.mem['KCNTOMS']['V'] < 4:
    #         # 초기 혹시 발생한 내역을 삭제함.
    #         self.ui.Auto_list.clear()
    #     if self.trig_mem['ST_OPStratey'] == PARA.Emergency:
    #         if self.mem['KLAMPO9']['V'] == 1: self.Auto_DIS_add_list_signal('Reactor trip')
    #         if self.mem['KLAMPO6']['V'] == 1: self.Auto_DIS_add_list_signal('SI valve open')
    #         if self.mem['KLAMPO4']['V'] == 1: self.Auto_DIS_add_list_signal('Containment ISO')
    #         if self.mem['KLAMPO2']['V'] == 1: self.Auto_DIS_add_list_signal('Feedwater ISO')
    #         if self.mem['KLAMPO3']['V'] == 1: self.Auto_DIS_add_list_signal('Main steam line ISO')
    #         if self.mem['KLAMPO134']['V'] == 1: self.Auto_DIS_add_list_signal('Aux feed pump 1 start')
    #         if self.mem['KLAMPO135']['V'] == 1: self.Auto_DIS_add_list_signal('Aux feed pump 2 start')
    #         if self.mem['KLAMPO136']['V'] == 1: self.Auto_DIS_add_list_signal('Aux feed pump 3 start')
    #         if self.mem['KLAMPO70']['V'] == 1: self.Auto_DIS_add_list_signal('Charging pump 2 start')
    #         if self.mem['KLAMPO69']['V'] == 1: self.Auto_DIS_add_list_signal('Charging pump 3 start')
    #         if self.mem['KLAMPO124']['V'] == 0: self.Auto_DIS_add_list_signal('RCP 1 stop')
    #         if self.mem['KLAMPO125']['V'] == 0: self.Auto_DIS_add_list_signal('RCP 2 stop')
    #         if self.mem['KLAMPO126']['V'] == 0: self.Auto_DIS_add_list_signal('RCP 3 stop')
    #
    # def Auto_DIS_add_list_signal(self, content):
    #     if len(self.ui.Auto_list.findItems('{}'.format(content), QtCore.Qt.MatchContains)) == 0:
    #         self.ui.Auto_list.addItem('{} {}'.format(self.Call_CNS_time[0], content))
    #
    # # ======================= Operation Strategy DIS ===================
    # def update_OPStrategy_DIS(self):
    #
    #     # =================== 전략 변경 시 리스트에 추가 ==================
    #     if len(self.trig_mem['OPStrategy_his']) > 1:    # 비교를 위해서 2개 이상 쌓고 나서 비교 시작
    #         # 앞과 뒤가 동일한지 여부에 따라서 리스트 추가 or 추가 않함.
    #         if self.trig_mem['OPStrategy_his'][0] != self.trig_mem['OPStrategy_his'][1]:
    #             # 갑작스런 비상, 비정상 발생, 또는 비상, 비정상 -> 정상에서 복구
    #             gen_print = '{} -> {}'.format(self.trig_mem['OPStrategy_his'][1],
    #                                           self.trig_mem['OPStrategy_his'][0])
    #             change_time = f'[{self.Call_CNS_time[0]}]'
    #             self.ui.listWidget.addItem(change_time + gen_print)
    #         else:
    #             pass
    #     else:
    #         self.trig_mem['OPStrategy_his'].append(self.trig_mem['OPStrategy'])
    #
    # # ======================= TSMS DIS =================================
    # def update_TSMS_DIS(self):
    #     if self.mem['KCNTOMS']['V'] < 4 or len(self.mem['KCNTOMS']['D']) < 1:
    #         self.TSMS_State = {}
    #         self.ui.Performace_Mn.clear()
    #
    #     if self.trig_mem['OPStrategy'] == PARA.Emergency:
    #         self.Monitoring()
    #
    # def Calculator_SDM(self):
    #
    #     self.init_para = {
    #         'HFP': 100,  # H
    #         'ReatorPower': 90,  # T
    #         'BoronConcentration': 1318,  # T
    #         'Burnup': 4000,  # T
    #         'Burnup_BOL': 150,  # H
    #         'Burnup_EOL': 18850,  # H
    #         'TotalPowerDefect_BOL': 1780,  # H
    #         'TotalPowerDefect_EOL': 3500,  # H
    #         'VoidCondtent': 50,  # H
    #         'TotalRodWorth': 5790,  # H
    #         'WorstStuckRodWorth': 1080,  # H
    #         'InoperableRodNumber': 1,  # T
    #         'BankWorth_D': 480,  # H
    #         'BankWorth_C': 1370,  # H
    #         'BankWorth_B': 1810,  # H
    #         'BankWorth_A': 760,  # H
    #         'AbnormalRodName': 'C',  # T
    #         'AbnormalRodNumber': 1,  # T
    #         'ShutdownMarginValue': 1770,  # H
    #     }
    #
    #     # 1. BOL, 현출력% -> 0% 하기위한 출력 결손량 계산
    #     ReactorPower = self.mem['QPROLD']['V'] * 100
    #     PowerDefect_BOL = self.init_para['TotalPowerDefect_BOL'] * ReactorPower / self.init_para['HFP']
    #
    #     # 2. EOL, 현출력% -> 0% 하기위한 출력 결손량 계산
    #     PowerDefect_EOL = self.init_para['TotalPowerDefect_EOL'] * ReactorPower / self.init_para['HFP']
    #
    #     # 3. 현재 연소도, 현출력% -> 0% 하기위한 출력 결손량 계산
    #     A = self.init_para['Burnup_EOL'] - self.init_para['Burnup_BOL']
    #     B = PowerDefect_EOL - PowerDefect_BOL
    #     C = self.init_para['Burnup'] - self.init_para['Burnup_EOL']
    #
    #     PowerDefect_Burnup = B * C / A + PowerDefect_BOL
    #
    #     # 4. 반응도 결손량을 계산
    #     PowerDefect_Final = PowerDefect_Burnup + self.init_para['VoidCondtent']
    #
    #     # 5. 운전불가능 제어봉 제어능을 계산
    #     InoperableRodWorth = self.init_para['InoperableRodNumber'] * self.init_para['WorstStuckRodWorth']
    #
    #     # 6. 비정상 제어봉 제어능을 계산
    #     AbnormalRodWorth = self.init_para['BankWorth_{}'.format(
    #         self.init_para['AbnormalRodName'])] / 8 * self.init_para['AbnormalRodNumber']
    #
    #     # 7. 운전 불능, 비정상 제어봉 제어능의 합 계산
    #     InoperableAbnormal_RodWorth = InoperableRodWorth + AbnormalRodWorth
    #
    #     # 8. 현 출력에서의 정지여유도 계산
    #     ShutdownMargin = self.init_para['TotalRodWorth'] - InoperableAbnormal_RodWorth - PowerDefect_Final
    #
    #     return ShutdownMargin
    #
    # def Monitoring(self):
    #     # LCO 3.4.4
    #     if [self.mem['KLAMPO124']['V'], self.mem['KLAMPO125']['V'], self.mem['KLAMPO126']['V']].count(0) >= 2:
    #         if not 'LCO 3.4.4' in self.TSMS_State.keys():
    #             self.TSMS_State['LCO 3.4.4'] = {'Start_time': self.Call_CNS_time[1],
    #                                             'End_time': self.Call_CNS_time[1]+24000}
    #             end_time = self.calculate_time(self.Call_CNS_time[1]+24000)
    #             self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.4.4\tDissatisfaction'.format(self.Call_CNS_time[0],
    #                                                                                      end_time))
    #     # LCO 3.4.1
    #     if not 154.7 < self.mem['ZINST65']['V'] < 161.6 and 286.7 < self.mem['UCOLEG1']['V'] < 293.3:
    #         if not'LCO 3.4.1' in self.TSMS_State.keys():
    #             self.TSMS_State['LCO 3.4.1'] = {'Start_time': self.Call_CNS_time[1],
    #                                             'End_time': self.Call_CNS_time[1]+7200}
    #             end_time = self.calculate_time(self.Call_CNS_time[1]+7200)
    #             self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.4.1\tDissatisfaction'.format(self.Call_CNS_time[0],
    #                                                                                       end_time))
    #     # LCO 3.4.3
    #     if self.predict_SVM(self.mem['UCOLEG1']['V'], self.mem['ZINST65']['V']) != 1:
    #         if not'LCO 3.4.3' in self.TSMS_State.keys():
    #             self.TSMS_State['LCO 3.4.3'] = {'Start_time': self.Call_CNS_time[1],
    #                                             'End_time': self.Call_CNS_time[1]+1800}
    #             end_time = self.calculate_time(self.Call_CNS_time[1]+1800)
    #             self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.4.3\tDissatisfaction'.format(self.Call_CNS_time[0],
    #                                                                                       end_time))
    #
    #     # LCO 3.1.1
    #     current_SDM = self.Calculator_SDM()
    #     if current_SDM < 1770:
    #         if not 'LCO 3.1.1' in self.TSMS_State.keys():
    #             self.TSMS_State['LCO 3.1.1'] = {'Start_time': self.Call_CNS_time[1],
    #                                             'End_time': self.Call_CNS_time[1] + 900}
    #             end_time = self.calculate_time(self.Call_CNS_time[1] + 900)
    #             self.ui.Performace_Mn.addItem('{}->{}\tLCO 3.1.1\tDissatisfaction'.format(self.Call_CNS_time[0],
    #                                                                                       end_time))
    #
    # def Monitoring_Operation_Mode(self):
    #     if self.mem['CRETIV']['V'] >= 0:
    #         if self.mem['ZINST1']['V'] > 5:
    #             mode = 1
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