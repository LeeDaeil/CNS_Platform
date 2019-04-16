import tensorflow as tf
import numpy as np
import keras.backend as K
import threading
from threading import Lock
from keras.models import Model
from keras.utils import to_categorical
from keras.layers import Dense, Input, Conv1D, MaxPooling1D, Flatten, CuDNNLSTM
from keras.optimizers import RMSprop
from time import sleep


class A3C:
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
        """ Update actor and critic networks from experience
        """
        # Compute discounted rewards and Advantage (TD. Error)
        discounted_rewards = self.discount(rewards)
        state_values = self.critic.predict(np.array(states))
        advantages = discounted_rewards - np.reshape(state_values, len(state_values))
        # Networks optimization
        self.a_opt([states, actions, advantages])
        self.c_opt([states, discounted_rewards])

    def train(self, summary_writer):
        Worker = worker()
        worker_list = [threading.Thread(
                target=Worker.training_thread,
                # daemon=True,
                args=(self, self.max_episode, self.shared_mem[i], self.action_dim, self.learning_interval,
                      summary_writer, i)) for i in range(self.nub_agent)]

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


class worker:
    def training_thread(self, A3C_agent, Nmax, shared_mem, action_dim, f, summary_writer, nub_agent):
        """ Build threads to run shared computation across """

        global episode
        while episode < Nmax:
            print('{}_{}'.format(nub_agent, episode))
            input_data = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
            print(np.shape(input_data))
            print(agent.policy_action(input_data))

            sleep(1)
            a = False

            if a:
                # Reset episode
                time, cumul_reward, done = 0, 0, False
                old_state = env.reset()
                actions, states, rewards = [], [], []
                while not done and episode < Nmax:
                    # Actor picks an action (following the policy)
                    a = agent.policy_action(np.expand_dims(old_state, axis=0))
                    # Retrieve new state, reward, and whether the state is terminal
                    new_state, r, done, _ = env.step(a)
                    # Memorize (s, a, r) for training
                    actions.append(to_categorical(a, action_dim))
                    rewards.append(r)
                    states.append(old_state)
                    # Update current state
                    old_state = new_state
                    cumul_reward += r
                    time += 1
                    # Asynchronous training
                    if (time % f == 0 or done):
                        lock.acquire()
                        agent.train_models(states, actions, rewards, done)
                        lock.release()
                        actions, states, rewards = [], [], []

                # Export results for Tensorboard
                score = self.tfSummary('score', cumul_reward)
                summary_writer.add_summary(score, global_step=episode)
                summary_writer.flush()
            # Update episode count
            with lock:
                if (episode < Nmax):
                    episode += 1

    def tfSummary(self, tag, val):
        """ Scalar Value Tensorflow Summary
        """
        return tf.Summary(value=[tf.Summary.Value(tag=tag, simple_value=val)])