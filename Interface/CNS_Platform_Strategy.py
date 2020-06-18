# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './/Interface\CNS_Platform_Strategy.ui',
# licensing of './/Interface\CNS_Platform_Strategy.ui' applies.
#
# Created: Thu Jun 18 17:52:08 2020
#      by: pyside2-uic  running on PySide2 5.13.2
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
        font.setWeight(75)
        font.setBold(True)
        self.Top_label.setFont(font)
        self.Top_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Top_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Top_label.setObjectName("Top_label")
        self.Fir_label = QtWidgets.QLabel(MainForm)
        self.Fir_label.setGeometry(QtCore.QRect(10, 90, 121, 40))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
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
        font.setWeight(75)
        font.setBold(True)
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
        MainForm.setWindowTitle(QtWidgets.QApplication.translate("MainForm", "Form", None, -1))
        self.Top_label.setText(QtWidgets.QApplication.translate("MainForm", "Strategy Selection Function", None, -1))
        self.Fir_label.setText(QtWidgets.QApplication.translate("MainForm", "Plant state", None, -1))
        self.Fou_label.setText(QtWidgets.QApplication.translate("MainForm", "TextLabel", None, -1))
        self.Thi_label.setText(QtWidgets.QApplication.translate("MainForm", "Strategy", None, -1))
        self.Sec_label.setText(QtWidgets.QApplication.translate("MainForm", "TextLabel", None, -1))
        self.btn_close.setText(QtWidgets.QApplication.translate("MainForm", "Close", None, -1))
        self.Sec_label_2.setText(QtWidgets.QApplication.translate("MainForm", "TextLabel", None, -1))

