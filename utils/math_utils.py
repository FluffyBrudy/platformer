from math import sin, pi
from typing import Union


def natural_x(x: Union[float, int], L: Union[float, int], scale=1):
    theta = sin(x % L) * (2 * pi / L)
    return theta * scale


def sign(n: float | int):
    return (n > 0) - (n < 0)
