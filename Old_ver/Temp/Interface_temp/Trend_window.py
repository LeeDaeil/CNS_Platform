# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Trend_window.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(700, 571)
        self.Rod_1 = QtWidgets.QLabel(Dialog)
        self.Rod_1.setGeometry(QtCore.QRect(10, 70, 41, 141))
        self.Rod_1.setStyleSheet("background-color: rgb(0, 22, 147);")
        self.Rod_1.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_1.setText("")
        self.Rod_1.setObjectName("Rod_1")
        self.Rod_1_back = QtWidgets.QLabel(Dialog)
        self.Rod_1_back.setGeometry(QtCore.QRect(10, 70, 41, 228))
        self.Rod_1_back.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.Rod_1_back.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_1_back.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Rod_1_back.setLineWidth(1)
        self.Rod_1_back.setText("")
        self.Rod_1_back.setObjectName("Rod_1_back")
        self.Rod_2 = QtWidgets.QLabel(Dialog)
        self.Rod_2.setGeometry(QtCore.QRect(70, 70, 41, 141))
        self.Rod_2.setStyleSheet("background-color: rgb(0, 22, 147);")
        self.Rod_2.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_2.setText("")
        self.Rod_2.setObjectName("Rod_2")
        self.Rod_2_back = QtWidgets.QLabel(Dialog)
        self.Rod_2_back.setGeometry(QtCore.QRect(70, 70, 41, 228))
        self.Rod_2_back.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.Rod_2_back.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_2_back.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Rod_2_back.setLineWidth(1)
        self.Rod_2_back.setText("")
        self.Rod_2_back.setObjectName("Rod_2_back")
        self.Rod_3_back = QtWidgets.QLabel(Dialog)
        self.Rod_3_back.setGeometry(QtCore.QRect(130, 70, 41, 228))
        self.Rod_3_back.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.Rod_3_back.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_3_back.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Rod_3_back.setLineWidth(1)
        self.Rod_3_back.setText("")
        self.Rod_3_back.setObjectName("Rod_3_back")
        self.Rod_4_back = QtWidgets.QLabel(Dialog)
        self.Rod_4_back.setGeometry(QtCore.QRect(190, 70, 41, 228))
        self.Rod_4_back.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.Rod_4_back.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_4_back.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Rod_4_back.setLineWidth(1)
        self.Rod_4_back.setText("")
        self.Rod_4_back.setObjectName("Rod_4_back")
        self.Rod_3 = QtWidgets.QLabel(Dialog)
        self.Rod_3.setGeometry(QtCore.QRect(130, 70, 41, 141))
        self.Rod_3.setStyleSheet("background-color: rgb(0, 22, 147);")
        self.Rod_3.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_3.setText("")
        self.Rod_3.setObjectName("Rod_3")
        self.Rod_4 = QtWidgets.QLabel(Dialog)
        self.Rod_4.setGeometry(QtCore.QRect(190, 70, 41, 141))
        self.Rod_4.setStyleSheet("background-color: rgb(0, 22, 147);")
        self.Rod_4.setFrameShape(QtWidgets.QFrame.Box)
        self.Rod_4.setText("")
        self.Rod_4.setObjectName("Rod_4")
        self.Dis_Rod_1 = QtWidgets.QLabel(Dialog)
        self.Dis_Rod_1.setGeometry(QtCore.QRect(10, 50, 41, 20))
        self.Dis_Rod_1.setStyleSheet("font: 9pt \"HY헤드라인M\";\n"
"background-color: rgb(255, 255, 255);")
        self.Dis_Rod_1.setFrameShape(QtWidgets.QFrame.Box)
        self.Dis_Rod_1.setAlignment(QtCore.Qt.AlignCenter)
        self.Dis_Rod_1.setObjectName("Dis_Rod_1")
        self.Dis_Rod_2 = QtWidgets.QLabel(Dialog)
        self.Dis_Rod_2.setGeometry(QtCore.QRect(70, 50, 41, 20))
        self.Dis_Rod_2.setStyleSheet("font: 9pt \"HY헤드라인M\";\n"
"background-color: rgb(255, 255, 255);")
        self.Dis_Rod_2.setFrameShape(QtWidgets.QFrame.Box)
        self.Dis_Rod_2.setAlignment(QtCore.Qt.AlignCenter)
        self.Dis_Rod_2.setObjectName("Dis_Rod_2")
        self.Dis_Rod_3 = QtWidgets.QLabel(Dialog)
        self.Dis_Rod_3.setGeometry(QtCore.QRect(130, 50, 41, 20))
        self.Dis_Rod_3.setStyleSheet("font: 9pt \"HY헤드라인M\";\n"
"background-color: rgb(255, 255, 255);")
        self.Dis_Rod_3.setFrameShape(QtWidgets.QFrame.Box)
        self.Dis_Rod_3.setAlignment(QtCore.Qt.AlignCenter)
        self.Dis_Rod_3.setObjectName("Dis_Rod_3")
        self.Dis_Rod_4 = QtWidgets.QLabel(Dialog)
        self.Dis_Rod_4.setGeometry(QtCore.QRect(190, 50, 41, 20))
        self.Dis_Rod_4.setStyleSheet("font: 9pt \"HY헤드라인M\";\n"
"background-color: rgb(255, 255, 255);")
        self.Dis_Rod_4.setFrameShape(QtWidgets.QFrame.Box)
        self.Dis_Rod_4.setAlignment(QtCore.Qt.AlignCenter)
        self.Dis_Rod_4.setObjectName("Dis_Rod_4")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 310, 681, 181))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.Rod_his = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.Rod_his.setContentsMargins(0, 0, 0, 0)
        self.Rod_his.setObjectName("Rod_his")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 680, 30))
        self.label.setStyleSheet("background-color: rgb(178, 206, 240);\n"
"border-style: outset;\n"
"border-width: 2px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 700, 700))
        self.label_2.setStyleSheet("background-color:rgb(216, 216, 216);")
        self.label_2.setText("")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 510, 110, 40))
        self.label_3.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 0.5px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 500, 680, 61))
        self.label_4.setStyleSheet("background-color: rgb(221, 221, 221);\n"
"border-style: outset;\n"
"border-width: 2px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label_4.setText("")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(140, 510, 110, 40))
        self.label_5.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 0.5px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.rodup = QtWidgets.QPushButton(Dialog)
        self.rodup.setGeometry(QtCore.QRect(270, 510, 200, 40))
        self.rodup.setStyleSheet("QPushButton {\n"
"    background-color: rgb(255, 255, 255);\n"
"    border-style: outset;\n"
"    border-width: 0.5px;\n"
"    border-color: black;\n"
"    font: bold 35px;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: rgb(220, 220, 220);\n"
"    border-style: inset;\n"
"}")
        self.rodup.setObjectName("rodup")
        self.roddown = QtWidgets.QPushButton(Dialog)
        self.roddown.setGeometry(QtCore.QRect(480, 510, 200, 40))
        self.roddown.setStyleSheet("QPushButton {\n"
"    background-color: rgb(255, 255, 255);\n"
"    border-style: outset;\n"
"    border-width: 0.5px;\n"
"    border-color: black;\n"
"    font: bold 35px;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: rgb(220, 220, 220);\n"
"    border-style: inset;\n"
"}")
        self.roddown.setObjectName("roddown")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(240, 70, 451, 231))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.Rod_his_cond = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.Rod_his_cond.setContentsMargins(0, 0, 0, 0)
        self.Rod_his_cond.setObjectName("Rod_his_cond")
        self.label_2.raise_()
        self.Rod_2_back.raise_()
        self.Rod_1_back.raise_()
        self.Rod_4_back.raise_()
        self.Rod_3_back.raise_()
        self.Rod_1.raise_()
        self.Rod_2.raise_()
        self.Rod_3.raise_()
        self.Rod_4.raise_()
        self.Dis_Rod_1.raise_()
        self.Dis_Rod_2.raise_()
        self.Dis_Rod_3.raise_()
        self.Dis_Rod_4.raise_()
        self.horizontalLayoutWidget.raise_()
        self.label.raise_()
        self.label_4.raise_()
        self.label_3.raise_()
        self.label_5.raise_()
        self.rodup.raise_()
        self.roddown.raise_()
        self.horizontalLayoutWidget_2.raise_()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.Dis_Rod_1.setText(_translate("Dialog", "100"))
        self.Dis_Rod_2.setText(_translate("Dialog", "100"))
        self.Dis_Rod_3.setText(_translate("Dialog", "100"))
        self.Dis_Rod_4.setText(_translate("Dialog", "100"))
        self.label.setText(_translate("Dialog", "Autonomous Rod Controller"))
        self.label_3.setText(_translate("Dialog", "Manual\n"
"Control"))
        self.label_5.setText(_translate("Dialog", "Autonomous\n"
"Control"))
        self.rodup.setText(_translate("Dialog", "▲"))
        self.roddown.setText(_translate("Dialog", "▼"))

