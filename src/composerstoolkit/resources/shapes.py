from __future__ import annotations
import math
from typing import Tuple, List, Optional

class Curve:
    def __init__(self,
                 bounds_x: Tuple[int, int],
                 bounds_y: Tuple[int, int],
                 bounds_deg: Tuple[int, int] = (0, 360),
                 f=math.sin,
                 modulators: Optional[List[Curve]] = None,
                 amplitude_modulators: Optional[List[Curve]] = None):
        """
        Used to modulate a musical parameter (y) as a function of time on a sine wave
        For example, pitch, duration, dynamic
        bounds_x: the range of time over which the curve will be applied
        bounds_y: the range of values of the curve, from trough to peak
        bounds_deg: how many degs the curve occupies. (A range of 0-360 is a complete up-down cycle for a sine).
        f: the curve function (typically math.sin or math.cos or your functor)
        modulators: other wave forms to modulate this carrier wave with to produce a more complex shape.
        """
        self.bounds_x = bounds_x
        self.bounds_y = bounds_y
        self.bounds_deg = bounds_deg
        self.f = f
        self.modulators = []
        if modulators is not None:
            self.modulators = modulators
        self.amplitude_modulators = []
        if amplitude_modulators is not None:
            self.amplitude_modulators = amplitude_modulators

    @property
    def x_min(self):
        return self.bounds_x[0]

    @property
    def x_max(self):
        return self.bounds_x[1]

    @property
    def y_min(self):
        return self.bounds_y[0]

    @property
    def y_max(self):
        return self.bounds_y[1]

    @property
    def start_deg(self):
        return self.bounds_deg[0]

    @property
    def end_deg(self):
        return self.bounds_deg[1]

    @property
    def degrees(self):
        return self.end_deg - self.start_deg

    def y(self, x, modulate=True):
        """
        Solve the y value for the given x (time) on the graph
        """
        if self.y_min < self.y_max:
            angle = (x / self.x_max) * self.degrees + self.start_deg
        else:
            angle = ((x / self.x_max) * self.degrees) + 180 + self.start_deg
        radians = math.radians(angle)
        val = self.f(math.radians(angle))
        y = math.ceil(val * (abs(self.y_max - self.y_min))) + self.y_min
        if modulate:
            y = self._apply_modulators(x, y)
        return y

    def _apply_modulators(self, x, y):
        values = [y] + [mod.y(x) for mod in self.modulators]
        val = sum(values) / len(values)
        if len(self.amplitude_modulators) == 0:
            return val
        x_range = self.x_max - self.x_min
        values = [(mod.y(x)/x_range) * val for mod in self.amplitude_modulators]
        return sum(values) / len(values)

    def plot(self, x_label="Time (Beats)", y_label=""):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min
        ax.plot(range(x_range), [(self.y(i)) for i in range(x_range)])
        plt.show()
