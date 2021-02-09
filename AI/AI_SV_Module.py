import pickle
import pandas as pd
import numpy as np
from collections import deque
import copy


class Signal_Validation:
    def __init__(self, network):
        # minmax Load
        with open('./AI/AI_SV_scaler_in.pkl', 'rb') as f:
            self.scaler_in = pickle.load(f)

        with open('./AI/AI_SV_scaler_out.pkl', 'rb') as f:
            self.scaler_out = pickle.load(f)

        self.network = network

        self.stack_db = deque(maxlen=10)
        self.stack_db_out = deque(maxlen=2)

        self.threshold = [0.011581499203325669, 0.009462367390260244, 0.008903015480589159, 0.009594334339569006,
                          0.031215020667924767, 0.010818916559719643, 0.01049919201077266, 0.01062811011351488,
                          0.010651478620771508, 0.011562519033165936, 0.035823854381993835, 0.039710045714257534,
                          0.033809111781334084, 0.04924519916104178, 0.04715594067619352, 0.042831757003614385,
                          0.008778805078996987, 0.014718878351330346, 0.02059897081470507, 0.027989265704257082,
                          0.0274660154968856, 0.025115614397052698, 0.03167101131485395, 0.02955934155605648,
                          0.06220589578881775, 0.05572199208638379]
        self.out_len = len(self.threshold)

    def predict_action(self, mem):
        if mem['KCNTOMS']['Val'] > 500:
            mem['UUPPPL']['Val'] = 500

        self.make_input_data(mem=mem)
        self.make_output_data(mem=mem)

        # (1, 397) -> (10, 397)
        input_array = np.array(self.stack_db)

        if input_array.shape[0] == 10:
            predict_result = self.network.predict(input_array)

            # predict_result = self.scaler_out.inverse_transform(predict_result)
            # predict_result
            # (10, 397) -> [-1, 397]

            net_out = predict_result[-1]                        # 26
            original_out = np.array(self.stack_db_out[-1])      # 26

            out = np.square(net_out - original_out)

            sw = []
            for i, val in enumerate(list(out)):
                if val > self.threshold[i]:
                    sw.append(1)
                else:
                    sw.append(0)

            return sw
        else:
            return [0 for _ in range(self.out_len)]

    def make_input_data(self, mem):
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
        input_para = [mem[para]['Val'] for para in self.in_col]
        out_min_max = self.scaler_in.transform([input_para])[0]

        self.stack_db.append(out_min_max)

    def make_output_data(self, mem):
        self.out_col = ['ZINST103', 'WFWLN1', 'WFWLN2', 'WFWLN3', 'ZINST100', 'ZINST101', 'ZINST85', 'ZINST86',
                        'ZINST87', 'ZINST99', 'UCHGUT', 'UCOLEG1', 'UCOLEG2', 'UCOLEG3', 'UPRZ', 'UUPPPL', 'WNETLD',
                        'ZINST63', 'ZINST65', 'ZINST79', 'ZINST80', 'ZINST81', 'ZINST70', 'ZINST72', 'ZINST73',
                        'ZINST75']

        output_para = [mem[para]['Val'] for para in self.out_col]
        out_min_max = self.scaler_out.transform([output_para])[0]

        self.stack_db_out.append(out_min_max)