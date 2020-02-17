# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\USER\PycharmProjects\CNS_Platform\Interface\popup_ss.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainForm(object):
    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(972, 887)
        MainForm.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));")
        self.Top_label = QtWidgets.QLabel(MainForm)
        self.Top_label.setGeometry(QtCore.QRect(10, 10, 950, 51))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.Top_label.setFont(font)
        self.Top_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Top_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Top_label.setObjectName("Top_label")
        self.Fir_label = QtWidgets.QLabel(MainForm)
        self.Fir_label.setGeometry(QtCore.QRect(10, 90, 121, 40))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.Fir_label.setFont(font)
        self.Fir_label.setStyleSheet("background-color: rgb(225, 224, 224);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0,0,0);\n"
"border-radius: 5px;\n"
"\n"
"")
        self.Fir_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Fir_label.setObjectName("Fir_label")
        self.Fou_label = QtWidgets.QLabel(MainForm)
        self.Fou_label.setGeometry(QtCore.QRect(710, 90, 251, 40))
        self.Fou_label.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")
        self.Fou_label.setObjectName("Fou_label")
        self.Thi_label = QtWidgets.QLabel(MainForm)
        self.Thi_label.setGeometry(QtCore.QRect(580, 90, 121, 40))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.Thi_label.setFont(font)
        self.Thi_label.setStyleSheet("background-color: rgb(225, 224, 224);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")
        self.Thi_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Thi_label.setObjectName("Thi_label")
        self.Sec_label = QtWidgets.QLabel(MainForm)
        self.Sec_label.setGeometry(QtCore.QRect(140, 90, 211, 40))
        self.Sec_label.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")
        self.Sec_label.setObjectName("Sec_label")
        self.btn_close = QtWidgets.QPushButton(MainForm)
        self.btn_close.setGeometry(QtCore.QRect(850, 850, 111, 31))
        self.btn_close.setObjectName("btn_close")
        self.frame = QtWidgets.QFrame(MainForm)
        self.frame.setGeometry(QtCore.QRect(10, 140, 951, 701))
        self.frame.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.SA = QtWidgets.QScrollArea(self.frame)
        self.SA.setGeometry(QtCore.QRect(0, 0, 951, 701))
        self.SA.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.SA.setWidgetResizable(True)
        self.SA.setObjectName("SA")
        self.SA_widget = QtWidgets.QWidget()
        self.SA_widget.setGeometry(QtCore.QRect(0, 0, 932, 699))
        self.SA_widget.setObjectName("SA_widget")
        self.SA.setWidget(self.SA_widget)
        self.Sec_label_2 = QtWidgets.QLabel(MainForm)
        self.Sec_label_2.setGeometry(QtCore.QRect(360, 90, 211, 40))
        self.Sec_label_2.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")
        self.Sec_label_2.setObjectName("Sec_label_2")

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

    def retranslateUi(self, MainForm):
        _translate = QtCore.QCoreApplication.translate
        MainForm.setWindowTitle(_translate("MainForm", "Form"))
        self.Top_label.setText(_translate("MainForm", "Strategy Selection Function"))
        self.Fir_label.setText(_translate("MainForm", "Plant state"))
        self.Fou_label.setText(_translate("MainForm", "TextLabel"))
        self.Thi_label.setText(_translate("MainForm", "Strategy"))
        self.Sec_label.setText(_translate("MainForm", "TextLabel"))
        self.btn_close.setText(_translate("MainForm", "Close"))
        self.Sec_label_2.setText(_translate("MainForm", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainForm = QtWidgets.QWidget()
    ui = Ui_MainForm()
    ui.setupUi(MainForm)
    MainForm.show()
    sys.exit(app.exec_())

