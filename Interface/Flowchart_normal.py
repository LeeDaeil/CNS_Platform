# 인터페이스 설계 측면에서,
# 이 위젯뭉치가 올라가야하는 프레임의 Geometry를 생각할 것
# 또한 전체 프레임의 좌표 또한 고려해야 할 것

import sys
from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QFrame
from PySide2.QtGui import QPainter, QPen
from PySide2.QtGui import Qt
from Interface.Button import btn_frame

class make_flowchart(QWidget):
    def __init__(self, mem, parent=None):
        super(make_flowchart, self).__init__(parent)
        print(mem)
        # self.parent = parent
        # self.setGeometry(self.parent.geometry())
        # self.trig_mem = mem
        self.setGeometry(0, 0, 1000, 1000)                              # 부모의 Geometry를 따라가야하는 이유는 ?

        self.btn_1 = btn_frame(self, x=390, y=20, w=200, h=50, text='Start', type=3)
        self.btn_2 = btn_frame(self, x=390, y=110, w=200, h=50, text='Are alarm and trip occur?', type=4)
        self.btn_3 = btn_frame(self, x=390, y=200, w=200, h=50, text='Normal operation strategy', type=1)
        self.btn_4 = btn_frame(self, x=390, y=290, w=200, h=50, text='Auto Control By RL', type=1)
        self.btn_5 = btn_frame(self, x=390, y=380, w=200, h=50, text='Are all the procedure performed?', type=4)
        self.btn_6 = btn_frame(self, x=390, y=470, w=200, h=50, text='End', type=3)

        self.pen_color = Qt.black
        self.control(mem)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(self.pen_color))

        p.drawLine(490, 70, 490, 110)   # 1-2
        p.drawLine(490, 160, 490, 200)  # 2-3
        p.drawLine(490, 250, 490, 290)  # 3-4
        p.drawLine(490, 340, 490, 380)  # 4-5
        p.drawLine(490, 430, 490, 470)  # 5-6

        p.drawLine(590, 405, 630, 405)  # 5-4
        p.drawLine(630, 405, 630, 315)  # 5-4
        p.drawLine(630, 315, 590, 315)  # 5-4

        self.update()

    def control(self, mem):
        print(mem['strategy'])
        if mem['strategy'][-1] == 'NA':                  # a 누르면 변신
            self.btn_1.color = Qt.lightGray
            self.btn_2.color = Qt.lightGray
            self.btn_3.color = Qt.lightGray
            self.btn_4.color = Qt.yellow
            self.btn_5.color = Qt.white
            self.btn_6.color = Qt.white
            print('lala')

        else:
            self.btn_1.color = Qt.white
            self.btn_2.color = Qt.white
            self.btn_3.color = Qt.white
            self.btn_4.color = Qt.white
            self.btn_5.color = Qt.white
            self.btn_6.color = Qt.white

        self.update()

    def mousePressEvent(self, e):
        print(e.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win_main = make_flowchart()
    win_main.show()
    sys.exit(app.exec_())