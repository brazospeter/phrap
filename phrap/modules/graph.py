import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy

class table2:
    def __init__(self):
        self.xlist = []
        self.ylist = []
    def add_data(self, x, y):
        self.xlist.append(x)
        self.ylist.append(y)
    def plot(self):
        fig, ax = plt.subplots()
        new_xlist = numpy.array(self.xlist)
        new_ylist = numpy.array(self.ylist)
        ax.plot(self.xlist, new_ylist)
        plt.show()
    def scatter(self):
        fig, ax = plt.subplots()
        new_xlist = numpy.array(self.xlist)
        new_ylist = numpy.array(self.ylist)
        ax.scatter(self.xlist, new_ylist)
        plt.show()

class table3:
    xlist = []
    ylist = []
    zlist = []

    def add_data(self, x, y, z):
        self.xlist.append(x)
        self.ylist.append(y)
        self.zlist.append(z)
    def plot(self):
        plt.locator_params(axis='x', nbins=5)
        plt.plot(self.xlist, self.ylist)
        plt.plot(self.xlist, self.zlist)
        plt.show()