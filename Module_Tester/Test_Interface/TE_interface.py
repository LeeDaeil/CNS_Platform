# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TE_interface.ui',
# licensing of 'TE_interface.ui' applies.
#
# Created: Tue Sep  3 22:25:16 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(269, 221)
        self.Run = QtWidgets.QPushButton(Form)
        self.Run.setGeometry(QtCore.QRect(10, 10, 75, 23))
        self.Run.setObjectName("Run")
        self.Freeze = QtWidgets.QPushButton(Form)
        self.Freeze.setGeometry(QtCore.QRect(90, 10, 75, 23))
        self.Freeze.setObjectName("Freeze")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 40, 251, 171))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(5, 5, 130, 16))
        self.label.setObjectName("label")
        self.Go_mal = QtWidgets.QPushButton(self.frame)
        self.Go_mal.setGeometry(QtCore.QRect(10, 140, 231, 23))
        self.Go_mal.setObjectName("Go_mal")
        self.Mal_list = QtWidgets.QListWidget(self.frame)
        self.Mal_list.setGeometry(QtCore.QRect(10, 80, 231, 51))
        self.Mal_list.setObjectName("Mal_list")
        self.Mal_nub = QtWidgets.QLineEdit(self.frame)
        self.Mal_nub.setGeometry(QtCore.QRect(70, 30, 50, 20))
        self.Mal_nub.setObjectName("Mal_nub")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 60, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(130, 30, 60, 20))
        self.label_3.setObjectName("label_3")
        self.Mal_type = QtWidgets.QLineEdit(self.frame)
        self.Mal_type.setGeometry(QtCore.QRect(190, 30, 50, 20))
        self.Mal_type.setObjectName("Mal_type")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(10, 50, 60, 20))
        self.label_4.setObjectName("label_4")
        self.Mal_time = QtWidgets.QLineEdit(self.frame)
        self.Mal_time.setGeometry(QtCore.QRect(70, 50, 50, 20))
        self.Mal_time.setObjectName("Mal_time")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.Run.setText(QtWidgets.QApplication.translate("Form", "Run", None, -1))
        self.Freeze.setText(QtWidgets.QApplication.translate("Form", "Freeze", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Form", "Malfunction", None, -1))
        self.Go_mal.setText(QtWidgets.QApplication.translate("Form", "Go Malfunction", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Form", "Mal_nub", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("Form", "Mal_type", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("Form", "Mal_time", None, -1))

