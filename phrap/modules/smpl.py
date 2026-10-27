import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def plot(xlist, ylist, xlabel='X-axis', ylabel='Y-axis', title='Plot'):
    fig, ax = plt.subplots()
    print("Average:", sum(ylist) / len(ylist))
    ax.plot(xlist, ylist)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.show()

def plot2(xlist, ylist, zlist, xlabel='X-axis', ylabel='Y-axis', title='Plot'):
    fig, ax = plt.subplots()
    ax.plot(xlist, ylist, label="Before")
    ax.plot(xlist, zlist, label="After")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.legend()
    plt.show()