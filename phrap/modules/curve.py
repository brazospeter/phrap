from loguru import logger
from scipy.integrate import simpson as scipy_integrate

from .smpl import plot, plot2

class Curve:
    def __init__(self, values: dict = None):
        if values is None:
            self.values = {}
        else:
            self.values = values

    def lookup(self, input: dict, key: str, interpolate: bool = True):
        try:
            ylist = self.values[key]
            for k, v in input.items():
                xlist = self.values[k]
                for i in range(len(xlist)):
                    if xlist[i] >= v:
                        if interpolate and i > 0:
                            # Perform linear interpolation
                            x0, x1 = xlist[i-1], xlist[i]
                            y0, y1 = ylist[i-1], ylist[i]
                            if x1 != x0:
                                m = (y1 - y0) / (x1 - x0) 
                            else: 
                                m = 0
                            return y0 + m * (v - x0)
                        else:
                            return ylist[i]
                return ylist[-1]  # Return the last value if input exceeds all x values
        except:
            return None

    def append(self, data: dict):
        for k, v in data.items():
            if k in self.values:
                self.values[k].append(v)
            else:
                self.values[k] = [v]

    def plot(self, x_key: str, y_key: str, title: str = ""):
        xlist = self.values[x_key]
        ylist = self.values[y_key]
        plot(xlist, ylist, xlabel=x_key, ylabel=y_key, title=title)

    def plot2(self, x_key: str, y_key: str, z_key: str, title: str = ""):
        xlist = self.values[x_key]
        ylist = self.values[y_key]
        zlist = self.values[z_key]
        plot2(xlist, ylist, zlist, xlabel=x_key, ylabel=y_key, title=title)

    def cplot(self, x_key: str, y_key: str, second_curve, title: str = ""):
        xlist = self.values[x_key]
        ylist = self.values[y_key]
        zlist = []
        for x in xlist:
            zlist.append(second_curve.lookup({x_key: x}, y_key))
        plot2(xlist, ylist, zlist, xlabel=x_key, ylabel=y_key, title=title)

    def get(self, key: str, index: int):
        try:
            return self.values[key][index]
        except (KeyError, IndexError):
            logger.warning(f"Key '{key}' or index '{index}' is out of range.")
            return None

    def integrate(self, x_bounds: dict, y_key: str):
        for k, v in x_bounds.items():
            x_list = self.values[k].copy()
            x0 = v[0]
            x1 = v[1]
        y_list = self.values[y_key].copy()
        if x1 >= x0:
            for i in range(len(x_list)):
                if not(x0 < x_list[i] < x1):
                    y_list[i] = 0
            return scipy_integrate(y_list, x_list)
        else:
            logger.error(f"Invalid bounds: {x_bounds}. x1 must be greater than or equal to x0.")
            return 0

    def set_step(self, step: float, t_key: str):
        if t_key in self.values:
            for key, v in self.values.items():
                if key != t_key:
                    t = self.values[t_key][0]
                    new_value = []
                    while t <= self.values[t_key][-1] + step:
                        new_value.append(self.lookup({t_key: t}, key))
                        t += step
                    self.values[key] = new_value

            t = self.values[t_key][0]
            new_t_value = []
            while t <= self.values[t_key][-1] + step:
                new_t_value.append(t)
                t += step
            self.values[t_key] = new_t_value

        else:
            logger.warning(f"Key '{t_key}' not found in values.")
    
