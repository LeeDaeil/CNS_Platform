from copy import deepcopy
from time import time
import sys
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
from collections import deque

from Interface import CNS_Platform_mainwindow as CNS_Main_window
from CNS_Platform_signalvalidation import SVBoardUI
from CNS_Platform_emergency import EMBoardUI
from CNS_Platform_abnormal import ABBoardUI
from TOOL import TOOL_etc, TOOL_PTCurve, TOOL_CSF
from CNS_Platform_rod_controller import RCBoardUI


class CNSMainWinBasic(QWidget):
    def __init__(self):
        super(CNSMainWinBasic, self).__init__()
        self.pr_('Main_interface UI 호출')
        self.ui = CNS_Main_window.Ui_Dialog()
        self.ui.setupUi(self)
        self.setGeometry(0, 0, 1600, 880)

        self._init_color_setting()

    def pr_(self, s):
        head_ = 'CNSMainWin'
        return print(f'[{head_:10}][{s}]')

    def _init_color_setting(self):
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


class CNSMainWinFunc(CNSMainWinBasic):
    def __init__(self, shmem):
        super(CNSMainWinFunc, self).__init__()
        self.shmem = shmem
        self.local_mem = self.shmem.get_shmem_db()
        self.local_save_mem = self.shmem.get_shmem_save_db()
        self.local_logic = self.shmem.get_logic_info()
        # 초기함수 호출 --------------------------------------------------------------------------------------------------
        self._init_add_window()
        # 버튼 명령 -----------------------------------------------------------------------------------------------------
        self.ui.Auto_op.clicked.connect(self._call_click_dis_click_auto)
        self.ui.Manual_op.clicked.connect(self._call_click_dis_click_man)
        self.ui.call_sv_monitoring.clicked.connect(self._call_click_win_signal_validation_monitoring)
        self.ui.call_rc_monitoring.clicked.connect(self._call_click_win_power_increase_monitoring)
        self.ui.call_em_monitoring.clicked.connect(self._call_click_win_emergency_monitoring)
        self.ui.Event_DIG.clicked.connect(self._call_click_win_abnormal_monitoring)
        # 테이블 클릭시 --------------------------------------------------------------------------------------------------
        self.ui.Performace_Mn.itemClicked.connect(self._call_click_item_lco)


        # 한번만 동작하는 기능 ..
        self.one_1 = False
        self.one_2 = False

        # Q Timer ------------------------------------------------------------------------------------------------------
        self.st = time()
        timer = QTimer(self)
        for _ in [self._update_dis]:
            timer.timeout.connect(_)
        timer.start(1000)

    # ------------------------------------------------------------------------------------------------------------------
    # _init
    def _init_add_window(self):
        self.signal_validation_monitoring = None
        self.power_increase_monitoring = None
        self.em_monitoring = None
        self.ab_monitoring = None

    # ------------------------------------------------------------------------------------------------------------------
    # _call_click
    def _call_click_dis_click_man(self):
        if not self.shmem.get_logic('Auto_re_man'):
            self.shmem.change_logic_val('Auto_Call', False)

    def _call_click_dis_click_auto(self):
        if not self.shmem.get_logic('Auto_re_man'):
            self.shmem.change_logic_val('Auto_Call', True)

    def _call_click_win_signal_validation_monitoring(self):
        local_logic = self.shmem.get_logic_info()
        if local_logic['Run_sv']:
            if self.signal_validation_monitoring is None:
                self.signal_validation_monitoring = SVBoardUI()
            else:
                self.signal_validation_monitoring.close()
                self.signal_validation_monitoring = None
        else:
            self.pr_('Not Work Signal Validation Module')

    def _call_click_win_power_increase_monitoring(self):
        local_logic = self.shmem.get_logic_info()
        if local_logic['Run_rc']:
            if self.power_increase_monitoring is None:
                self.power_increase_monitoring = RCBoardUI()
            else:
                self.power_increase_monitoring.close()
                self.power_increase_monitoring = None
        else:
            self.pr_('Not Work Power Increase Module')

    def _call_click_win_emergency_monitoring(self):
        local_logic = self.shmem.get_logic_info()
        if local_logic['Run_ec']:
            if self.em_monitoring is None:
                self.em_monitoring = EMBoardUI()
            else:
                self.em_monitoring.close()
                self.em_monitoring = None
        else:
            self.pr_('Not Work Emergency Module')

    def _call_click_win_abnormal_monitoring(self):
        local_logic = self.shmem.get_logic_info()
        if local_logic['Run_abd']:
            if self.ab_monitoring is None:
                self.ab_monitoring = ABBoardUI()
            else:
                self.ab_monitoring.close()
                self.ab_monitoring = None
        else:
            self.pr_('Not Work Abnormal Module')

    # ------------------------------------------------------------------------------------------------------------------
    # _call_click_item
    def _call_click_item_lco(self, item):
        LCO_name = item.text().split('\t')[1]

        currnet_mode = TOOL_etc.ToolEtc.get_op_mode(self.local_mem['CRETIV']['Val'],
                                                    self.local_mem['ZINST1']['Val'],
                                                    self.local_mem['UCOLEG1']['Val'])
        QMessageBox.information(self, "LCO 정보", TOOL_etc.ToolEtc.get_lco_card(
            LCO_name, currnet_mode,
            self.local_logic['LCO_Dict'][LCO_name]['St'],
            self.local_mem['KCNTOMS']['Val'],
            self.local_logic['LCO_Dict'][LCO_name]['Et'],
            self.local_mem,
        ))

    # ------------------------------------------------------------------------------------------------------------------
    # _update_dis

    def _update_dis(self):
        self.local_mem = self.shmem.get_shmem_db()
        self.local_save_mem = self.shmem.get_shmem_save_db()
        self.local_logic = self.shmem.get_logic_info()

        if self.local_logic['UpdateUI']:
            self._update_sub_win()

            self._update_dis_time()
            self._update_dis_autonomous()
            self._update_dis_alarm()
            self._update_dis_comp()
            self._update_dis_csf()
            self._update_dis_op_strategy()
            self._update_dis_indicator()

            self._update_dis_autonomous_control()

            self._update_function_LCO()

            self.shmem.change_logic_val('UpdateUI', False)

    def _update_sub_win(self):
        if self.signal_validation_monitoring is not None:
            self.signal_validation_monitoring.update(self.local_logic)

        if self.power_increase_monitoring is not None:
            self.power_increase_monitoring.update(self.local_save_mem, self.local_mem)

        if self.em_monitoring is not None:
            self.em_monitoring.update(self.local_save_mem)

        if self.ab_monitoring is not None:
            self.ab_monitoring.update(self.local_logic)

    def _update_dis_time(self):
        get_sec = int(self.local_mem["KCNTOMS"]["Val"] / 5)
        self.ui.CNS_Time.setText(f'CNS TIME : {TOOL_etc.ToolEtc.get_calculated_time(get_sec)}')

    def _update_dis_autonomous(self):
        def _update_dis_autonomous_auto_call(logic=False):
            if logic:
                self.ui.Manual_op.setStyleSheet(self.back_color['gray'])
                self.ui.Auto_op.setStyleSheet(self.back_color['red'])
            else:
                self.ui.Manual_op.setStyleSheet(self.back_color['red'])
                self.ui.Auto_op.setStyleSheet(self.back_color['gray'])

        if self.shmem.get_logic('Auto_re_man'):                                # True 사람 필요
            self.shmem.change_logic_val('Auto_Call', False)
            self.ui.Operator_need.setStyleSheet(self.back_color['red'])
            self.ui.Manual_op.setStyleSheet(self.back_color['red'])
            self.ui.Auto_op.setStyleSheet(self.back_color['gray'])
        else:
            self.ui.Operator_need.setStyleSheet(self.back_color['gray'])
            _update_dis_autonomous_auto_call(self.shmem.get_logic('Auto_Call'))

    def _update_dis_alarm(self):
        alarm_dis_list = [
            (self.ui.A_01, 'KLAMPO251'), (self.ui.A_02, 'KLAMPO252'), (self.ui.A_03, 'KLAMPO253'),
            (self.ui.A_04, 'KLAMPO254'), (self.ui.A_05, 'KLAMPO255'), (self.ui.A_06, 'KLAMPO256'),
            (self.ui.A_07, 'KLAMPO257'), (self.ui.A_08, 'KLAMPO258'), (self.ui.A_09, 'KLAMPO259'),
            (self.ui.A_10, 'KLAMPO260'), (self.ui.A_11, 'KLAMPO261'), (self.ui.A_12, 'KLAMPO262'),
            (self.ui.A_13, 'KLAMPO263'), (self.ui.A_14, 'KLAMPO264'), (self.ui.A_15, 'KLAMPO265'),
            (self.ui.A_16, 'KLAMPO266'), (self.ui.A_17, 'KLAMPO268'), (self.ui.A_18, 'KLAMPO269'),
            (self.ui.A_19, 'KLAMPO270'), (self.ui.A_20, 'KLAMPO271'), (self.ui.A_21, 'KLAMPO272'),
            (self.ui.A_22, 'KLAMPO273'), (self.ui.A_23, 'KLAMPO274'), (self.ui.A_24, 'KLAMPO295'),
            (self.ui.A_25, 'KLAMPO296'), (self.ui.A_26, 'KLAMPO297'), (self.ui.A_27, 'KLAMPO298'),
            (self.ui.A_28, 'KLAMPO275'), (self.ui.A_29, 'KLAMPO276'), (self.ui.A_30, 'KLAMPO277'),
            (self.ui.A_31, 'KLAMPO278'), (self.ui.A_32, 'KLAMPO279'), (self.ui.A_33, 'KLAMPO280'),
            (self.ui.A_34, 'KLAMPO281'), (self.ui.A_35, 'KLAMPO282'), (self.ui.A_36, 'KLAMPO283'),
            (self.ui.A_37, 'KLAMPO284'), (self.ui.A_38, 'KLAMPO285'), (self.ui.A_39, 'KLAMPO286'),
            (self.ui.A_40, 'KLAMPO287'), (self.ui.A_41, 'KLAMPO288'), (self.ui.A_42, 'KLAMPO289'),
            (self.ui.A_43, 'KLAMPO290'), (self.ui.A_44, 'KLAMPO301'), (self.ui.A_45, 'KLAMPO302'),
            (self.ui.A_46, 'KLAMPO303'), (self.ui.A_47, 'KLAMPO304'), (self.ui.A_48, 'KLAMPO305'),
            (self.ui.A_49, 'KLAMPO306'), (self.ui.A_50, 'KLAMPO307'), (self.ui.A_51, 'KLAMPO308'),
            (self.ui.A_52, 'KLAMPO309'), (self.ui.A_53, 'KLAMPO310'), (self.ui.A_54, 'KLAMPO311'),
            (self.ui.A_55, 'KLAMPO312'), (self.ui.A_56, 'KLAMPO313'), (self.ui.A_57, 'KLAMPO314'),
            (self.ui.A_58, 'KLAMPO315'), (self.ui.A_59, 'KLAMPO316'), (self.ui.A_60, 'KLAMPO317'),
            (self.ui.A_61, 'KLAMPO318'), (self.ui.A_62, 'KLAMPO319'), (self.ui.A_63, 'KLAMPO320'),
            (self.ui.A_64, 'KLAMPO321'), (self.ui.A_65, 'KLAMPO322'), (self.ui.A_66, 'KLAMPO323'),
            (self.ui.A_67, 'KLAMPO324'), (self.ui.A_68, 'KLAMPO325'), (self.ui.A_69, 'KLAMPO326'),
            (self.ui.A_70, 'KLAMPO327'), (self.ui.A_71, 'KLAMPO328'), (self.ui.A_72, 'KLAMPO329'),
            (self.ui.A_73, 'KLAMPO330'), (self.ui.A_74, 'KLAMPO331'), (self.ui.A_75, 'KLAMPO332'),
            (self.ui.A_76, 'KLAMPO333'), (self.ui.A_77, 'KLAMPO335'), (self.ui.A_78, 'KLAMPO336'),
            (self.ui.A_79, 'KLAMPO337'), (self.ui.A_80, 'KLAMPO338'), (self.ui.A_81, 'KLAMPO339'),
            (self.ui.A_82, 'KLAMPO340'), (self.ui.A_83, 'KLAMPO341'),
        ]

        for ui, para in alarm_dis_list:
            if self.local_mem[para]['Val'] == 1:
                ui.setStyleSheet(self.back_color['red'])
            else:
                ui.setStyleSheet(self.back_color['gray'])

    def _update_dis_comp(self):
        def comp_on_off(ui_type, ui_pump, para):
            if ui_type == 1 or ui_type == 2 or ui_type == 3:
                """
                펌프 및 on/off 변수
                """
                if para == 'KLAMPO70':
                    # 검증 영상 촬영 용 ... 나중에 지울 것.
                    if self.local_mem[para]['Val'] == 1:
                        ui_pump.setStyleSheet(self.back_img[f'P_{ui_type}_ON'])
                    else:
                        if self.local_logic['Operation_Strategy'] == 'A' and self.local_mem['KCNTOMS']['Val'] >= 200:
                            ui_pump.setStyleSheet(self.back_img[f'P_{ui_type}_ON'])
                        else:
                            ui_pump.setStyleSheet(self.back_img[f'P_{ui_type}_OFF'])
                else:
                    if self.local_mem[para]['Val'] == 1:
                        ui_pump.setStyleSheet(self.back_img[f'P_{ui_type}_ON'])
                    else:
                        ui_pump.setStyleSheet(self.back_img[f'P_{ui_type}_OFF'])
            elif ui_type == 4:
                """
                Label로 된 변수
                """
                if self.local_mem[para]['Val'] == 1:
                    ui_pump.setStyleSheet(self.back_color['red'])
                else:
                    ui_pump.setStyleSheet(self.back_color['gray'])
            elif ui_type == 5 or ui_type == 6:
                """
                개도가 조절 가능한 Valve 
                """
                if self.local_mem[para]['Val'] == 1:
                    ui_pump.setStyleSheet(self.back_img[f'V_{ui_type - 4}_OPEN'])
                elif self.local_mem[para]['Val'] == 0:
                    ui_pump.setStyleSheet(self.back_img[f'V_{ui_type - 4}_CLOSE'])
                else:
                    ui_pump.setStyleSheet(self.back_img[f'V_{ui_type - 4}_HALF'])
            elif ui_type == 7:
                if para == 'WAFWS1':
                    if self.local_mem['KLAMPO134']['Val'] == 1:
                        if self.local_mem[para]['Val'] == 25:
                            ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                            self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                            self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                        elif self.local_mem[para]['Val'] == 0:
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
                    if self.local_mem['KLAMPO135']['Val'] == 1:
                        if self.local_mem[para]['Val'] == 25:
                            ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                            self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                            self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                        elif self.local_mem[para]['Val'] == 0:
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
                    if self.local_mem['KLAMPO136']['Val'] == 1:
                        if self.local_mem[para]['Val'] == 25:
                            ui_pump.setStyleSheet(self.back_img['V_2_OPEN'])
                            self.ui.V_20.setStyleSheet(self.back_img['V_1_OPEN'])
                            self.ui.V_21.setStyleSheet(self.back_img['V_1_OPEN'])
                        elif self.local_mem[para]['Val'] == 0:
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

        comp_on_off_list = [
            # Aux Feed Water Pump
            (1, self.ui.P_1, 'KLAMPO134'), (1, self.ui.P_2, 'KLAMPO135'), (1, self.ui.P_3, 'KLAMPO136'),
            # Main Feed Water Pump
            (1, self.ui.P_4, 'KLAMPO241'), (1, self.ui.P_5, 'KLAMPO242'), (1, self.ui.P_6, 'KLAMPO243'),
            # Condensor pump
            (3, self.ui.P_7, 'KLAMPO181'), (3, self.ui.P_8, 'KLAMPO182'), (3, self.ui.P_9, 'KLAMPO183'),
            # Charging pump
            (2, self.ui.P_10, 'KLAMPO71'), (2, self.ui.P_11, 'KLAMPO70'), (2, self.ui.P_12, 'KLAMPO69'),
            # RHR Pump
            (2, self.ui.P_13, 'KLAMPO55'),
            # RCP
            (4, self.ui.D_51, 'KLAMPO124'),(4, self.ui.D_52, 'KLAMPO125'),(4, self.ui.D_53, 'KLAMPO126'),
            # Main steam line
            (6, self.ui.V_37, 'BHV108'),   (6, self.ui.V_38, 'BHV208'),   (6, self.ui.V_39, 'BHV308'),
            # Feedwater valve
            (5, self.ui.V_12, 'BFV478'),   (5, self.ui.V_13, 'BFV479'),   (5, self.ui.V_14, 'BFV488'),
            (5, self.ui.V_15, 'BFV489'),   (5, self.ui.V_16, 'BFV498'),   (5, self.ui.V_17, 'BFV499'),
            # AUX FEED VALVE
            (7, self.ui.V_48, 'WAFWS1'),   (7, self.ui.V_49, 'WAFWS2'),   (7, self.ui.V_50, 'WAFWS3'),
            # VALVE
            (5, self.ui.V_1, 'BHV22'),     (6, self.ui.V_40, 'BHSV'),     (6, self.ui.V_41, 'BHSV'),
            (6, self.ui.V_42, 'BHSV'),     (6, self.ui.V_43, 'BHSV'),     (6, self.ui.V_44, 'BHTV'),
            (6, self.ui.V_45, 'BHTV'),     (6, self.ui.V_46, 'BHTV'),     (6, self.ui.V_47, 'BHTV'),
            (6, self.ui.V_36, 'BHV40'),    (6, self.ui.V_35, 'BHV201'),   (6, self.ui.V_51, 'BHV302'),
            (6, self.ui.V_52, 'BHV301'),   (6, self.ui.V_19, 'BHV301'),
            (5, self.ui.V_19, 'BHV8'),     (5, self.ui.V_5, 'BHV1'),      (5, self.ui.V_6, 'BHV1'),
            (5, self.ui.V_7, 'BHV1'),      (5, self.ui.V_8, 'BLV615'),    (5, self.ui.V_9, 'BLV616'),
            (5, self.ui.V_11, 'BLV459'),   (5, self.ui.V_2, 'BHV101'),    (5, self.ui.V_3, 'BHV102'),
            (5, self.ui.V_10, 'BHV39'),    (5, self.ui.V_24, 'BLTV'),     (5, self.ui.V_23, 'BLTV'),
            (5, self.ui.V_27, 'BLTV'),     (5, self.ui.V_28, 'BLTV'),     (5, self.ui.V_31, 'BLTV'),
            (5, self.ui.V_32, 'BLTV'),     (5, self.ui.V_25, 'BLSV'),     (5, self.ui.V_26, 'BLSV'),
            (5, self.ui.V_30, 'BLSV'),     (5, self.ui.V_22, 'BLSV'),     (5, self.ui.V_29, 'BLSV'),
            (5, self.ui.V_33, 'BLSV'),     (5, self.ui.V_19, 'BFV13'),    (5, self.ui.V_18, 'BLV177'),
            (5, self.ui.V_19, 'BHV8'),     (5, self.ui.V_5, 'BHV1'),      (5, self.ui.V_6, 'BHV1'),
            (5, self.ui.V_7, 'BHV1'),      (5, self.ui.V_8, 'BLV615'),    (5, self.ui.V_9, 'BLV616'),
            (5, self.ui.V_11, 'BLV459'),   (5, self.ui.V_2, 'BHV101'),    (5, self.ui.V_3, 'BHV102'),
            (5, self.ui.V_10, 'BHV39'),    (5, self.ui.V_24, 'BLTV'),     (5, self.ui.V_23, 'BLTV'),
            (5, self.ui.V_27, 'BLTV'),     (5, self.ui.V_28, 'BLTV'),     (5, self.ui.V_31, 'BLTV'),
            (5, self.ui.V_32, 'BLTV'),     (5, self.ui.V_25, 'BLSV'),     (5, self.ui.V_26, 'BLSV'),
            (5, self.ui.V_30, 'BLSV'),     (5, self.ui.V_22, 'BLSV'),     (5, self.ui.V_29, 'BLSV'),
            (5, self.ui.V_33, 'BLSV'),     (5, self.ui.V_19, 'BFV13'),    (5, self.ui.V_18, 'BLV177'),
        ]

        for case, ui, para in comp_on_off_list:
            comp_on_off(case, ui, para)

    def _update_dis_csf(self):
        v = {
            'Trip': self.local_mem['KLAMPO9']['Val'],
            # CSF 1 Value 미임계 상태 추적도
            'PowerRange': self.local_mem['ZINST1']['Val'], 'IntermediateRange': self.local_mem['ZINST2']['Val'],
            'SourceRange': self.local_mem['ZINST3']['Val'],
            # CSF 2 Value 노심냉각 상태 추적도
            'CoreExitTemp': self.local_mem['UUPPPL']['Val'],
            'PTCurve': TOOL_PTCurve.PTCureve().Check(Temp=self.local_mem['UAVLEG2']['Val'],
                                                     Pres=self.local_mem['ZINST65']['Val']),
            # CSF 3 Value 열제거원 상태 추적도
            'SG1Nar': self.local_mem['ZINST78']['Val'], 'SG2Nar': self.local_mem['ZINST77']['Val'],
            'SG3Nar': self.local_mem['ZINST76']['Val'],
            'SG1Pres': self.local_mem['ZINST75']['Val'], 'SG2Pres': self.local_mem['ZINST74']['Val'],
            'SG3Pres': self.local_mem['ZINST73']['Val'],
            'SG1Feed': self.local_mem['WFWLN1']['Val'], 'SG2Feed': self.local_mem['WFWLN2']['Val'],
            'SG3Feed': self.local_mem['WFWLN3']['Val'],

            'AllSGFeed': self.local_mem['WFWLN1']['Val'] +
                         self.local_mem['WFWLN2']['Val'] +
                         self.local_mem['WFWLN3']['Val'],
            'SG1Wid': self.local_mem['ZINST72']['Val'], 'SG2Wid': self.local_mem['ZINST71']['Val'],
            'SG3Wid': self.local_mem['ZINST70']['Val'],
            'SG123Wid': [self.local_mem['ZINST72']['Val'], self.local_mem['ZINST71']['Val'], self.local_mem['ZINST70']['Val']],

            # CSF 4 Value RCS 건전성 상태 추적도
            'RCSColdLoop1': self.local_mem['UCOLEG1']['List'], 'RCSColdLoop2': self.local_mem['UCOLEG2']['List'],
            'RCSColdLoop3': self.local_mem['UCOLEG3']['List'], 'RCSPressure': self.local_mem['ZINST65']['Val'],
            'CNSTimeL': self.local_mem['KCNTOMS']['List'],  # PTCurve: ...
            # CSF 5 Value 격납용기 건전성 상태 추적도
            'CTMTPressre': self.local_mem['ZINST26']['Val'], 'CTMTSumpLevel': self.local_mem['ZSUMP']['Val'],
            'CTMTRad': self.local_mem['ZINST22']['Val'],
            # CSF 6 Value RCS 재고량 상태 추적도
            'PZRLevel': self.local_mem['ZINST63']['Val']
        }
        csf_ = {
            'CSF1': TOOL_CSF.CSFTree.CSF1(v['Trip'], v['PowerRange'], v['IntermediateRange'], v['SourceRange'])['L'],
            'CSF2': TOOL_CSF.CSFTree.CSF2(v['Trip'], v['CoreExitTemp'], v['PTCurve'])['L'],
            'CSF3': TOOL_CSF.CSFTree.CSF3(v['Trip'], v['SG1Nar'], v['SG2Nar'], v['SG3Nar'],
                                          v['SG1Pres'], v['SG2Pres'], v['SG3Pres'],
                                          v['SG1Feed'], v['SG2Feed'], v['SG3Feed'])['L'],
            'CSF4': TOOL_CSF.CSFTree.CSF4(v['Trip'], v['RCSColdLoop1'], v['RCSColdLoop2'], v['RCSColdLoop3'],
                                          v['RCSPressure'], v['PTCurve'], v['CNSTimeL'])['L'],
            'CSF5': TOOL_CSF.CSFTree.CSF5(v['Trip'], v['CTMTPressre'], v['CTMTSumpLevel'], v['CTMTRad'])['L'],
            'CSF6': TOOL_CSF.CSFTree.CSF6(v['Trip'], v['PZRLevel'])['L']
        }
        # CSF = {'CSF1':0, ..}
        # 'L': 0 만족, 1: 노랑, 2: 주황, 3: 빨강

        def csf_switch(level=0, display=[0, 0, 0, 0]):
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

        csf_switch(csf_['CSF1'], [self.ui.CSF_1_1, self.ui.CSF_1_2, self.ui.CSF_1_3, self.ui.CSF_1_4])
        csf_switch(csf_['CSF2'], [self.ui.CSF_1_5, self.ui.CSF_1_6, self.ui.CSF_1_7, self.ui.CSF_1_8])
        csf_switch(csf_['CSF3'], [self.ui.CSF_1_9, self.ui.CSF_1_10, self.ui.CSF_1_11, self.ui.CSF_1_12])
        csf_switch(csf_['CSF4'], [self.ui.CSF_1_13, self.ui.CSF_1_14, self.ui.CSF_1_15, self.ui.CSF_1_16])
        csf_switch(csf_['CSF5'], [self.ui.CSF_1_17, self.ui.CSF_1_18, self.ui.CSF_1_19, self.ui.CSF_1_20])
        csf_switch(csf_['CSF6'], [self.ui.CSF_1_21, self.ui.CSF_1_22, self.ui.CSF_1_23, self.ui.CSF_1_24])
        pass

    def _update_dis_op_strategy(self):
        light = ['', '', '']
        if self.local_logic['Operation_Strategy'] == 'N':  light = ['green',    'gray',     'gray']
        if self.local_logic['Operation_Strategy'] == 'A':  light = ['gray',     'yellow',   'gray']
        if self.local_logic['Operation_Strategy'] == 'E':  light = ['gray',     'gray',     'red']
        self.ui.Normal_dis.setStyleSheet(self.back_color[light[0]])
        self.ui.Abnormal_dis.setStyleSheet(self.back_color[light[1]])
        self.ui.Emergen_dis.setStyleSheet(self.back_color[light[2]])

        # _update_dis_op_strategy_log ----------------------------------------------------------------------------------
        st_list = self.local_logic['Operation_Strategy_list']
        get_len = len(self.local_logic['Operation_Strategy_list'])
        if get_len >= 2:
            if st_list[0] != st_list[1]:
                # 상태 변화시 이전 상태 -> 현재 상태
                gen_print = '{} -> {}'.format(st_list[0], st_list[1])
                # 현재 시간 수집
                get_sec = int(self.local_mem["KCNTOMS"]["Val"] / 5)
                gen_time = TOOL_etc.ToolEtc.get_calculated_time(get_sec)
                self.ui.listWidget.addItem(gen_time + gen_print)

        if self.local_logic['Operation_Strategy'] == 'E': self.shmem.append_strategy_list('Emergency')
        if self.local_logic['Operation_Strategy'] == 'A': self.shmem.append_strategy_list('Abnormal')
        if self.local_logic['Operation_Strategy'] == 'N': self.shmem.append_strategy_list('Normal')
        pass

    def _update_dis_indicator(self):
        self.ui.D_50.setText('{:0.2f}'.format(self.local_mem['UHOLEG1']['Val']))  # Hot leg temp loop 1
        self.ui.D_48.setText('{:0.2f}'.format(self.local_mem['UHOLEG2']['Val']))  # Hot leg temp loop 2
        self.ui.D_45.setText('{:0.2f}'.format(self.local_mem['UHOLEG3']['Val']))  # Hot leg temp loop 3
        self.ui.D_15.setText('{:0.2f}'.format(self.local_mem['UCOLEG1']['Val']))  # Cold leg temp loop 1
        self.ui.D_18.setText('{:0.2f}'.format(self.local_mem['UCOLEG2']['Val']))  # Cold leg temp loop 2
        self.ui.D_44.setText('{:0.2f}'.format(self.local_mem['UCOLEG3']['Val']))  # Cold leg temp loop 3
        self.ui.D_21.setText('{:0.2f}'.format(self.local_mem['ZINST58']['Val']))  # PZR pressure
        self.ui.D_9.setText('{:0.2f}'.format(self.local_mem['ZINST46']['Val']))  # CORE outtemp
        self.ui.D_31.setText('{:0.2f}'.format(self.local_mem['ZINST78']['Val']))  # S/G1 level
        self.ui.D_32.setText('{:0.2f}'.format(self.local_mem['ZINST75']['Val']))  # S/G1 pressure
        self.ui.D_36.setText('{:0.2f}'.format(self.local_mem['ZINST77']['Val']))  # S/G2 level
        self.ui.D_35.setText('{:0.2f}'.format(self.local_mem['ZINST74']['Val']))  # S/G2 pressure
        self.ui.D_42.setText('{:0.2f}'.format(self.local_mem['ZINST76']['Val']))  # S/G3 level
        self.ui.D_40.setText('{:0.2f}'.format(self.local_mem['ZINST73']['Val']))  # S/G3 pressure

        self.ui.D_20.setText('{:0.2f}'.format(self.local_mem['ZINST63']['Val']))  # PZR REAL LEVEL
        self.ui.D_12.setText('{:0.2f}'.format(self.local_mem['ZREAC']['Val']))  # CORE_LEVEL
        self.ui.D_14.setText('{:0.2f}'.format(self.local_mem['KBCDO16']['Val']))  # CORE_BORON
        self.ui.D_1.setText('{:0.2f}'.format(self.local_mem['URHRRE']['Val']))  # RHR_TEMP
        self.ui.D_4.setText('{:0.2f}'.format(self.local_mem['WRHRRE']['Val']))  # RHR_FLOW
        self.ui.D_5.setText('{:0.2f}'.format(self.local_mem['PVCT']['Val']))  # VCT_PRESSURE
        self.ui.D_7.setText('{:0.2f}'.format(self.local_mem['ZVCT']['Val']))  # VCT_LEVEL
        self.ui.D_27.setText('{:0.2f}'.format(self.local_mem['UCOND']['Val']))  # COND_TEMP
        self.ui.D_30.setText('{:0.2f}'.format(self.local_mem['ZCOND']['Val']))  # COND_PRESSURE
        self.ui.D_24.setText('{:0.2f}'.format(self.local_mem['ZCNDTK']['Val']))  # CST1_LEVEL
        self.ui.D_25.setText('{:0.2f}'.format(self.local_mem['ZAFWTK']['Val']))  # CST2_LEVEL
        self.ui.D_power.setText('{:0.2f} [%]'.format(self.local_mem['QPROREL']['Val'] * 100))  # POWER
        self.ui.D_elec.setText('{:0.2f} [MWe]'.format(self.local_mem['ZINST124']['Val']))  # POWER

    def _update_dis_autonomous_control(self):
        # TODO ...... 자율 제어 수정
        def _add_dis_list_signal(content):
            if len(self.ui.Auto_list.findItems('{}'.format(content), QtCore.Qt.MatchContains)) == 0:
                get_sec = int(self.local_mem["KCNTOMS"]["Val"] / 5)
                self.ui.Auto_list.addItem('{} {}'.format(TOOL_etc.ToolEtc.get_calculated_time(get_sec), content))

        if self.local_mem['KCNTOMS']['Val'] < 4:
            self.ui.Auto_list.clear()
        else:
            if self.local_logic['Operation_Strategy'] == 'A':
                if self.local_mem['KCNTOMS']['Val'] >= 170 and self.one_1 == False:
                    _add_dis_list_signal('Charging Valve Open')
                    self.one_1 = True
                if self.local_mem['KCNTOMS']['Val'] >= 200 and self.one_2 == False:
                    _add_dis_list_signal('Charging pump 2 start')
                    self.one_2 = False
                pass

            if self.local_logic['Operation_Strategy'] == 'E':
                if self.local_mem['KLAMPO9']['Val'] == 1: _add_dis_list_signal('Reactor trip')
                if self.local_mem['KLAMPO6']['Val'] == 1: _add_dis_list_signal('SI valve open')
                if self.local_mem['KLAMPO4']['Val'] == 1: _add_dis_list_signal('Containment ISO')
                if self.local_mem['KLAMPO2']['Val'] == 1: _add_dis_list_signal('Feedwater ISO')
                if self.local_mem['KLAMPO3']['Val'] == 1: _add_dis_list_signal('Main steam line ISO')
                if self.local_mem['KLAMPO134']['Val'] == 1: _add_dis_list_signal('Aux feed pump 1 start')
                if self.local_mem['KLAMPO135']['Val'] == 1: _add_dis_list_signal('Aux feed pump 2 start')
                if self.local_mem['KLAMPO136']['Val'] == 1: _add_dis_list_signal('Aux feed pump 3 start')
                if self.local_mem['KLAMPO70']['Val'] == 1: _add_dis_list_signal('Charging pump 2 start')
                if self.local_mem['KLAMPO69']['Val'] == 1: _add_dis_list_signal('Charging pump 3 start')
                if self.local_mem['KLAMPO124']['Val'] == 0: _add_dis_list_signal('RCP 1 stop')
                if self.local_mem['KLAMPO125']['Val'] == 0: _add_dis_list_signal('RCP 2 stop')
                if self.local_mem['KLAMPO126']['Val'] == 0: _add_dis_list_signal('RCP 3 stop')

    def _update_function_LCO(self):
        # LCO 3.4.1
        # if not 154.7 < self.local_mem['ZINST65']['Val'] < 161.6 and 286.7 < self.local_mem['ZINST65']['Val'] < 293.3:
        if self.local_mem['KCNTOMS']['Val'] > 400:
            if not 'LCO 3.4.1' in self.local_logic['LCO_Dict'].keys():
                start_time = self.local_mem['KCNTOMS']['Val']
                end_tiem = self.local_mem['KCNTOMS']['Val'] + 7200

                self.shmem.append_lco_dict('LCO 3.4.1',
                                           self.local_mem['KCNTOMS']['Val'],
                                           self.local_mem['KCNTOMS']['Val'] + 7200)

                self.ui.Performace_Mn.addItem(f'{TOOL_etc.ToolEtc.get_calculated_time(int(start_time/5))}'
                                              f'->'
                                              f'{TOOL_etc.ToolEtc.get_calculated_time(int(end_tiem/5))}'
                                              f'\tLCO 3.4.1\tDissatisfaction')
    # ------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    # Gui Test
    app = QApplication(sys.argv)
    w = CNSMainWinBasic()
    w.show()
    sys.exit(app.exec_())