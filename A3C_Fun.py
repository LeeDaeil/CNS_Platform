import multiprocessing
import time


class A3C_Process_Module(multiprocessing.Process):
    ## 단순한 값만 읽어 오는 예제
    def __init__(self, mem, net_type='DNN', Top_title = 'Untitle'):
        multiprocessing.Process.__init__(self)
        self.top_title = Top_title
        self.all_mem = mem
        self.nub_agent = len(self.all_mem)
        # self.all_mem[0] : 1번 에이전트의 메모리
        # self.all_mem[0][0] : 1번 에이전트의 메모리 중 Main 메모리
        # self.all_mem[0][0]['ZSGNOR1'] : 1번 에이전트의 메모리 중 Main 메모리에서 'ZSG..'의 정보

        # 네트워크 정의 부분 ================================
        if True:
            self.net_type = net_type
            if self.net_type == 'DNN':
                self.action_dim = 3
                self.state_dim = 5
                self.time_dim = 0
            elif self.net_type == 'LSTM':
                self.action_dim = 3
                self.state_dim = 5
                self.time_dim = 10
            else:
                print('정의되지 않은 네트워크 입니다.')
        # ===================================================

    def run(self):
        from A3C_Network import A3C
        import tensorflow as tf
        from keras.backend.tensorflow_backend import set_session
        # 텐서보드에 데이터를 저장하기 위한 변수 선언
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        set_session(tf.Session(config=config))
        summary_writer = tf.summary.FileWriter('./tb_{}'.format(self.top_title))

        # 네트워크 클래스 호출해옴
        Network_model = A3C(self.action_dim, self.state_dim, self.time_dim, self.net_type, self.nub_agent,
                            self.all_mem)
        Network_model.train(summary_writer)