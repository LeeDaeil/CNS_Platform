# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'A_Event Diagnosis Module.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(850, 600)
        Dialog.setStyleSheet("background-color:rgb(216, 216, 216);")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 49, 801, 451))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 801, 30))
        self.label.setStyleSheet("background-color: rgb(172, 255, 127);\n"
"border-style: outset;\n"
"border-width: 2px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 520, 831, 60))
        self.label_2.setStyleSheet("border-style: outset;\n"
"border-width: 2px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(19, 530, 151, 40))
        self.label_3.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 0.5px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(180, 530, 651, 40))
        self.label_4.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 0.5px;\n"
"border-color: black;\n"
"font: bold 14px;")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Abnormal Event Diagnosis Module"))
        self.label_3.setText(_translate("Dialog", "Event"))
        self.label_4.setText(_translate("Dialog", "TextLabel"))

