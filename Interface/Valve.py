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