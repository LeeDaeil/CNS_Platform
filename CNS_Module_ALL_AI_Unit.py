

class MainNet:
    def __init__(self):
        self.AB_DIG_AI, self.AB_CONT_AI, self.ROD_actor, self.ROD_critic = self.build_model()
        self.load_model()

    def build_model(self):
        from keras.layers import Dense, Input, Conv1D, MaxPooling1D, LSTM, Flatten
        from keras.models import Model

        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        # ------------------------------------------------------------------------
        state = Input(batch_shape=(None, 10, 136))
        shared = LSTM(256)(state)
        shared = Dense(256, activation='relu')(shared)
        shared = Dense(512, activation='relu')(shared)
        shared = Dense(21, activation='softmax')(shared)

        AB_DIG_AI = Model(inputs=state, outputs=shared)
        # ------------------------------------------------------------------------
        state_1 = Input(batch_shape=(None, 10, 137))
        shared_1 = LSTM(256)(state_1)
        shared_1 = Dense(512, activation='relu')(shared_1)
        shared_1 = Dense(512, activation='relu')(shared_1)
        shared_1 = Dense(7)(shared_1)

        AB_CONT_AI = Model(inputs=state_1, outputs=shared_1)
        # ------------------------------------------------------------------------
        # ROD_input = Input(batch_shape=(None, 10, 6)) -- OLD
        ROD_input = Input(batch_shape=(None, 10, 13))
        ROD_shared = LSTM(32, activation='relu')(ROD_input)
        ROD_shared = Dense(64)(ROD_shared)

        # ROD_act_hid = Dense(64, activation='relu', kernel_initializer='glorot_uniform')(ROD_shared)
        ROD_act_hid = Dense(124, activation='relu', kernel_initializer='glorot_uniform')(ROD_shared)
        ROD_act_prob = Dense(3, activation='softmax', kernel_initializer='glorot_uniform')(ROD_act_hid)
        # ROD_cri_hid = Dense(32, activation='relu', kernel_initializer='he_uniform')(ROD_shared)
        ROD_cri_hid = Dense(64, activation='relu', kernel_initializer='he_uniform')(ROD_shared)
        ROD_cri_val = Dense(1, activation='linear', kernel_initializer='he_uniform')(ROD_cri_hid)

        ROD_actor = Model(inputs=ROD_input, outputs=ROD_act_prob)
        ROD_critic = Model(inputs=ROD_input, outputs=ROD_cri_val)

        print(ROD_actor.summary())
        print(ROD_critic.summary())
        # ------------------------------------------------------------------------
        return AB_DIG_AI, AB_CONT_AI, ROD_actor, ROD_critic

    # def predict_cont_action(self, input_window):
    #     predict_result = self.AB_CONT_AI.predict([[input_window]])
    #     return predict_result

    def load_model(self):
        self.AB_DIG_AI.load_weights("ab_all_model.h5")
        self.AB_CONT_AI.load_weights("ab_control_model.h5")
        self.ROD_actor.load_weights("ROD_A3C_actor.h5")
        self.ROD_critic.load_weights("ROD_A3C_cric.h5")