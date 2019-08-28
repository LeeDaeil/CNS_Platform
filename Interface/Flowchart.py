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
        # print(mem)
        # self.parent = parent
        # self.setGeometry(self.parent.geometry())
        # self.trig_mem = mem
        self.setGeometry(0, 0, 1000, 1000)                              # 부모의 Geometry를 따라가야하는 이유는 ?

        self.sub_1 = btn_frame(self, x=550, y=20, w=100, h=50, text='Start', type=3)
        self.sub_2 = btn_frame(self, x=500, y=90, w=200, h=50, text='Did an alarm or trip occur?', type=4)
        self.sub_3 = btn_frame(self, x=500, y=160, w=200, h=50, text='Abnormal Operation Mode', type=1)
        self.sub_4 = btn_frame(self, x=500, y=230, w=200, h=50, text='Is it possible to diagnose?', type=4)
        self.sub_5 = btn_frame(self, x=350, y=300, w=200, h=50, text='Is its condition diagnose?', type=4)
        self.sub_5_1 = btn_frame(self, x=650, y=300, w=200, h=50, text='Is its condition diagnose?', type=4)
        self.sub_6 = btn_frame(self, x=350, y=370, w=200, h=50, text='Auto Control_선제', type=1)
        self.sub_6_1 = btn_frame(self, x=130, y=370, w=200, h=50, text='Auto Control_LSTM', type=1) # -130
        self.sub_6_2 = btn_frame(self, x=650, y=370, w=200, h=50, text='Auto Control_RL', type=1)
        self.sub_7 = btn_frame(self, x=500, y=440, w=200, h=50, text='Is it controlled correctly?', type=4)
        self.sub_8 = btn_frame(self, x=500, y=510, w=200, h=50, text='Manual Control', type=1)

        self.pen_color = Qt.black
        self.control(mem)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(self.pen_color))

        p.drawLine(600, 70, 600, 90)  # 1-2
        p.drawLine(600, 140, 600, 160)  # 2-3
        p.drawLine(600, 210, 600, 230)  # 3-4
        p.drawLine(450, 255, 500, 255)  # 4-5
        p.drawLine(450, 255, 450, 300)  # 4-5
        p.drawLine(700, 255, 750, 255)  # 4-5_1
        p.drawLine(750, 255, 750, 300)  # 4-5_1
        p.drawLine(350, 325, 230, 325)  # 5-6_1
        p.drawLine(230, 325, 230, 370)  # 5-6_1
        p.drawLine(450, 350, 450, 370)  # 5-6
        p.drawLine(750, 350, 750, 370)  # 5_1-6_2
        p.drawLine(230, 420, 230, 465)  # 6_1-7
        p.drawLine(230, 465, 500, 465)  # 6_1-7
        p.drawLine(450, 420, 450, 465)  # 6-7
        p.drawLine(750, 420, 750, 465)  # 6_2-7
        p.drawLine(750, 465, 700, 465)  # 6_2-7
        p.drawLine(600, 490, 600, 510)  # -7

        self.update()

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_A:                  # a 누르면 변신
    #         self.sub_1.color = Qt.lightGray
    #         self.sub_2.color = Qt.lightGray
    #         self.sub_3.color = Qt.lightGray
    #         self.sub_4.color = Qt.lightGray
    #         self.sub_5.color = Qt.lightGray
    #         self.sub_6_1.color = Qt.yellow
    #
    #     elif event.key() == Qt.Key_S:               # s 누르면 변신
    #         self.sub_1.color = Qt.lightGray
    #         self.sub_2.color = Qt.lightGray
    #         self.sub_3.color = Qt.lightGray
    #         self.sub_4.color = Qt.lightGray
    #         self.sub_5.color = Qt.lightGray
    #         self.sub_6.color = Qt.yellow
    #
    #     elif event.key() == Qt.Key_D:               # s 누르면 변신
    #         self.sub_1.color = Qt.lightGray
    #         self.sub_2.color = Qt.lightGray
    #         self.sub_3.color = Qt.lightGray
    #         self.sub_4.color = Qt.lightGray
    #         self.sub_5_1.color = Qt.lightGray
    #         self.sub_6_2.color = Qt.yellow
    #
    #     elif event.key() == Qt.Key_B:               # b 누르면 초기화
    #         self.sub_1.color = Qt.white
    #         self.sub_2.color = Qt.white
    #         self.sub_3.color = Qt.white
    #         self.sub_4.color = Qt.white
    #         self.sub_5.color = Qt.white
    #         self.sub_5_1.color = Qt.white
    #         self.sub_6.color = Qt.white
    #         self.sub_6_1.color = Qt.white
    #         self.sub_6_2.color = Qt.white
    #         pass
    #     self.update()

        # # -------------------------------------
        # #if st == 1:#
        # self.sub_1.w = self.sub_1.w + 10
        # print(self.sub_1.w)
        # # -------------------------------------

    def control(self, mem):
        print(mem['strategy'])
        if mem['strategy'][-1] == 'NA':                  # a 누르면 변신
            self.sub_1.color = Qt.lightGray
            self.sub_2.color = Qt.lightGray
            self.sub_3.color = Qt.lightGray
            self.sub_4.color = Qt.lightGray
            self.sub_5.color = Qt.lightGray
            self.sub_6_1.color = Qt.yellow
            print('lala')
        else:
            self.sub_1.color = Qt.white
            self.sub_2.color = Qt.white
            self.sub_3.color = Qt.white
            self.sub_4.color = Qt.white
            self.sub_5.color = Qt.white
            self.sub_5_1.color = Qt.white
            self.sub_6.color = Qt.white
            self.sub_6_1.color = Qt.white
            self.sub_6_2.color = Qt.white

        self.update()

    def mousePressEvent(self, e):
        print(e.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win_main = make_flowchart()
    win_main.show()
    sys.exit(app.exec_())