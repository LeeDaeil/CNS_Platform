import threading
import time

class function(threading.Thread):
    def __init__(self, UDP, delay):
        threading.Thread.__init__(self)
        self.UDP_data = UDP
        self.time_delay = delay

    def run(self):
        while True:
            print(self.name, self.UDP_data.data, self.time_delay)
            self.UDP_data.data += 1
            time.sleep(self.time_delay)