import multiprocessing
import matplotlib.pyplot as plt
import time

from CNS_Fun import function
from CNS_UDP import *
from CNS_GFun import gfunction


class Top(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        UDP = UDPSocket(IP='', Port=7001)
        UDP.start()
        time.sleep(1)
        #fun1 = function(UDP, delay = 1)
        #fun2 = function(UDP, delay = 2)
        gfun1 = gfunction(UDP)
        #gfun2 = gfunction(UDP)

        #fun1.start()
        #fun2.start()
        gfun1.start()
        #gfun2.start()

        plt.show()

if __name__ == '__main__':
    Top().start()