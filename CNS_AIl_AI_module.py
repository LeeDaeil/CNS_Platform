import numpy as np


class Mainnet:
    def __init__(self):
        self.net_1, self.AB_DIG_Net = self.make_net()

    def make_net(self):
        import tensorflow as tf
        from keras import backend as K
        from keras.models import Model
        from keras.layers import Input, Dense, Lambda, LSTM, RepeatVector
        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        def sampling(args):
            z_mean, z_log_sigma = args
            epsilon = tf.keras.backend.random_normal(shape=(1, 8))
            return z_mean + z_log_sigma * epsilon

        x = Input(shape=(397,))
        y = RepeatVector(10)(x)
        h = LSTM(4)(y)

        z_mean = Dense(8)(h)
        z_log_sigma = Dense(8)(h)

        z = Lambda(sampling, output_shape=(8,))([z_mean, z_log_sigma])

        h_decoded = RepeatVector(10)(z)
        x_decoded_mean = LSTM(4, return_sequences=True)(h_decoded)
        x_decoded_mean = LSTM(26, return_sequences=False)(x_decoded_mean)

        vae = Model(x, x_decoded_mean)
        vae.load_weights('vae_lstm_weight.h5')
        # --------------------------------------------------------------------------------------------------------------
        state = tf.keras.Input(batch_shape=(None, 10, 136))
        shared = tf.keras.layers.LSTM(256)(state)
        shared = tf.keras.layers.Dense(256, activation='relu')(shared)
        shared = tf.keras.layers.Dense(512, activation='relu')(shared)
        shared = tf.keras.layers.Dense(21, activation='softmax')(shared)

        AB_DIG_AI = tf.keras.Model(inputs=state, outputs=shared)
        AB_DIG_AI.load_weights('./AI/AI_AB_DIG.h5')
        # --------------------------------------------------------------------------------------------------------------

        return vae, AB_DIG_AI