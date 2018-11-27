import multiprocessing
import matplotlib.pyplot as plt
import time

from CNS_Fun import PMF_function
from CNS_UDP import *
from CNS_GFun import *


class Top(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        UDP = UDPSocket(IP='', Port=7001)
        fun1 = PMF_function(UDP)
        UDP.start()
        fun1.start()

        time.sleep(1)

        gfun1 = gfunction(UDP)
        gfun2 = PMF_gfunction(fun1)

        gfun1.start()
        gfun2.start()

        plt.show()

if __name__ == '__main__':
    Top().start()