# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CNS_Platform_controller_interface.ui'
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


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(269, 383)
        self.Run = QPushButton(Form)
        self.Run.setObjectName(u"Run")
        self.Run.setGeometry(QRect(10, 10, 120, 23))
        self.Freeze = QPushButton(Form)
        self.Freeze.setObjectName(u"Freeze")
        self.Freeze.setGeometry(QRect(140, 10, 120, 23))
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 140, 251, 171))
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Raised)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(5, 5, 130, 16))
        self.Go_mal = QPushButton(self.frame)
        self.Go_mal.setObjectName(u"Go_mal")
        self.Go_mal.setGeometry(QRect(10, 140, 231, 23))
        self.Mal_list = QListWidget(self.frame)
        self.Mal_list.setObjectName(u"Mal_list")
        self.Mal_list.setGeometry(QRect(10, 80, 231, 51))
        self.Mal_nub = QLineEdit(self.frame)
        self.Mal_nub.setObjectName(u"Mal_nub")
        self.Mal_nub.setGeometry(QRect(70, 30, 50, 20))
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 30, 60, 20))
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(130, 30, 60, 20))
        self.Mal_type = QLineEdit(self.frame)
        self.Mal_type.setObjectName(u"Mal_type")
        self.Mal_type.setGeometry(QRect(190, 30, 50, 20))
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 50, 60, 20))
        self.Mal_time = QLineEdit(self.frame)
        self.Mal_time.setObjectName(u"Mal_time")
        self.Mal_time.setGeometry(QRect(70, 50, 50, 20))
        self.frame_2 = QFrame(Form)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(10, 40, 251, 41))
        self.frame_2.setFrameShape(QFrame.Box)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.Initial = QPushButton(self.frame_2)
        self.Initial.setObjectName(u"Initial")
        self.Initial.setGeometry(QRect(10, 10, 75, 22))
        self.Initial_list = QComboBox(self.frame_2)
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.addItem("")
        self.Initial_list.setObjectName(u"Initial_list")
        self.Initial_list.setGeometry(QRect(90, 10, 151, 22))
        self.Go_db = QPushButton(Form)
        self.Go_db.setObjectName(u"Go_db")
        self.Go_db.setGeometry(QRect(20, 320, 231, 23))
        self.Show_main_win = QPushButton(Form)
        self.Show_main_win.setObjectName(u"Show_main_win")
        self.Show_main_win.setGeometry(QRect(20, 350, 231, 23))
        self.frame_3 = QFrame(Form)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setGeometry(QRect(10, 90, 251, 41))
        self.frame_3.setFrameShape(QFrame.Box)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.label_5 = QLabel(self.frame_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 10, 60, 20))
        self.Se_SP = QLineEdit(self.frame_3)
        self.Se_SP.setObjectName(u"Se_SP")
        self.Se_SP.setGeometry(QRect(120, 10, 61, 20))
        self.Apply_Sp = QPushButton(self.frame_3)
        self.Apply_Sp.setObjectName(u"Apply_Sp")
        self.Apply_Sp.setGeometry(QRect(190, 10, 51, 23))
        self.Cu_SP = QLabel(self.frame_3)
        self.Cu_SP.setObjectName(u"Cu_SP")
        self.Cu_SP.setGeometry(QRect(60, 10, 41, 20))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.Run.setText(QCoreApplication.translate("Form", u"Run", None))
        self.Freeze.setText(QCoreApplication.translate("Form", u"Freeze", None))
        self.label.setText(QCoreApplication.translate("Form", u"Malfunction", None))
        self.Go_mal.setText(QCoreApplication.translate("Form", u"Go Malfunction", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Mal_nub", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Mal_type", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Mal_time", None))
        self.Initial.setText(QCoreApplication.translate("Form", u"(1) Initial", None))
        self.Initial_list.setItemText(0, QCoreApplication.translate("Form", u"1. 100%", None))
        self.Initial_list.setItemText(1, QCoreApplication.translate("Form", u"2. 80%", None))
        self.Initial_list.setItemText(2, QCoreApplication.translate("Form", u"3. 70%", None))
        self.Initial_list.setItemText(3, QCoreApplication.translate("Form", u"4. 60% (??)", None))
        self.Initial_list.setItemText(4, QCoreApplication.translate("Form", u"5. 13% (??)", None))
        self.Initial_list.setItemText(5, QCoreApplication.translate("Form", u"6. 7% (??)", None))
        self.Initial_list.setItemText(6, QCoreApplication.translate("Form", u"7. 2% (??)", None))
        self.Initial_list.setItemText(7, QCoreApplication.translate("Form", u"8. Reactor Critical", None))
        self.Initial_list.setItemText(8, QCoreApplication.translate("Form", u"9. Hotstandby", None))
        self.Initial_list.setItemText(9, QCoreApplication.translate("Form", u"10. Hotshutdown", None))
        self.Initial_list.setItemText(10, QCoreApplication.translate("Form", u"11. Cold shutdown", None))
        self.Initial_list.setItemText(11, QCoreApplication.translate("Form", u"12. Hot standby", None))
        self.Initial_list.setItemText(12, QCoreApplication.translate("Form", u"13. Cold shutdown 1", None))
        self.Initial_list.setItemText(13, QCoreApplication.translate("Form", u"14. Hot showdown(colddown)", None))
        self.Initial_list.setItemText(14, QCoreApplication.translate("Form", u"15. Hot shut to Hot standby", None))
        self.Initial_list.setItemText(15, QCoreApplication.translate("Form", u"16. Test 70%", None))
        self.Initial_list.setItemText(16, QCoreApplication.translate("Form", u"17. 2%(real)", None))
        self.Initial_list.setItemText(17, QCoreApplication.translate("Form", u"18. d", None))
        self.Initial_list.setItemText(18, QCoreApplication.translate("Form", u"19. REAL2%", None))
        self.Initial_list.setItemText(19, QCoreApplication.translate("Form", u"20. 2% to ALL", None))

        self.Go_db.setText(QCoreApplication.translate("Form", u"Save_DB", None))
        self.Show_main_win.setText(QCoreApplication.translate("Form", u"Show Interface", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Speed", None))
        self.Apply_Sp.setText(QCoreApplication.translate("Form", u"\uc801\uc6a9", None))
        self.Cu_SP.setText(QCoreApplication.translate("Form", u"1", None))
    # retranslateUi
