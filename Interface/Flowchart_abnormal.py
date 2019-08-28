# 인터페이스 설계 측면에서,
# 이 위젯뭉치가 올라가야하는 프레임의 Geometry를 생각할 것
# 또한 전체 프레임의 좌표 또한 고려해야 할 것

import sys
from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QFrame
from PySide2.QtGui import QPainter, QPen
from PySide2.QtGui import Qt
from Interface.Button import btn_frame

class make_flowchart(QWidget):                                          # QWidget 확인하기
    def __init__(self, mem, parent=None):                                    #
        super(make_flowchart, self).__init__(parent)                    #

        # self.parent = parent
        # self.setGeometry(self.parent.geometry())
        # self.trig_mem = mem
        self.setGeometry(0, 0, 1000, 1000)                              # 부모의 Geometry를 따라가야하는 이유는 ?

        self.btn_1 = btn_frame(self, x=130, y=20, w=200, h=50, text='Start', type=3)
        self.btn_2 = btn_frame(self, x=130, y=90, w=200, h=50, text='Are alarms ans trip occur?', type=4)
        self.btn_3 = btn_frame(self, x=130, y=160, w=200, h=50, text='Abnormal operation', type =1)
        self.btn_4 = btn_frame(self, x=130, y=230, w=200, h=50, text='Is trained abnormal scenario?', type=4)
        self.btn_5 = btn_frame(self, x=130, y=300, w=200, h=50, text='Is the operator required?', type=4)
        self.btn_5_1 = btn_frame(self, x=650, y=300, w=200, h=50, text='Request for operator intervention', type=1)
        self.btn_6 = btn_frame(self, x=130, y=370, w=200, h=50, text='Request for operator intervention', type=1)
        self.btn_6_1= btn_frame(self, x=650, y=370, w=200, h=50, text='Auto control by RL', type=1)
        self.btn_7 = btn_frame(self, x=130, y=440, w=200, h=50, text='Auto control by LSTM', type=1)
        self.btn_7_1= btn_frame(self, x=390, y=440, w=200, h=50, text='Auto control by LSTM', type=1)
        self.btn_7_2 = btn_frame(self, x=650, y=440, w=200, h=50, text='Is the operator involved?', type=4)
        self.btn_8 = btn_frame(self, x=130, y=510, w=200, h=50, text='Are all the procedure performed?', type=4)
        self.btn_8_1 = btn_frame(self, x=390, y=510, w=200, h=50, text='Are all the procedure performed?', type=4)
        self.btn_8_2 = btn_frame(self, x=650, y=510, w=200, h=50, text='Manual control', type=1)
        self.btn_9 = btn_frame(self, x=130, y=580, w=200, h=50, text='Manual control', type=1)
        self.btn_10 = btn_frame(self, x=130, y=650, w=200, h=50, text='End', type=3)

        self.pen_color = Qt.black
        self.control(mem)


    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(self.pen_color))

        p.drawLine(230, 70, 230, 90)    # 1-2
        p.drawLine(230, 140, 230, 160)  # 2-3
        p.drawLine(230, 210, 230, 230)  # 3-4
        p.drawLine(230, 280, 230, 300)  # 4-5
        p.drawLine(330, 255, 750, 255)  # 4-5_1
        p.drawLine(750, 255, 750, 300)  # 4-5_1
        p.drawLine(230, 350, 230, 370)  # 5-6
        p.drawLine(330, 325, 490, 325)  # 5-7_1
        p.drawLine(490, 325, 490, 440)  # 5-7_1
        p.drawLine(230, 420, 230, 440)  # 6-7
        p.drawLine(230, 490, 230, 510)  # 7-8
        p.drawLine(230, 560, 230, 580)  # 8-9
        p.drawLine(230, 630, 230, 650)  # 9-10

        p.drawLine(750, 350, 750, 370)  # 5_1-6_1
        p.drawLine(750, 420, 750, 440)  # 6_1-7_2
        p.drawLine(750, 490, 750, 510)  # 7_2-8_2
        p.drawLine(850, 465, 870, 465)  # 7_2-6-1
        p.drawLine(870, 465, 870, 395)  # 7_2-6-1
        p.drawLine(870, 395, 850, 395)  # 7_2-6-1

        p.drawLine(330, 535, 350, 535)  # 8-7
        p.drawLine(350, 535, 350, 465)  # 8-7
        p.drawLine(350, 465, 330, 465)  # 8-7

        p.drawLine(590, 535, 610, 535)  # 8_1-7_1
        p.drawLine(610, 535, 610, 465)  # 8_1-7_1
        p.drawLine(610, 465, 590, 465)  # 8_1-7_1

        p.drawLine(490, 560, 490, 640)  # 8_1-10
        p.drawLine(490, 640, 230, 640)  # 8_1-10

        p.drawLine(750, 560, 750, 640)  # 8_2-10
        p.drawLine(750, 640, 230, 640)  # 8_2-10

        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:                  # a 누르면 변신
            self.btn_2.color = Qt.lightGray
            self.btn_3.color = Qt.lightGray
            self.btn_4.color = Qt.lightGray
            self.btn_5.color = Qt.lightGray
            self.btn_6.color = Qt.lightGray
            self.btn_7.color = Qt.yellow
            self.btn_8.color = Qt.white
            self.btn_9.color = Qt.white

            self.btn_5_1.color = Qt.white
            self.btn_6_1.color = Qt.white
            self.btn_7_1.color = Qt.white
            self.btn_7_2.color = Qt.white
            self.btn_8_1.color = Qt.white
            self.btn_8_2.color = Qt.white

        elif event.key() == Qt.Key_S:               # s 누르면 변신
            self.btn_2.color = Qt.lightGray
            self.btn_3.color = Qt.lightGray
            self.btn_4.color = Qt.lightGray
            self.btn_5.color = Qt.lightGray
            self.btn_6.color = Qt.lightGray
            self.btn_7.color = Qt.lightGray
            self.btn_8.color = Qt.lightGray
            self.btn_9.color = Qt.yellow

            self.btn_5_1.color = Qt.white
            self.btn_6_1.color = Qt.white
            self.btn_7_1.color = Qt.white
            self.btn_7_2.color = Qt.white
            self.btn_8_1.color = Qt.white
            self.btn_8_2.color = Qt.white

        elif event.key() == Qt.Key_D:               # s 누르면 변신
            self.btn_2.color = Qt.lightGray
            self.btn_3.color = Qt.lightGray
            self.btn_4.color = Qt.lightGray
            self.btn_5.color = Qt.lightGray
            self.btn_6.color = Qt.white
            self.btn_7.color = Qt.white
            self.btn_8.color = Qt.white
            self.btn_9.color = Qt.white

            self.btn_5_1.color = Qt.white
            self.btn_6_1.color = Qt.white
            self.btn_7_1.color = Qt.yellow
            self.btn_7_2.color = Qt.white
            self.btn_8_1.color = Qt.white
            self.btn_8_2.color = Qt.white

        elif event.key() == Qt.Key_F:                  # a 누르면 변신
            self.btn_2.color = Qt.lightGray
            self.btn_3.color = Qt.lightGray
            self.btn_4.color = Qt.white
            self.btn_5.color = Qt.white
            self.btn_6.color = Qt.white
            self.btn_7.color = Qt.white
            self.btn_8.color = Qt.white
            self.btn_9.color = Qt.white

            self.btn_5_1.color = Qt.lightGray
            self.btn_6_1.color = Qt.yellow
            self.btn_7_1.color = Qt.white
            self.btn_7_2.color = Qt.white
            self.btn_8_1.color = Qt.white
            self.btn_8_2.color = Qt.white

        elif event.key() == Qt.Key_G:                  # a 누르면 변신
            self.btn_2.color = Qt.lightGray
            self.btn_3.color = Qt.lightGray
            self.btn_4.color = Qt.white
            self.btn_5.color = Qt.white
            self.btn_6.color = Qt.white
            self.btn_7.color = Qt.white
            self.btn_8.color = Qt.white
            self.btn_9.color = Qt.white

            self.btn_5_1.color = Qt.lightGray
            self.btn_6_1.color = Qt.lightGray
            self.btn_7_1.color = Qt.white
            self.btn_7_2.color = Qt.lightGray
            self.btn_8_1.color = Qt.white
            self.btn_8_2.color = Qt.yellow

        elif event.key() == Qt.Key_B:               # b 누르면 초기화
            self.sub_1.color = Qt.white
            self.sub_2.color = Qt.white
            self.sub_3.color = Qt.white
            self.sub_4.color = Qt.white
            self.sub_5.color = Qt.white
            self.sub_5_1.color = Qt.white
            self.sub_6.color = Qt.white
            self.sub_6_1.color = Qt.white
            self.sub_6_2.color = Qt.white
            pass

        self.update()

        # # -------------------------------------
        # #if st == 1:#
        # self.sub_1.w = self.sub_1.w + 10
        # print(self.sub_1.w)
        # # -------------------------------------

    def control(self, mem):
        # print(mem['strategy'])
        if mem['strategy'][-1] == 'AA_2301':                  # a 누르면 변신
            self.btn_2.color = Qt.lightGray
            self.btn_3.color = Qt.lightGray
            self.btn_4.color = Qt.lightGray
            self.btn_5.color = Qt.lightGray
            self.btn_6.color = Qt.white
            self.btn_7.color = Qt.white
            self.btn_8.color = Qt.white
            self.btn_9.color = Qt.white

            self.btn_5_1.color = Qt.white
            self.btn_6_1.color = Qt.white
            self.btn_7_1.color = Qt.yellow
            self.btn_7_2.color = Qt.white
            self.btn_8_1.color = Qt.white
            self.btn_8_2.color = Qt.white
        else:
            pass

        self.update()


    def mousePressEvent(self, e):
        print(e.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win_main = make_flowchart()
    win_main.show()
    sys.exit(app.exec_())