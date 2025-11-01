from random import random
from typing import List, Set, Tuple, TYPE_CHECKING, Union, cast
from pygame import Rect, Vector2
from math import hypot, pi

from pygame.typing import Point
from constants import BASE_PROJECTILE_RANGE, BASE_SPEED, PROJECTILE_SPEED_LIMIT
from objects.sparks import Spark
from utils.math_utils import sign

if TYPE_CHECKING:
    from game import Game
    from pygame import Surface
    from entities import PhysicsEntity


class Projectile:
    __slots__ = ("rect", "velocity", "range", "sparks", "force_kill")
    _game_instance: "Game" = None  # type: ignore
    _all_projectiles: Set["Projectile"] = set()

    def __init__(
        self,
        game: "Game",
        pos: Tuple[int, int],
        velocity: Tuple[int, int],
        addition_range=0.0,
    ) -> None:
        if cast(None, Projectile._game_instance) is None:
            Projectile._game_instance = game
        self.rect = Rect(*pos, *game.assets["projectile"].size)
        self.velocity = Vector2(velocity)
        self.range = BASE_PROJECTILE_RANGE + addition_range
        self.force_kill = False

        Projectile._all_projectiles.add(self)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, value: object, /) -> bool:
        return self is value

    @classmethod
    def get_projectiles(cls):
        return cls._all_projectiles

    def add(self, group: Union[Set, List]):
        if isinstance(group, set):
            group.add(self)
        elif isinstance(group, list):
            group.append(self)
        Projectile._all_projectiles.add(self)

    def add_sparks(
        self,
        shift: float = 0,
        d: Point = (0, 0),
        count=8,
        scaler_change: Point = (0, 0),
    ):
        angle_shift = pi if sign(self.velocity.x) < 0 else 0
        for _ in range(count):
            pos = (
                self.rect.centerx + d[0],
                self.rect.centery + d[0],
            )
            Spark(
                pos, random() - 0.5 + angle_shift + shift, 2 + random(), scaler_change
            )

    def update(self, dt: float):
        movement_x = self.velocity.x * BASE_SPEED * dt
        movement_y = self.velocity.y * BASE_SPEED * dt
        self.rect.x += movement_x
        self.rect.y += movement_y
        self.range -= hypot(abs(movement_x), abs(movement_y))

        if self.range <= 20:
            self.add_sparks()

        wall_collide = Projectile._game_instance.tilemap.solid_tile_check(
            self.rect.center
        )
        if wall_collide is not None:
            left = wall_collide.pos[0] - self.rect.left
            self.add_sparks(pi if left else 0)
            self.force_kill = True

        return not max(PROJECTILE_SPEED_LIMIT, self.range) or self.force_kill

    def entity_collision(self, sprite: "PhysicsEntity"):
        if sprite.collision_rect.colliderect(self.rect):
            self.add_sparks(0)
            self.add_sparks(pi / 4)
            self.add_sparks(pi / 2)
            self.add_sparks(pi / 2 + pi / 4)
            self.add_sparks(pi)
            self.add_sparks(pi + pi / 4)
            self.add_sparks(-pi / 2)
            self.add_sparks(-pi / 4)
            self.force_kill = True
            return True
        return False

    def render(self, surf: "Surface", offset: Tuple[int, int] = (0, 0)):
        if not (self.range <= 20):
            pos = (self.rect.x - offset[0], self.rect.y - offset[1])
            surf.blit(Projectile._game_instance.assets["projectile"], pos)

    @classmethod
    def render_projectiles(
        cls, surf: "Surface", dt: float, offset: Tuple[int, int] = (0, 0)
    ):
        to_remove = []
        for projectile in cls._all_projectiles:
            if projectile.update(dt):
                to_remove.append(projectile)
            projectile.render(surf, offset)

        for projectile in to_remove:
            Projectile._all_projectiles.remove(projectile)
