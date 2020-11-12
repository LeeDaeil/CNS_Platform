import tensorflow as tf
import numpy as np
import keras.backend as K
import threading
from threading import Lock
from keras.models import Model
from keras.layers import Dense, Input, Conv1D, MaxPooling1D, Flatten, CuDNNLSTM
from keras.optimizers import RMSprop
from time import sleep

# import os
# os.environ['CUDA_VISIBLE_DEVICES'] = ''

class TD3:
    '''
    TD3 네트워크
        - 구조
            [======
            [*******Top*******]-[*******Mid********]-[*******Bot********]-[*******Bot********]-[*******Bot********]
            [---TD3_Main.py---]-[----CNS_UDP.py----]
                      │        [------UDP_net-----]----------┐
                      │                             [-------mem--------]----------┐
                      │                                                           │
                      └--------[----TD3_Fun.py----]                               │
                                [TD3_Process_Module]-[--TD3_Network.py--]          │
                                                     [-------TD3--------]┬[-----Worker_1-----]-[----CNS_UDP.py----]
                                                                                                [-CNS_Send_Signal--]
    '''

    def __init__(self, action_dim, state_dim, time_dim, net_type, nub_agent, shared_mem, gamma=0.99, lr=0.0001):
        ''' 네트워크에 대한 정보'''
        self.nub_agent = nub_agent
        self.action_dim, self.state_dim, self.time_dim, self.net_type = action_dim, state_dim, time_dim, net_type
        self.shared_mem = shared_mem # 에이전트들의 메모리 주소를 가져옴

        self.learning_interval = 30
        self.max_episode = 20000
        self.gamma = gamma
        self.lr = lr
        # 공유되는 actor와 critic 네트워크를 작성
        self.body_network = self.build_network_model(net_type=self.net_type, in_pa=self.state_dim,
                                                     time_leg=self.time_dim)
        self.actor = Actor(state_dim=self.state_dim, action_dim=self.action_dim, network=self.body_network,
                           lr=self.lr)
        self.critic = Critic(state_dim=self.state_dim, action_dim=self.action_dim, network=self.body_network,
                             lr=self.lr)
        self.act_op = self.actor.optimizer()
        self.cri_op = self.critic.optimizer()

    def build_network_model(self, net_type='DNN', in_pa=1, time_leg=1):
        # 네트워크 모델 - 의존성 없음
        if True:
            if net_type == 'DNN':
                state = Input(batch_shape=(None, in_pa))
                shared = Dense(32, input_dim=in_pa, activation='relu', kernel_initializer='glorot_uniform')(state)
                # shared = Dense(48, activation='relu', kernel_initializer='glorot_uniform')(shared)

            elif net_type == 'CNN' or net_type == 'LSTM' or net_type == 'CLSTM':
                state = Input(batch_shape=(None, time_leg, in_pa))
                if net_type == 'CNN':
                    shared = Conv1D(filters=10, kernel_size=3, strides=1, padding='same')(state)
                    shared = MaxPooling1D(pool_size=2)(shared)
                    shared = Flatten()(shared)

                elif net_type == 'LSTM':
                    shared = CuDNNLSTM(16)(state)

                elif net_type == 'CLSTM':
                    shared = Conv1D(filters=10, kernel_size=3, strides=1, padding='same')(state)
                    shared = MaxPooling1D(pool_size=2)(shared)
                    shared = CuDNNLSTM(8)(shared)
        return Model(state, shared)

    def policy_action(self, s):
        print(self.actor.predict(s))
        return np.random.choice(np.arange(self.action_dim), 1, p=self.actor.predict(s).ravel())[0]

    def discount(self, r):
        discounted_r, cumul_r = np.zeros_like(r), 0
        for t in reversed(range(0, len(r))):
            cumul_r = r[t] + cumul_r * self.gamma
            discounted_r[t] = cumul_r
        return discounted_r

    def train_models(self, states, actions, rewards):
        """ Update all_dig and critic networks from experience
        """
        # Compute discounted rewards and Advantage (TD. Error)
        discounted_rewards = self.discount(rewards)
        state_values = self.critic.predict(np.array(states))
        advantages = discounted_rewards - np.reshape(state_values, len(state_values))
        # Networks optimization
        self.act_op([states, actions, advantages])
        self.cri_op([states, discounted_rewards])

    def train(self, summary_writer):
        Worker = worker()
        worker_list = [threading.Thread(
                target=Worker.training_thread,
                # daemon=True,
                args=(self, self.max_episode, self.shared_mem[nub_agent], self.action_dim, self.learning_interval,
                      summary_writer, nub_agent)) for nub_agent in range(self.nub_agent)]

        for __ in worker_list:
            __.start()
            sleep(1)

    def save_weights(self, path):
        path += '_LR_{}'.format(self.lr)
        self.actor.save(path)
        self.critic.save(path)

    def load_weights(self, path_actor, path_critic):
        self.critic.load_weights(path_critic)
        self.actor.load_weights(path_actor)


