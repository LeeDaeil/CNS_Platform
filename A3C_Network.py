class A3C_main_network:
    def __init__(self):
        pass

    def build_network_model(self, net_type='DNN', in_pa=1, ou_pa=1, time_leg=1):
        import tensorflow as tf
        from keras import backend as K
        from keras.layers import Dense, Input, Conv1D, MaxPooling1D, LSTM, Flatten
        from keras.models import Model
        from keras.optimizers import Adam, RMSprop

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
                    shared = LSTM(16, activation='relu')(state)

                elif net_type == 'CLSTM':
                    shared = Conv1D(filters=10, kernel_size=3, strides=1, padding='same')(state)
                    shared = MaxPooling1D(pool_size=2)(shared)
                    shared = LSTM(8)(shared)

            # ----------------------------------------------------------------------------------------------------
            # Common output network
            actor_hidden = Dense(8, activation='relu', kernel_initializer='glorot_uniform')(shared)
            action_prob = Dense(ou_pa, activation='softmax', kernel_initializer='glorot_uniform')(actor_hidden)

            value_hidden = Dense(4, activation='relu', kernel_initializer='he_uniform')(shared)
            state_value = Dense(1, activation='linear', kernel_initializer='he_uniform')(value_hidden)

            actor, critic = Model(inputs=state, outputs=action_prob), Model(inputs=state, outputs=state_value)
            print('Make {} Network'.format(net_type))

            actor._make_predict_function()
            critic._make_predict_function()

        # actor.summary(print_fn=logging.info)
        # critic.summary(print_fn=logging.info)

        return [actor, critic]
