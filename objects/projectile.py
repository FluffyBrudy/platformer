from typing import List, Set, Tuple, TYPE_CHECKING, Union, cast
from pygame import Rect, Vector2
from math import hypot
from constants import BASE_PROJECTILE_RANGE, BASE_SPEED

if TYPE_CHECKING:
    from game import Game
    from pygame import Surface
    from entities import PhysicsEntity


class Projectile:
    __slots__ = ("rect", "velocity", "range")
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
        Projectile._all_projectiles.add(self)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, value: object, /) -> bool:
        return self is value

    def add(self, group: Union[Set, List]):
        if isinstance(group, set):
            group.add(self)
        elif isinstance(group, list):
            group.append(self)
        Projectile._all_projectiles.add(self)

    def remove(self, group: Union[Set, List]):
        group.remove(self)
        Projectile._all_projectiles.remove(self)

    def movement(self, dt: float):
        movement_x = self.velocity.x * BASE_SPEED * dt
        movement_y = self.velocity.y * BASE_SPEED * dt
        self.rect.x += movement_x
        self.rect.y += movement_y
        self.range -= hypot(abs(movement_x), abs(movement_y))

    def can_die(self, *other_sprite: "PhysicsEntity"):
        base_kill_case = (self.range <= 0) or (
            Projectile._game_instance.tilemap.solid_tile_check(self.rect.center)
            is not None
        )
        if base_kill_case:
            return True
        return any(
            self.rect.colliderect(sprite.collision_rect) for sprite in other_sprite
        )

    def render(self, surf: "Surface", offset: Tuple[int, int] = (0, 0)):
        pos = (self.rect.x - offset[0], self.rect.y - offset[1])
        surf.blit(Projectile._game_instance.assets["projectile"], pos)

    @classmethod
    def render_projectiles(
        cls, surf: "Surface", dt: float, offset: Tuple[int, int] = (0, 0)
    ):
        for projectile in cls._all_projectiles:
            projectile.movement(dt)
            projectile.render(surf, offset)
