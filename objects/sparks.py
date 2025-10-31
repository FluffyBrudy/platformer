from random import choice
from typing import List, Set, Tuple, Union
import pygame
import math

from constants import BASE_SPEED, PROJECTILE_SPEED_LIMIT


SPARK_COLORS = (
    (57, 255, 20),
    (0, 255, 144),
    (255, 255, 20),
    (100, 149, 237),
    (0, 255, 255),
    (65, 105, 225),
    (255, 90, 0),
    (255, 0, 0),
    (255, 69, 0),
    (255, 0, 144),
    (148, 0, 211),
    (255, 20, 147),
    (255, 255, 255),
    (255, 255, 0),
    (0, 206, 209),
    (123, 104, 238),
    (220, 20, 60),
    (64, 224, 208),
    (255, 140, 0),
    (50, 205, 50),
    (199, 21, 133),
)


class Spark:
    __slots__ = ("pos", "angle", "speed", "color_index")
    angle_offset = [0, math.pi / 2, math.pi, -math.pi / 2]
    scaler = [3, 0.5, 3, 0.5]
    _all_sparks: Set["Spark"] = set()

    def __init__(self, pos: Tuple[float, float], angle: float, speed: float) -> None:
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color_index = 0
        Spark._all_sparks.add(self)

    def update(self, dt: float) -> bool:
        polar_x = math.cos(self.angle) * self.speed
        polar_y = math.sin(self.angle) * self.speed
        self.pos[0] += polar_x * dt * BASE_SPEED
        self.pos[1] += polar_y * dt * BASE_SPEED
        self.speed = max(self.speed - 0.1, PROJECTILE_SPEED_LIMIT)
        self.color_index = (self.color_index + 1) % len(SPARK_COLORS)
        return self.speed == PROJECTILE_SPEED_LIMIT

    def render(
        self, surf: pygame.Surface, offset: Tuple[int, int] | pygame.Vector2 = (0, 0)
    ):
        render_points = [
            (
                int(
                    self.pos[0]
                    + math.cos(self.angle + a) * self.speed * Spark.scaler[i] * -1
                )
                - offset[0],
                int(
                    self.pos[1]
                    + math.sin(self.angle + a) * self.speed * Spark.scaler[i] * -1
                )
                - offset[1],
            )
            for i, a in enumerate(Spark.angle_offset)
        ]

        color = SPARK_COLORS[self.color_index]
        pygame.draw.polygon(surf, color, render_points)

    @classmethod
    def render_sparks(
        cls, surf: "pygame.Surface", dt: float, offset: Tuple[int, int] = (0, 0)
    ):
        print(len(cls._all_sparks))
        to_remove = []
        for spark in cls._all_sparks:
            if spark.update(dt):
                to_remove.append(spark)
            spark.render(surf, offset)

        for spark in to_remove:
            Spark._all_sparks.remove(spark)
