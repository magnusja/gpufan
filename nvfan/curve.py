"""This module contains Curve class.

A Curve is used for converting temperature to fan speed based on
a curve constructed by custom points.

Credit: https://gist.github.com/byaka/6337021.
"""


class Curve(object):
    """Curve object represents a curve constructed using custom points.

    If you want to provide custom points, make sure the GPU's thermal threshold
    is set as the latest point. Otherwise, if temperature reaches above the latest
    point, the function returns None.

    Arguments
    ---------
    curve_point_array list : a list of tuples of the form (temperature, fanspeed)
    """

    def __init__(self, curve_point_array=([20, 20],
                                          [40, 30],
                                          [50, 35], [59, 40],
                                          [60, 50], [64, 60],
                                          [68, 65], [70, 75],
                                          [80, 85], [86, 92],
                                          [100, 100])):  # noqa: D107
        self.cpa = curve_point_array

    def evaluate(self, x):
        """Evaluate the curve function for the temperature x.

        Arguments
        ---------
        x int : the temperature
        """
        point_i = 0
        while point_i < len(self.cpa) - 1:
            if self.cpa[point_i][0] <= x < self.cpa[point_i + 1][0]:
                point_1 = self.cpa[point_i]
                point_2 = self.cpa[point_i + 1]
                delta_x = point_2[0] - point_1[0]
                delta_y = point_2[1] - point_1[1]
                gradient = float(delta_y) / float(delta_x)
                x_bit = x - point_1[0]
                y_bit = int(float(x_bit) * gradient)
                y = point_1[1] + y_bit
                return y

            point_i += 1
