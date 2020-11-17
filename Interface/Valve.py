import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *


class Valve_App(QWidget):
    def __init__(self, valve_name='', parent=None):
        super().__init__(parent=parent)
        self.valve_name = valve_name
        self.valve_state = 0        # 0 Close 1 Open

        # Load Svg
        self.svgWidget = QSvgWidget('./Img/Valve.svg', self)
        self.update_valve_state()

        # SetUp Main Widget
        self.resize(self.svgWidget.sizeHint())
        self.show()

        # Setup Mouse_state
        self.Mouse_state = 0
        self.Save_pos = 0
        self.Save_scale = 1

    def update_valve_state(self):
        if self.valve_state > 1:  self.valve_state = 0      # 테스트용 0~1 사이만

        if self.valve_state == 0:
            self.svgWidget.load('./Img/Valve_close.svg')
        else:
            self.svgWidget.load('./Img/Valve_open.svg')

    def resizeEvent(self, a0) -> None:
        self.svgWidget.resize(a0.size())

    def enterEvent(self, a0) -> None:
        print(f'Enter: {self.valve_name}_{self.valve_state}_{self.Mouse_state}_{self.geometry()}')

    def mousePressEvent(self, a0) -> None:
        self.Mouse_state = a0.button()
        if a0.button() == 1 or a0.button() == 2:
            self.Save_pos = a0.pos()
        else:
            if a0.button() == 4:
                # Valve test 용
                self.valve_state += 1
                self.update_valve_state()

    def mouseMoveEvent(self, a0) -> None:
        if self.Mouse_state == 1:   # Move
            self.move(a0.pos() - self.Save_pos + self.pos())
        elif self.Mouse_state == 2:
            self.resize(self.size().width(), self.size().height())
        else:                       # Mold
            pass

class MainNet:
    def __init__(self):
        self.SV_model = self.build_model()

    def build_model(self):
        from keras import backend as K
        from keras.models import Model
        from keras.layers import Input, Dense, Lambda, LSTM, RepeatVector
        from keras import objectives

        def sampling(args):
            z_mean, z_log_sigma = args
            epsilon = K.random_normal(shape=(1, 8),
                                      mean=0., stddev=1)
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

        def vae_loss(x, x_decoded_mean):
            xent_loss = objectives.mse(x, x_decoded_mean)
            kl_loss = - 0.5 * K.mean(1 + z_log_sigma - K.square(z_mean) - K.exp(z_log_sigma))
            loss = xent_loss + kl_loss
            return loss

        vae.compile(optimizer='adam', loss=vae_loss, metrics=['acc', 'cosine_proximity'])
        vae.load_weights('vae_lstm_weight.h5')

        return vae

class Test_window(QWidget):
    def __init__(self):
        super().__init__()

        self.Valve_list = []

        self.setGeometry(300, 300, 700, 700)
        self.show()

    def mousePressEvent(self, a0) -> None:
        if a0.button() == 1: # Left Click
            Valve_ = Valve_App(valve_name=f'A{len(self.Valve_list)}', parent=self)
            Valve_.setGeometry(a0.pos().x(), a0.pos().y(), Valve_.size().width(), Valve_.size().height())
            self.Valve_list.append(Valve_)
            print(f'Call Make_{Valve_.geometry()}_{a0.pos().x()}_{a0.pos().y()}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Test_window()
    sys.exit(app.exec_())