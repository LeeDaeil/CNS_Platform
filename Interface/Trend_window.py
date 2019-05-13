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
        Dialog.resize(497, 471)
        self.Test_label = QtWidgets.QLabel(Dialog)
        self.Test_label.setGeometry(QtCore.QRect(10, 10, 56, 12))
        self.Test_label.setObjectName("Test_label")
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(10, 30, 256, 192))
        self.listWidget.setObjectName("listWidget")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.Test_label.setText(_translate("Dialog", "Value"))

