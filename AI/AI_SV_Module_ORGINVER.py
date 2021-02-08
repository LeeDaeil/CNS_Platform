import pickle
import pandas as pd
import numpy as np
from collections import deque
import copy


class Signal_Validation:
    def __init__(self, net, fault_type=3, select_signal=0):
        # net 받기
        self.net = net
        #
        self.select_signal = select_signal

        self.threshold = [0.011581499203325669, 0.009462367390260244, 0.008903015480589159, 0.009594334339569006,
                          0.031215020667924767, 0.010818916559719643, 0.01049919201077266, 0.01062811011351488,
                          0.010651478620771508, 0.011562519033165936, 0.035823854381993835, 0.039710045714257534,
                          0.033809111781334084, 0.04924519916104178, 0.04715594067619352, 0.042831757003614385,
                          0.008778805078996987, 0.014718878351330346, 0.02059897081470507, 0.027989265704257082,
                          0.0274660154968856, 0.025115614397052698, 0.03167101131485395, 0.02955934155605648,
                          0.06220589578881775, 0.05572199208638379]
        self.in_col = ['BHSV', 'BHTV', 'BLSV', 'BLTV', 'BRHCV', 'BRHSV', 'KLAMPO241', 'KLAMPO242', 'KLAMPO243', 'UCOND',
                       'ULPHOUT', 'ZAFWTK', 'ZINST103', 'BFV122', 'BHV1', 'BHV2', 'BLV459', 'BLV616', 'BPV145',
                       'URHXUT', 'WBOAC', 'WDEWT', 'KLAMPO234', 'ZINST119', 'ZINST121', 'BHV108', 'BHV208', 'BHV308',
                       'BHV501', 'WFWLN1', 'WFWLN2', 'WFWLN3', 'ZINST100', 'ZINST101', 'ZINST85', 'ZINST86', 'ZINST87',
                       'ZINST99', 'BFV478', 'BFV479', 'BFV488', 'BFV498', 'BFV499', 'BHV502', 'KBCDO20', 'KBCDO21',
                       'KBCDO22', 'KLAMPO124', 'KLAMPO125', 'KLAMPO126', 'KSWO132', 'KSWO133', 'KSWO134', 'UAVLEG1',
                       'UAVLEG2', 'UAVLEG3', 'UCHGUT', 'UCOLEG1', 'UCOLEG2', 'UCOLEG3', 'UHOLEG1', 'UHOLEG2', 'UHOLEG3',
                       'UNRHXUT', 'UPRZ', 'UUPPPL', 'WCHGNO', 'WNETLD', 'ZINST36', 'ZINST63', 'ZINST65', 'ZINST67',
                       'ZINST68', 'ZINST69', 'ZINST79', 'ZINST80', 'ZINST81', 'ZPRZSP', 'ZPRZUN', 'ZINST70', 'ZINST72',
                       'ZINST73', 'ZINST75', 'ZINST76', 'ZINST77','ZINST78', 'KFAST', 'KBCDO10', 'KBCDO11', 'KBCDO3',
                       'KBCDO4', 'KBCDO5', 'KBCDO6', 'KBCDO7', 'KBCDO8', 'KBCDO9', 'KLAMPO21', 'KLAMPO22', 'ZINST1',
                       'CIODMPC', 'QPROLD', 'UAVLEGS', 'ZINST124', 'BFWMAI', 'BPV145I', 'CBRWIN', 'CIOD', 'DECH',
                       'DECH1', 'DENEUO', 'DNEUTR', 'EAFWTK', 'EHPHA', 'EHPHB', 'ELPHA', 'ELPHB', 'FCDP1', 'FCDP2',
                       'FCDP3', 'FCWP', 'FEICDP', 'FEIFWP', 'FFWP1', 'FFWP2', 'FFWP3', 'FNET', 'HHPTEX', 'HRHDT',
                       'HSDMP', 'HTIN', 'KBCDO23', 'KCONTS9', 'KEXCTB', 'KFWP1', 'KFWP2', 'KFWP3', 'KIRTBS',
                       'KLAMPO103', 'KLAMPO105', 'KLAMPO138', 'KLAMPO140', 'KLAMPO142', 'KLAMPO152', 'KLAMPO154',
                       'KLAMPO171', 'KLAMPO173', 'KLAMPO180', 'KLAMPO194', 'KLAMPO196', 'KLAMPO49', 'KLAMPO60',
                       'KLAMPO66', 'KLAMPO79', 'KLAMPO97', 'KMOSTP', 'KOILTM', 'KPERMS10', 'KPERMS13', 'KPERMS7',
                       'KPRTBS', 'KRCP1', 'KRCP2', 'KRCP3', 'KRILM', 'KTBREST', 'KTLC', 'KTSIS', 'KTSISC', 'KZBANK1',
                       'KZBANK2', 'KZBANK3', 'KZBANK4', 'KZBANK5', 'KZBANK6', 'KZBANK7', 'KZBANK8', 'KZROD1', 'KZROD10',
                       'KZROD11', 'KZROD12', 'KZROD13', 'KZROD14', 'KZROD15', 'KZROD16', 'KZROD17', 'KZROD18',
                       'KZROD19', 'KZROD2', 'KZROD20', 'KZROD21', 'KZROD22', 'KZROD23', 'KZROD24', 'KZROD25', 'KZROD26',
                       'KZROD27', 'KZROD28', 'KZROD29', 'KZROD3', 'KZROD30', 'KZROD31', 'KZROD32', 'KZROD33', 'KZROD34',
                       'KZROD35', 'KZROD36', 'KZROD37', 'KZROD38', 'KZROD39', 'KZROD4', 'KZROD40', 'KZROD41', 'KZROD42',
                       'KZROD43', 'KZROD44', 'KZROD45', 'KZROD46', 'KZROD47', 'KZROD48', 'KZROD49', 'KZROD5', 'KZROD50',
                       'KZROD51', 'KZROD52', 'KZROD6', 'KZROD7', 'KZROD8', 'KZROD9', 'PCDTB', 'PCNDS', 'PFWP',
                       'PFWPOUT', 'PHDTK', 'PHPTIN', 'PLETDB', 'PLETIN', 'PPRZ', 'PPRZCO', 'PPRZLP', 'PPRZN', 'PPRZW',
                       'PRHTR', 'PSG1', 'PSG2', 'PSG3', 'PSGLP', 'PSGWM', 'PTIN', 'PTINWM', 'PWRHFX', 'QLDSET', 'QLOAD',
                       'QLRSET', 'QNET', 'QPRONOR', 'QPROREL', 'QTHNOR', 'UCCWNR', 'UCCWSW', 'UCHGIN', 'UCNDS', 'UCOOL',
                       'UFDW', 'UHPHOA', 'UHPHOB', 'ULPHOA', 'ULPHOB', 'UMAXDT', 'UNORDT', 'URHDT', 'URHTR', 'UTIN',
                       'VNET', 'VRWST', 'WAUXSP', 'WBHFWP', 'WCDHTR', 'WCDPO', 'WCWAT', 'WDEMI', 'WFDW', 'WFWBYP1',
                       'WFWBYP2', 'WFWBYP3', 'WFWCNT1', 'WFWCNT2', 'WFWCNT3', 'WFWP', 'WFWPBY', 'WFWPOUT', 'WGSL',
                       'WHDTP', 'WHPDRNA', 'WHPDRNB', 'WHPDTA', 'WHPDTB', 'WHPHBYA', 'WHPHBYB', 'WHPHDT', 'WHPHINA',
                       'WHPHINB', 'WHPRH', 'WHPSRQA', 'WHPSRQB', 'WHPT', 'WHPTEX', 'WHPTEXA', 'WHPTEXB', 'WLPDRNA',
                       'WLPDRNB', 'WLPHBYA', 'WLPHBYB', 'WLPHCD', 'WLPHINA', 'WLPHINB', 'WLPHOUT', 'WLPT', 'WLPTC',
                       'WLPTEX', 'WLPTEXA', 'WLPTEXB', 'WLV616', 'WNETCH', 'WRHDRN', 'WRHDRNA', 'WRHDRNB', 'WRHDT',
                       'WRHFWP', 'WRHSTM', 'WSGRCP1', 'WSGRCP2', 'WSGRCP3', 'WSTM1', 'WSTM2', 'WSTM3', 'WTIN', 'XPEINP',
                       'XPEOUT', 'XSEINP', 'XSEOUT', 'XSMINJ', 'XSMOUT', 'YNET', 'ZBANK', 'ZHPHA', 'ZHPHB', 'ZINST10',
                       'ZINST104', 'ZINST106', 'ZINST109', 'ZINST110', 'ZINST114', 'ZINST124', 'ZINST126', 'ZINST37',
                       'ZINST38', 'ZINST39', 'ZINST40', 'ZINST41', 'ZINST43', 'ZINST44', 'ZINST46', 'ZINST49',
                       'ZINST50', 'ZINST51', 'ZINST52', 'ZINST53', 'ZINST54', 'ZINST57', 'ZINST58', 'ZINST59', 'ZINST6',
                       'ZINST60', 'ZINST61', 'ZINST62', 'ZINST64', 'ZINST82', 'ZINST83', 'ZINST84', 'ZINST91',
                       'ZINST92', 'ZINST94', 'ZINST95', 'ZINST96', 'ZLPHA', 'ZLPHB', 'ZPRZ', 'ZPRZNO', 'ZSGN1', 'ZSGN2',
                       'ZSGN3', 'ZSGNOR1', 'ZSGNOR2', 'ZSGNOR3', 'ZSGW1', 'ZSGW2', 'ZSGW3']
        self.out_col = ['ZINST103', 'WFWLN1', 'WFWLN2', 'WFWLN3', 'ZINST100', 'ZINST101', 'ZINST85', 'ZINST86',
                        'ZINST87', 'ZINST99', 'UCHGUT', 'UCOLEG1', 'UCOLEG2', 'UCOLEG3', 'UPRZ', 'UUPPPL', 'WNETLD',
                        'ZINST63', 'ZINST65', 'ZINST79', 'ZINST80', 'ZINST81', 'ZINST70', 'ZINST72', 'ZINST73',
                        'ZINST75']
        self.ylabel = ['FEEDWATER PUMP OUTLET PRESS', 'FEEDWATER LINE #1 FLOW (KG-SEC).',
                       'FEEDWATER LINE #2 FLOW (KG-SEC).', 'FEEDWATER LINE #3 FLOW (KG-SEC).',
                       'FEEDWATER TEMP', 'MAIN STEAM FLOW', 'STEAM LINE 3 FLOW', 'STEAM LINE 2 FLOW',
                       'STEAM LINE 1 FLOW', 'MAIN STEAM HEADER PRESSURE', 'CHARGING LINE OUTLET TEMPERATURE',
                       'LOOP #1 COLDLEG TEMPERATURE.', 'LOOP #2 COLDLEG TEMPERATURE.', 'LOOP #3 COLDLEG TEMPERATURE.',
                       'PRZ TEMPERATURE.', 'CORE OUTLET TEMPERATURE.', 'NET LETDOWN FLOW.', 'PRZ LEVEL',
                       'PRZ PRESSURE(WIDE RANGE)', 'LOOP 3 FLOW', 'LOOP 2 FLOW', 'LOOP 1 FLOW', 'SG 3 LEVEL(WIDE)',
                       'SG 1 LEVEL(WIDE)', 'SG 3 PRESSURE', 'SG 1 PRESSURE']
        self.input_num = ['12', '29', '30', '31', '32', '33', '34', '35', '36', '37', '56', '57', '58', '59', '64',
                          '65', '67', '69', '70', '74', '75', '76', '79', '80', '81', '82']
        self.output_num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
                           '17', '18', '19', '20', '21', '22', '23', '24', '25']
        self.High = ['100', '500', '500', '500', '500', '150', '500', '500', '500', '80', '300', '600', '600', '600',
                     '600', '600', '10', '80', '180', '150', '150', '150', '100', '100', '100', '100']
        self.Low = ['', '', '', '', '0', '', '', '', '', '', '0', '0', '0', '0', '0', '0', '', '', '0', '', '', '', '0',
                    '0', '0', '0']
        self.Current = ['', '', '', '', '0', '', '', '', '', '', '0', '0', '0', '0', '0', '0', '', '', '0', '', '', '',
                        '0', '0', '0', '0']
        self.select_fault_type = fault_type  # {0:high, 1:low, 2:current, 3:normal}
        self.select_input_signal = int(self.input_num[self.select_signal])  # you can choice one signal
        self.select_output_signal = int(self.output_num[self.select_signal])  # you can choice one signal
        self.select_high = self.High[self.select_signal]
        self.select_low = self.Low[self.select_signal]
        self.select_current = self.Current[self.select_signal]
        self.stack_data = deque(maxlen=2)

        self.tick = 0

        # minmax Load
        with open('./AI/AI_SV_scaler_in.pkl', 'rb') as f:
            self.scaler_in = pickle.load(f)

        with open('./AI/AI_SV_scaler_out.pkl', 'rb') as f:
            self.scaler_out = pickle.load(f)

    def step(self, mem):
        """
        CNS mem 값을 받고 network predict 한 값을 반환함.

        :param mem: CNS mem 받음
        :return: {'Para': val, ... }
        """
        get_db = self.scaler_in.transform([[mem[para]['Val'] for para in self.in_col]])
        fin_out = self.scaler_out.inverse_transform(self.net.predict(get_db))[0]
        fin_out_add_label = {key: fin_out[i] for key, i in zip(self.out_col, range(len(self.out_col)))}
        return fin_out_add_label

    def SV_result(self, db):
        while True:
            real_data = db[self.in_col]
            self.stack_data.append(real_data)
            if len(self.stack_data) < 2:
                pass
            else:
                pd_real_data_1 = self.stack_data[0]
                pd_real_data_2 = self.stack_data[1]

                test_in_1 = pd_real_data_1
                test_out_1 = test_in_1[self.out_col]
                test_in = pd_real_data_2
                # test_in = test_in.apply(creat_noise)
                test_out = test_in[self.out_col]

                # test_out = test_out.apply(creat_noise)
                test_A_in = copy.deepcopy(test_in)

                test_A_out = copy.deepcopy(test_out)

                # print(test_in)
                if self.tick >= 300:
                    if self.select_fault_type == 0:
                        test_in.iloc[:, self.select_input_signal] = int(self.select_high)
                        test_out.iloc[:, self.select_output_signal] = int(self.select_high)
                    elif self.select_fault_type == 1:
                        if self.Low == '':
                            print('Not define low fault')
                        else:
                            test_in.iloc[:, self.select_input_signal] = int(self.select_low)
                            test_out.iloc[:, self.select_output_signal] = int(self.select_low)
                    elif self.select_fault_type == 2:
                        if self.Current == '':
                            print('Not define current fault')
                        else:
                            test_in.iloc[:, self.select_input_signal] = test_in_1.iloc[:, self.select_input_signal]
                            test_out.iloc[:, self.select_output_signal] = test_out_1.iloc[:, self.select_output_signal]
                    elif self.select_fault_type == 3:
                        print('No fault signal')

                test_in = pd.DataFrame(self.scaler_in.transform(test_in), columns=self.in_col, index=[self.tick])
                test_out = pd.DataFrame(self.scaler_out.transform(test_out), columns=self.out_col, index=[self.tick])

                predictions_test = self.network.SV_model.predict(test_in)
                p_test = pd.DataFrame(predictions_test, columns=self.out_col, index=[self.tick])

                p_test_scale = copy.deepcopy(p_test)
                p_test = pd.DataFrame(self.scaler_out.inverse_transform(p_test), columns=self.out_col, index=[self.tick])

                test_out_scale = copy.deepcopy(test_out)
                test_out = pd.DataFrame(self.scaler_out.inverse_transform(test_out), columns=self.out_col, index=[self.tick])

                return test_in, test_out, test_A_in, test_A_out, p_test, test_out_scale, p_test_scale

    def run(self):
        app = []
        for time in range(len(self.data)):
            read_data_step = self.data.iloc[time:time + 1, ]
            # print('=======================================================================')
            # pack_data = self.SV_plot(read_data_step)
            pack_data = self.SV_result(read_data_step)
            self.tick += 1
            print(self.tick)
        #     app.append(pack_data)
        # with open('all_data.pkl', 'wb') as f:
        #     pickle.dump(app, f)


if __name__ == '__main__':
    read = pd.read_csv('12_10020_30_0_0_5.csv')
    data = Signal_Validation(fault_type=3, select_signal=0)
    data.run()