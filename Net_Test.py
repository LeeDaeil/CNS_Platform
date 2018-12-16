from keras.preprocessing import sequence
from keras.models import Sequential, Model
from keras import backend as K
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding
from keras.layers import LSTM
from keras.layers import Conv1D, MaxPooling1D
from keras.datasets import imdb
import numpy as np
'''
ref. Keras Example, https://github.com/keras-team/keras/tree/master/examples
'''
class C_LSTM_Test:
    def __init__(self):
        # Embedding
        self.max_features = 20000
        self.maxlen = 5
        self.embedding_size = 128

        # Convolution
        self.kernel_size = 5
        self.filters = 64
        self.pool_size = 4

        # LSTM
        self.lstm_output_size = 70

        # Training
        self.batch_size = 30
        self.epochs = 2

    def make_array(self):
        x_input = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [5, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
        print(x_input.shape, x_input)
        x_input = sequence.pad_sequences(x_input, maxlen=10)
        print(x_input.shape, x_input)

        model = Sequential()
        model.add(Embedding(5, 4, input_length=10))
        model.compile('rmsprop', 'mse')
        output_array = model.predict(x_input)
        print(output_array, output_array.shape)

    def run(self):
        # x_train = np.random.random((1, 80, 3))
        x_train = np.random.random((1, 8, 2))
        print(x_train)

        model = Sequential()
        # model.add(Conv1D(100, 2, strides=1, activation='relu', input_shape=(80, 3)))
        model.add(Conv1D(10, 3, strides=1, activation='relu', input_shape=(8, 2)))
        # model.add(Conv1D(input_shape=(10, 5),
        #                  filters=64,
        #                  kernel_size=5,
        #                  padding='valid',
        #                  activation='relu',
        #                  strides=1))
        model.add(MaxPooling1D(pool_size=2))  # strides=None means strides=pool_size
        # model.add(LSTM(5, return_sequences=True))
        model.add(LSTM(4, return_sequences=True))
        model.add(LSTM(10))
        model.model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])
        model.summary()
        result_ = model.predict(x_train)
        print(result_, np.shape(result_))

        from keras import backend as K

        # with a Sequential model
        layer_output_0 = K.function([model.layers[0].input], [model.layers[0].output])
        layer_output = layer_output_0([x_train])
        print(layer_output, np.shape(layer_output))

        layer_output_0 = K.function([model.layers[0].input], [model.layers[1].output])
        layer_output = layer_output_0([x_train])
        print(layer_output, np.shape(layer_output))

        layer_output_0 = K.function([model.layers[0].input], [model.layers[2].output])
        layer_output = layer_output_0([x_train])
        print(layer_output, np.shape(layer_output))

        layer_output_0 = K.function([model.layers[0].input], [model.layers[3].output])
        layer_output = layer_output_0([x_train])
        print(layer_output, np.shape(layer_output))

    def run1(self):
        '''
        Note:
        batch_size is highly sensitive.
        Only 2 epochs are needed as the dataset is very small.
        '''

        print('Build model...')

        model = Sequential()
        # model.add(Embedding(self.max_features, self.embedding_size))#, input_length=self.maxlen))
        # model.add(Dropout(0.25))
        model.add(Dense(20))
        model.add(Conv1D(5, 2, padding='valid', activation='relu', strides=1))
        model.add(MaxPooling1D(pool_size=self.pool_size))
        # model.add(LSTM(self.lstm_output_size))
        model.add(Dense(1))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])
        model.summary()



        # print('Train...')
        # model.fit(x_train, y_train,
        #           batch_size=self.batch_size,
        #           epochs=self.epochs,
        #           validation_data=(x_test, y_test))
        # score, acc = model.evaluate(x_test, y_test, batch_size=self.batch_size)
        # print('Test score:', score)
        # print('Test accuracy:', acc)