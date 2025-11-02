import math
from random import random
from pygame.typing import Point

from objects.sparks import Spark


def add_sparks(
    position: Point,
    angle: float,
    displacement: Point = (0, 0),
    count: int = 8,
    scale_delta: Point = (0, 0),
):
    for _ in range(count):
        pos = (
            position[0] + displacement[0],
            position[1] + displacement[1],
        )
        Spark(pos, random() - 0.5 + angle, 2 + random(), scale_delta)


def radial_sparks(
    position, speed: float, parts=12, displacement=(0, 0), scale_delta=(0, 0)
):
    for i in range(parts):
        angle = (i / parts) * 2 * math.pi
        Spark(
            (position[0] + displacement[0], position[1] + displacement[1]),
            angle,
            speed,
            scale_delta,
        )
