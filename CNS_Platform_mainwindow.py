from PySide2.QtWidgets import QApplication, QWidget
from Interface import CNS_Platform_mainwindow as CNS_Main_window


class CNS_mw(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = CNS_Main_window.Ui_Dialog()
        self.ui.setupUi(self)
        self.show()