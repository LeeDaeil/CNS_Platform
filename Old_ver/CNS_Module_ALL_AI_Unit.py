

class MainNet:
    def __init__(self):
        self.AB_DIG_AI, self.AB_CONT_AI, self.ROD_actor, self.ROD_critic, self.PZR_actor, self.PZR_critic = self.build_model()
        # self.load_model()

    def build_model(self):
        # from keras.models import tf.keras.Model

        import tensorflow as tf

        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        # ------------------------------------------------------------------------
        state = tf.keras.Input(batch_shape=(None, 10, 136))
        shared = tf.keras.layers.LSTM(256)(state)
        shared = tf.keras.layers.Dense(256, activation='relu')(shared)
        shared = tf.keras.layers.Dense(512, activation='relu')(shared)
        shared = tf.keras.layers.Dense(21, activation='softmax')(shared)

        AB_DIG_AI = tf.keras.Model(inputs=state, outputs=shared)
        # ------------------------------------------------------------------------
        state_1 = tf.keras.Input(batch_shape=(None, 10, 137))
        shared_1 = tf.keras.layers.LSTM(256)(state_1)
        shared_1 = tf.keras.layers.Dense(512, activation='relu')(shared_1)
        shared_1 = tf.keras.layers.Dense(512, activation='relu')(shared_1)
        shared_1 = tf.keras.layers.Dense(7)(shared_1)

        AB_CONT_AI = tf.keras.Model(inputs=state_1, outputs=shared_1)
        # ------------------------------------------------------------------------
        # ROD_input = tf.keras.Input(batch_shape=(None, 10, 6)) -- OLD
        ROD_input = tf.keras.Input(batch_shape=(None, 10, 13))
        ROD_shared = tf.keras.layers.LSTM(32, activation='relu')(ROD_input)
        ROD_shared = tf.keras.layers.Dense(64)(ROD_shared)

        # ROD_act_hid = tf.keras.layers.Dense(64, activation='relu', kernel_initializer='glorot_uniform')(ROD_shared)
        ROD_act_hid = tf.keras.layers.Dense(124, activation='relu', kernel_initializer='glorot_uniform')(ROD_shared)
        ROD_act_prob = tf.keras.layers.Dense(3, activation='softmax', kernel_initializer='glorot_uniform')(ROD_act_hid)
        # ROD_cri_hid = tf.keras.layers.Dense(32, activation='relu', kernel_initializer='he_uniform')(ROD_shared)
        ROD_cri_hid = tf.keras.layers.Dense(64, activation='relu', kernel_initializer='he_uniform')(ROD_shared)
        ROD_cri_val = tf.keras.layers.Dense(1, activation='linear', kernel_initializer='he_uniform')(ROD_cri_hid)

        ROD_actor = tf.keras.Model(inputs=ROD_input, outputs=ROD_act_prob)
        ROD_critic = tf.keras.Model(inputs=ROD_input, outputs=ROD_cri_val)
        # ------------------------------------------------------------------------
        PZR_state = tf.keras.Input(batch_shape=(None, 5, 7))
        PZR_shared = tf.keras.layers.Conv1D(filters=10, kernel_size=5, strides=1, padding='same')(PZR_state)
        PZR_shared = tf.keras.layers.MaxPooling1D(pool_size=3)(PZR_shared)
        PZR_shared = tf.keras.layers.LSTM(12)(PZR_shared)
        PZR_shared = tf.keras.layers.Dense(24)(PZR_shared)

        PZR_actor_hidden = tf.keras.layers.Dense(24, activation='relu', kernel_initializer='glorot_uniform')(PZR_shared)
        PZR_action_prob = tf.keras.layers.Dense(9, activation='softmax', kernel_initializer='glorot_uniform')(PZR_actor_hidden)

        PZR_value_hidden = tf.keras.layers.Dense(12, activation='relu', kernel_initializer='he_uniform')(PZR_shared)
        PZR_state_value = tf.keras.layers.Dense(1, activation='linear', kernel_initializer='he_uniform')(PZR_value_hidden)

        PZR_actor = tf.keras.Model(inputs=PZR_state, outputs=PZR_action_prob)
        PZR_critic = tf.keras.Model(inputs=PZR_state, outputs=PZR_state_value)

        # ------------------------------------------------------------------------
        return AB_DIG_AI, AB_CONT_AI, ROD_actor, ROD_critic, PZR_actor, PZR_critic

    # def predict_cont_action(self, input_window):
    #     predict_result = self.AB_CONT_AI.predict([[input_window]])
    #     return predict_result

    def load_model(self):
        self.AB_DIG_AI.load_weights("ab_all_model.h5")
        self.AB_CONT_AI.load_weights("ab_control_model.h5")
        self.ROD_actor.load_weights("ROD_A3C_actor.h5")
        self.ROD_critic.load_weights("ROD_A3C_cric.h5")
        self.PZR_actor.load_weights("PZR_A3C_actor.h5")
        self.PZR_critic.load_weights("PZR_A3C_cric.h5")