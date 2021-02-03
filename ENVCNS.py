from TOOL.TOOL_CNS_UDP_FAST import CNS


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

    def _send_control_save(self, zipParaVal):
        super(ENVCNS, self)._send_control_save(para=zipParaVal[0], val=zipParaVal[1])

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
        ActOrderBook = {
            'BPV145Man': (['KSWO89'], [1]),
            'BFV122Man': (['KSWO100'], [1]),
            'OpenHV41_HV3': (['BHV41', 'KHV43'], [1, 1]),
            'CloseHV41_HV3': (['BHV41', 'KHV43'], [0, 0]),
            'OpenLet': (['BHV1', 'BHV2', 'BLV459'], [1, 1, 1]),
            'CloseLet': (['BHV1', 'BHV2', 'BLV459'], [0, 0, 0]),
        }
        # self._send_control_save(ActOrderBook['CloseHV41_HV3'])

        # Done Act
        self._send_control_to_cns()
        return AMod

    def step(self, A):
        """
        A를 받고 1 step 전진
        :param A: [Act], numpy.ndarry, Act는 numpy.float32
        :return: 최신 state와 reward done 반환
        """
        # Old Data (time t) ---------------------------------------
        AMod = self.send_act(A)
        # self.want_tick = int(5)

        # New Data (time t+1) -------------------------------------
        super(ENVCNS, self).step()
        self._append_val_to_list()
        self.ENVStep += 1

        # ----------------------------------------------------------
        return AMod

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