class Agent:

    '''에이전트 모델'''

    def __init__(self, state_dim, action_dim, lr, tau=0.001):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.tau = tau
        self.rms_optimizer = RMSprop(lr=lr, epsilon=0.1, rho=0.99)

    def fit(self, inp, targ):
        """ Perform one epoch of training
        """
        self.model.fit(inp, targ, epochs=1, verbose=0)

    def predict(self, inp):
        """ Critic Value Prediction
        """
        return self.model.predict(inp)


class Critic(Agent):
    ''' Critic 모델 '''

    def __init__(self, state_dim, action_dim, network, lr):
        # Agent로부터 값을 상속받음.
        Agent.__init__(self, state_dim, action_dim, lr)
        self.model = self.addHead(network)
        self.discounted_r = K.placeholder(shape=(None,))
        # Pre-compile for threading
        self.model._make_predict_function()
        self.model.summary()

    def addHead(self, network):
        '''Critic 모델의 최종 출력값'''
        x = Dense(128, activation='relu')(network.output)
        out = Dense(1, activation='linear')(x)
        return Model(network.input, out)

    def optimizer(self):
        """ Critic Optimization: Mean Squared Error over discounted rewards
        """
        critic_loss = K.mean(K.square(self.discounted_r - self.model.output))
        updates = self.rms_optimizer.get_updates(self.model.trainable_weights, [], critic_loss)
        return K.function([self.model.input, self.discounted_r], [], updates=updates)

    def save(self, path):
        self.model.save_weights(path + '_critic.h5')

    def load_weights(self, path):
        self.model.load_weights(path)


class Actor(Agent):
    ''' Actor 모델 '''

    def __init__(self, state_dim, action_dim, network, lr):
        # Agent로부터 값을 상속받음.
        Agent.__init__(self, state_dim, action_dim, lr)
        self.model = self.addHead(network)
        self.action_pl = K.placeholder(shape=(None, self.action_dim))
        self.advantages_pl = K.placeholder(shape=(None,))
        # Pre-compile for threading
        self.model._make_predict_function()
        self.model.summary()

    def addHead(self, network):
        """ Assemble Actor network to predict probability of each action
        """
        x = Dense(128, activation='relu')(network.output)
        out = Dense(self.action_dim, activation='softmax')(x)
        return Model(network.input, out)

    def optimizer(self):
        """ Actor Optimization: Advantages + Entropy term to encourage exploration
        (Cf. https://arxiv.org/abs/1602.01783)
        """
        weighted_actions = K.sum(self.action_pl * self.model.output, axis=1)
        eligibility = K.log(weighted_actions + 1e-10) * K.stop_gradient(self.advantages_pl)
        entropy = K.sum(self.model.output * K.log(self.model.output + 1e-10), axis=1)
        loss = 0.001 * entropy - K.sum(eligibility)

        updates = self.rms_optimizer.get_updates(self.model.trainable_weights, [], loss)
        return K.function([self.model.input, self.action_pl, self.advantages_pl], [], updates=updates)

    def save(self, path):
        self.model.save_weights(path + '_actor.h5')

    def load_weights(self, path):
        self.model.load_weights(path)


#====================================================================================================================#
episode = 0
lock = Lock()
from Temp import A3C_Port as AP


