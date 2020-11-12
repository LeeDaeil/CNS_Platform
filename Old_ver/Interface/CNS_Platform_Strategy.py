# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CNS_Platform_Strategy.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_MainForm(object):
    def setupUi(self, MainForm):
        if not MainForm.objectName():
            MainForm.setObjectName(u"MainForm")
        MainForm.resize(972, 887)
        MainForm.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));")
        self.Top_label = QLabel(MainForm)
        self.Top_label.setObjectName(u"Top_label")
        self.Top_label.setGeometry(QRect(10, 10, 950, 51))
        font = QFont()
        font.setFamily(u"Calibri")
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.Top_label.setFont(font)
        self.Top_label.setLayoutDirection(Qt.LeftToRight)
        self.Top_label.setAlignment(Qt.AlignCenter)
        self.Fir_label = QLabel(MainForm)
        self.Fir_label.setObjectName(u"Fir_label")
        self.Fir_label.setGeometry(QRect(10, 90, 121, 40))
        font1 = QFont()
        font1.setFamily(u"Calibri")
        font1.setPointSize(18)
        font1.setBold(True)
        font1.setWeight(75)
        self.Fir_label.setFont(font1)
        self.Fir_label.setStyleSheet(u"background-color: rgb(225, 224, 224);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0,0,0);\n"
"border-radius: 5px;\n"
"\n"
"")
        self.Fir_label.setAlignment(Qt.AlignCenter)
        self.Fou_label = QLabel(MainForm)
        self.Fou_label.setObjectName(u"Fou_label")
        self.Fou_label.setGeometry(QRect(710, 90, 251, 40))
        self.Fou_label.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")
        self.Thi_label = QLabel(MainForm)
        self.Thi_label.setObjectName(u"Thi_label")
        self.Thi_label.setGeometry(QRect(580, 90, 121, 40))
        self.Thi_label.setFont(font1)
        self.Thi_label.setStyleSheet(u"background-color: rgb(225, 224, 224);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")
        self.Thi_label.setAlignment(Qt.AlignCenter)
        self.Sec_label = QLabel(MainForm)
        self.Sec_label.setObjectName(u"Sec_label")
        self.Sec_label.setGeometry(QRect(140, 90, 211, 40))
        self.Sec_label.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")
        self.btn_close = QPushButton(MainForm)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setGeometry(QRect(850, 850, 111, 31))
        self.frame = QFrame(MainForm)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 140, 951, 701))
        self.frame.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.SA = QScrollArea(self.frame)
        self.SA.setObjectName(u"SA")
        self.SA.setGeometry(QRect(0, 0, 951, 701))
        self.SA.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.SA.setWidgetResizable(True)
        self.SA_widget = QWidget()
        self.SA_widget.setObjectName(u"SA_widget")
        self.SA_widget.setGeometry(QRect(0, 0, 932, 699))
        self.SA.setWidget(self.SA_widget)
        self.Sec_label_2 = QLabel(MainForm)
        self.Sec_label_2.setObjectName(u"Sec_label_2")
        self.Sec_label_2.setGeometry(QRect(360, 90, 211, 40))
        self.Sec_label_2.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-style: outset;\n"
"border-width: 1px;\n"
"border-color: rgb(0, 0, 0);\n"
"border-radius: 5px;")

        self.retranslateUi(MainForm)

        QMetaObject.connectSlotsByName(MainForm)
    # setupUi

    def retranslateUi(self, MainForm):
        MainForm.setWindowTitle(QCoreApplication.translate("MainForm", u"Form", None))
        self.Top_label.setText(QCoreApplication.translate("MainForm", u"Strategy Selection Function", None))
        self.Fir_label.setText(QCoreApplication.translate("MainForm", u"Plant state", None))
        self.Fou_label.setText(QCoreApplication.translate("MainForm", u"TextLabel", None))
        self.Thi_label.setText(QCoreApplication.translate("MainForm", u"Strategy", None))
        self.Sec_label.setText(QCoreApplication.translate("MainForm", u"TextLabel", None))
        self.btn_close.setText(QCoreApplication.translate("MainForm", u"Close", None))
        self.Sec_label_2.setText(QCoreApplication.translate("MainForm", u"TextLabel", None))
    # retranslateUi

