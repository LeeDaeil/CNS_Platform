# 커스텀 버튼
# 목표
# * 버튼 그리기 => 성공
# * 마우스로 버튼을 클릭하여 버튼의 색깔 변경 => 실패 -> 문제점: 도형 이외의 공간을 클릭해도 색상이 변함 -> 원인 추측: Geometry 때문인가?
# * 마름모 모양 추가 => 성공
# * 텍스트 써주는 기능 추가 => 성공

import sys
from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QFrame, QLabel

from PySide2.QtGui import QPainter, Qt, QPen, QPolygon
from PySide2.QtCore import QRect, QPoint

class btn_frame(QPushButton):                                                            # 부모는 무조건 한명이어야 하나?

    def __init__(self, parent=None, x=None, y=None, w=None, h=None, text=None, type=1):
        super(btn_frame, self).__init__(parent)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.setGeometry(self.x, self.y, self.w, self.h)
        self.color = Qt.white
        self.type = type
        # self.write()

    # def mouseReleaseEvent(self, e):
    #     self.color_ = Qt.blue

    def mousePressEvent(self, e):
        self.color = Qt.green

    def mouseDoubleClickEvent(self, e):
        self.color = Qt.red

    def paintEvent(self, event):
        rect = QRect(0, 0, self.w - 1, self.h - 1)
        p = QPainter(self)
        p.setPen(QPen(Qt.black))
        p.setBrush(self.color)
        if self.type == 1:
            p.drawRect(0, 0, self.w-1, self.h-1)
            p.drawText(rect, Qt.AlignCenter, self.text)                 # 이게 더 좋은데? 어떤 방식이지? =>   # w.setGeometry(self.geometry()) 차이점이 무엇이지?
        elif self.type == 2:
            p.drawEllipse(0, 0, self.w-1, self.h-1)
            p.drawText(rect, Qt.AlignCenter, self.text)
        elif self.type == 3:
            p.drawEllipse(0, 0, self.w-1, self.h-1)
            p.drawText(rect, Qt.AlignCenter, self.text)
        elif self.type == 4:                            # 마름모 꼴
            points = [QPoint(self.w / 2, 0),
                      QPoint(0, self.h / 2),
                      QPoint(self.w / 2, self.h),
                      QPoint(self.w, self.h / 2)]
            poly = QPolygon(points)
            p.drawPolygon(poly)
            p.drawText(rect, Qt.AlignCenter, self.text)
        self.update()                                                   # self.update()

    # def write(self):
    #     w = QLabel(self)
    #
    #     w.setText(self.text)
    #     # w.setAlignment(Qt.AlignCenter)                              # 말을 안듣네
    #     w.setGeometry(self.geometry())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win_main = btn_frame(x=10, y=10, w=150, h=150, text='bibi', type=4)
    win_main.show()
    sys.exit(app.exec_())