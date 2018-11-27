import threading
import time

class PMF_function(threading.Thread):
    def __init__(self, UDP):
        threading.Thread.__init__(self)
        self.UDP_data = UDP
        self.result = []

    def run(self):
        while True:
            if self.UDP_data.list_mem_length != len(self.result):
                self.calculator()

    def calculator(self):
        self.result = []

        for __ in range(0, self.UDP_data.list_mem_length):
            pressure = self.UDP_data.list_mem['QPROLD']['Val'][__]
            if 154.7 < pressure < 161.6 and 286.7 < pressure < 293.3:
                self.result.append(1)
            else:
                self.result.append(0)



