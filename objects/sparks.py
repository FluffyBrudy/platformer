from random import choice, randint
from typing import List, Set, Tuple, Union
import pygame
import math

from pygame.typing import Point

from constants import BASE_SPEED, PROJECTILE_SPEED_LIMIT

SPARK_COLORS = (
    (255, 220, 0),
    (255, 140, 0),
    (255, 0, 0),
)


class Spark:
    __slots__ = ("pos", "angle", "speed", "color_index", "scaler_change")
    angle_offset = [0, math.pi / 2, math.pi, -math.pi / 2]
    scaler = [5, 0.8, 5, 0.8]
    _all_sparks: Set["Spark"] = set()

    def __init__(
        self,
        pos: Tuple[float, float],
        angle: float,
        speed: float,
        scaler_change: Point = (0, 0),
    ) -> None:
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color_index = randint(0, len(SPARK_COLORS) - 1)
        self.scaler_change = scaler_change
        Spark._all_sparks.add(self)

    def update(self, dt: float) -> bool:
        polar_x = math.cos(self.angle) * self.speed
        polar_y = math.sin(self.angle) * self.speed
        self.pos[0] += polar_x * dt * BASE_SPEED
        self.pos[1] += polar_y * dt * BASE_SPEED
        self.speed = max(self.speed - 0.1, PROJECTILE_SPEED_LIMIT)
        self.color_index = randint(0, len(SPARK_COLORS) - 1)
        return self.speed == PROJECTILE_SPEED_LIMIT

    def render(
        self, surf: pygame.Surface, offset: Tuple[int, int] | pygame.Vector2 = (0, 0)
    ):
        render_points = [
            (
                int(
                    self.pos[0]
                    + math.cos(self.angle + a)
                    * self.speed
                    * (Spark.scaler[i] - self.scaler_change[0])
                    * -1
                )
                - offset[0],
                int(
                    self.pos[1]
                    + math.sin(self.angle + a)
                    * self.speed
                    * (Spark.scaler[i] - self.scaler_change[1])
                    * -1
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
        to_remove = []
        for spark in cls._all_sparks:
            if spark.update(dt):
                to_remove.append(spark)
            spark.render(surf, offset)

        for spark in to_remove:
            Spark._all_sparks.remove(spark)