class worker:
    def training_thread(self, A3C_agent, max_episode, shared_mem, action_dim, learning_interval, summary_writer, nub_agent):
        '''
        A3C Network 단일 에이전트 부분
        - Shared_mem
            : self.shared_mem[nub_agent] - 해당 에이전트의 단독적인 메모리가 보내짐.

            : self.all_mem[0] : 1번 에이전트의 메모리 <- 현재 수준에 전달된 메모리
            : self.all_mem[0][0] : 1번 에이전트의 메모리 중 Main 메모리
            : self.all_mem[0][0]['ZSGNOR1'] : 1번 에이전트의 메모리 중 Main 메모리에서 'ZSG..'의 정보

            : 현재 클레스에서 값을 접근하려면
            ex) shared_mem[0]['ZSGNOR1']

            : CNS로 보내질 메모리 - shared_mem[0]
                - CNS내에서는 shared_mem['ZSGNOR1']로 접근
        - nub_agent
            : 에이전트 1번의 경우 원격 컴퓨터의 포트는 7001번 CNS도 7001번
            : AP.IP_PORT[nub_agent]['CNS_IP'] 또는 AP.IP_PORT[nub_agent]['CNS_Port']로 사용
        - 입력 데이터 예시
            1. DNN
                input_data = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
                :> shape : (1,5) [5: input_para]
            2. LSTM
                input_data = np.array([[[0.1, 0.2, 0.3, 0.4, 0.5], [0.1, 0.2, 0.3, 0.4, 0.5]]])
                :> shape : (1,2,5) [2: time_leg][5: input_para]
            3. 입력
                A3C_agent.policy_action(input_data)

        '''

        global episode
        self.shard_mem = shared_mem[0]
        #=== CNS 선언 ===============================================================================================#
        self.CNS = CNS(mem=shared_mem[0], ip=AP.IP_PORT[nub_agent]['CNS_IP'], port=AP.IP_PORT[nub_agent]['CNS_Port'],
                       s_para=['KSWO33', 'KSWO32', 'KSWO31', 'KSWO30', 'KSOW29'],
                       t_para=['Reward', 'Action', 'Done'])
        # === CNS 선언 ===============================================================================================#
        self.CNS.cns_initial()  # CNS 초기화를 요청

        time, cumul_reward, done = 0, 0, False
        while episode < max_episode:
            # LSTM 대기 용
            for _ in range(4):
                self.pass_step()

            old_state = self.CNS.state_mem.iloc[-2:].values

            actions, states, rewards = [], [], []
            for _ in range(0, 5):
                a = A3C_agent.policy_action([[old_state]])
                r, done = self.step(a)
                # Memorize (s, a, r) for training
                actions.append(a)
                rewards.append(r)
                states.append(old_state)
                # New state
                new_state = self.CNS.state_mem.iloc[-2:].values
                # Update current state
                old_state = new_state
                cumul_reward += r
                time += 1
            self.CNS.save_db()
            print('done and train')

            # lock.acquire()
            A3C_agent.train_models(states, actions, rewards)
            # lock.release()
            actions, states, rewards = [], [], []

            print('done')

            a = False
            if a:
                while not done and episode < max_episode:
                    # Asynchronous training
                    if (time % learning_interval == 0 or done):
                        lock.acquire()
                        A3C_agent.train_models(states, actions, rewards, done)
                        lock.release()
                        actions, states, rewards = [], [], []

                # Export results for Tensorboard
                score = self.tfSummary('score', cumul_reward)
                summary_writer.add_summary(score, global_step=episode)
                summary_writer.flush()
            # Update episode count
            with lock:
                if (episode < max_episode):
                    episode += 1

    def tfSummary(self, tag, val):
        """ Scalar Value Tensorflow Summary
        """
        return tf.Summary(value=[tf.Summary.Value(tag=tag, simple_value=val)])

    def step(self, action):
        if action == 0:
            self.CNS.cns_control(['KSWO33', 'KSWO32'], [1, 0])
        elif action == 1:
            self.CNS.cns_control(['KSWO33', 'KSWO32'], [0, 0])
        elif action == 2:
            self.CNS.cns_control(['KSWO33', 'KSWO32'], [0, 1])
        else:
            pass
        self.CNS.cns_run()
        # ================================================================================================
        done = False
        r = 1
        self.CNS.update_train_db_structure(r=r, a=action, done=done)
        self.CNS.update_state_db_structure([
            self.shard_mem['KSWO33']['L'][-1],
            self.shard_mem['KSWO33']['L'][-1]/5,
            self.shard_mem['KSWO33']['L'][-1]/4,
            self.shard_mem['KSWO33']['L'][-1]/3,
            self.shard_mem['KSWO33']['L'][-1]/2,
        ])
        return r, done

    def pass_step(self):
        self.CNS.cns_run()
        self.CNS.update_train_db_structure(r=0, a=0, done=False)
        self.CNS.update_state_db_structure([
            self.shard_mem['KSWO33']['L'][-1],
            self.shard_mem['KSWO33']['L'][-1]/5,
            self.shard_mem['KSWO33']['L'][-1]/4,
            self.shard_mem['KSWO33']['L'][-1]/3,
            self.shard_mem['KSWO33']['L'][-1]/2,
        ])

