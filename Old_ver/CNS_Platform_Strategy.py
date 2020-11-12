from PySide2.QtWidgets import QDialog, QApplication, QMessageBox, QWidget
from PySide2.QtGui import QFont

from Interface import CNS_Platform_Strategy as Strategy
from CNS_Platform_Strategy_Flowchart import ab_make_flowchart, nor_make_flowchart
import CNS_Platform_PARA as PARA

class Strategy_interface(QWidget):
    def __init__(self, trig_mem):
        self.trig_mem = trig_mem
        QWidget.__init__(self)

        self.init_widget()
        self.show_flowchart()
        self.show()

    def init_widget(self):
        self.main_ui = Strategy()
        self.main_ui.setupUi(self)                                                          #만약 self 없으면 어떻게 되?

        self.font = QFont("Calibri", 14, QFont.Bold)
        self.main_ui.Sec_label.setFont(self.font)
        self.main_ui.Sec_label_2.setFont(self.font)
        self.main_ui.Fou_label.setFont(self.font)

    def show_flowchart(self):
        if self.trig_mem['OPStrategy'] == PARA.Abnormal:
            ab_make_flowchart(self.trig_mem, self.main_ui.SA_widget)
            self.main_ui.Sec_label.setText('Abnormal Operation')
            self.main_ui.Sec_label_2.setText('RCS Leak')
            self.main_ui.Fou_label.setText('Autonomous Control By LSTM')

        elif self.trig_mem['OPStrategy'] == PARA.Normal:
            nor_make_flowchart(self.trig_mem, self.main_ui.SA_widget)
            self.main_ui.Sec_label.setText('Normal Operation')
            self.main_ui.Sec_label_2.setText('Startup')
            self.main_ui.Fou_label.setText('Autonomous Control By RL')
        else:
            pass