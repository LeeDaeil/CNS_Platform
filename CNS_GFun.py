import multiprocessing
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

class gfunction(multiprocessing.Process):
    def __init__(self, mem):
        multiprocessing.Process.__init__(self)
        self.mem = mem[0]
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1, 1, 1)

    def animate(self, i):
        self.ax1.clear()
        print(self, self.mem['KCNTOMS']['L'])
        if self.mem['KCNTOMS']['L'] != []:
            self.draw_animate()

    def draw_animate(self):
        temp_x = []
        for _ in range(0, len(self.mem['KCNTOMS']['L'])):
            temp_x.append(_)
        self.ax1.plot(temp_x, self.mem['KCNTOMS']['L'], label='Result', linewidth=1)

    def run(self):
        print(self.name, 'gfunction start')
        self.ani = FuncAnimation(self.fig, self.animate, interval=1000)
        plt.show()