#====================================================================================================================#
from CNS_Send_UDP import CNS_Send_Signal as CNSUDP
import time
import pandas as pd


class Control_data:
    '''
    훈련 데이터를 저장 및 관리하는 class
    '''

    def __init__(self, s_para, t_para):
        self.state_parameter = s_para
        self.train_parameter = t_para
        self.state_mem = self.initial_db_structure(self.state_parameter)
        self.train_mem = self.initial_db_structure(self.train_parameter)

    def update_state_db_structure(self, value):
        self.state_mem.loc[len(self.state_mem)] = value
        return 0

    def update_train_db_structure(self, r, a, done):
        self.train_mem.loc[len(self.train_mem)] = [r, a, done]
        return 0
    
    def save_db(self):
        for _ in self.train_mem.columns:
            self.state_mem[_] = self.train_mem[_]
        self.state_mem.to_csv('{}.csv'.format(episode))
        # 메모리 초기화 및 재 설계
        self.state_mem = []
        self.train_mem = []
        self.state_mem = self.initial_db_structure(self.state_parameter)
        self.train_mem = self.initial_db_structure(self.train_parameter)

    def initial_db_structure(self, para):
        # 초기 상태 메모리 선언
        state_structure = pd.DataFrame([], columns=para)
        return state_structure


class CNS(Control_data):
    '''
    - Shared_mem
        : shared_mem[0] - 해당 에이전트의 Main 메모리가 보내짐.

        : self.all_mem[0] : 1번 에이전트의 메모리
        : self.all_mem[0][0] : 1번 에이전트의 메모리 중 Main 메모리 <- 현재 수준에 전달된 메모리
        : self.all_mem[0][0]['ZSGNOR1'] : 1번 에이전트의 메모리 중 Main 메모리에서 'ZSG..'의 정보

        : 현재 클레스에서 값을 접근하려면
        ex) self.CNS_condition['ZSGNOR1']
    '''
    def __init__(self, mem, ip, port, s_para, t_para):
        Control_data.__init__(self, s_para, t_para)
        self.CNS_condition = mem
        self.cns_udp = CNSUDP(ip=ip, port=port)

    def cns_run(self):
        '''
        cns에 동작 신호를 보내고 1step 진행이 완료되면 0을 반환
        :return: 0 : 1Step 진행 완료
        '''
        old_line = len(self.CNS_condition['KFZRUN']['L'])
        self.cns_udp._send_control_signal(['KFZRUN'], [3])
        while True:
            new_line = len(self.CNS_condition['KFZRUN']['L'])
            if self.CNS_condition['KFZRUN']['V'] == 4:  # Run하고 1초 대기후 Freeze한 상태
                if old_line != new_line:
                    break
            time.sleep(1)
        return 0

    def cns_initial(self):
        '''
        cns에 초기화 동작 신호를 보내고 완료되면 0을 반환
        :return: 0 : CNS 초기화 완료
        '''
        self.cns_udp._send_control_signal(['KFZRUN'], [5])
        while True:
            if self.CNS_condition['KCNTOMS']['V'] == 0 and self.CNS_condition['KFZRUN']['V'] == 6:  # Initial이 완료된 상태
                break
            time.sleep(1)
        return 0

    def cns_mal_fun(self, mal_nub, mal_opt, mal_time):
        '''
        cns에 malfunction 신호를 보냄
        :param mal_nub: malfunction nuber
        :param mal_opt: malfunction option
        :param mal_time: malfunction 발생 time
        :return: -
        '''
        return self.cns_udp._send_malfunction_signal(mal_nub, mal_opt, mal_time)

    def cns_control(self, para, val):
        return self.cns_udp._send_control_signal(para=para, val=val)