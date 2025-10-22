from enum import Enum, auto
import pygame
from typing import TYPE_CHECKING, List, Literal, Tuple, Union
from constants import BASE_SPEED
from pgdebug import pgdebug, pgdebug_rect

if TYPE_CHECKING:
    from game import Game
    from tilemap import Tilemap
    from utils.animation import Animation

TActions = Literal["idle", "jump", "slide", "run", "wallslide", ""]


class PhysicsEntity:
    def __init__(
        self, game: "Game", etype: str, pos: Tuple[int, int], size: Tuple[int, int]
    ) -> None:
        self.game = game
        self.type = etype
        self.pos = list(pos)
        self.size = size
        self.velocity = pygame.Vector2(0, 0)
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        self.action: TActions = ""
        self.flipped = False
        self.set_action("idle")

        self.hitbox_offset = (10, 0)
        self.hitbox_size = (self.size[0] - 2 * self.hitbox_offset[0], self.size[1])

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    @property
    def collision_rect(self):
        return pygame.Rect(
            self.pos[0] + self.hitbox_offset[0],
            self.pos[1] + self.hitbox_offset[1],
            self.hitbox_size[0],
            self.hitbox_size[1],
        )

    def set_action(self, action: TActions):
        if self.action != action:
            self.action = action
            self.animation: "Animation" = self.game.assets[f"player/{action}"].copy()
            self.size = self.animation.get_frame().size

    def handle_flipping(self, movement: Tuple[int, int]):
        if movement[0] < 0:
            self.flipped = True
        elif movement[0] > 0:
            self.flipped = False

    def update(self, dt: float, tilemap: "Tilemap", movement: Tuple[int, int] = (0, 0)):
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        frame_movement_x = (movement[0] + (self.velocity.x)) * (dt * BASE_SPEED)
        frame_movement_y = (movement[1] + (self.velocity.y)) * (dt * BASE_SPEED)

        self.pos[0] += frame_movement_x  # type:ignore
        entity_rect = self.collision_rect
        delta = 0
        for rect in tilemap.physics_rects_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if movement[0] > 0:
                    delta = rect.left - entity_rect.right - 1
                    self.collisions["right"] = True
                    self.pos[0] += delta  # type: ignore
                    break
                elif movement[0] < 0:
                    delta = rect.right - entity_rect.left
                    self.collisions["left"] = True
                    self.pos[0] += delta  # type: ignore
                    break

        self.pos[1] += frame_movement_y  # type: ignore

        entity_rect = self.collision_rect
        for rect in tilemap.physics_rects_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if frame_movement_y < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                if frame_movement_y > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                self.pos[1] = entity_rect.y

        self.velocity.y = min(10, (self.velocity.y + 0.1))
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity.y = 0

        self.handle_flipping(movement)

        probe_rect = self.collision_rect.move(0, 1)
        tiles_around = tilemap.physics_rects_around(self.pos)  # type: ignore

        for rect in tiles_around:
            if probe_rect.colliderect(rect):
                self.collisions["down"] = True
                break

        flip_dir = -1 if self.flipped else 1

        collision_side = "left" if self.flipped else "right"
        probe_rect = self.collision_rect.move(flip_dir, 0)
        for rect in tiles_around:
            if probe_rect.colliderect(rect):
                self.collisions[collision_side] = True

        if not self.collisions["down"] and movement[0] != 0:
            self.set_action("jump")  # TODO: jump state when falling
        if not self.collisions["down"] and (
            self.collisions["left"] or self.collisions["right"]
        ):
            self.set_action("wallslide")
            self.velocity.y = min(self.velocity.y, 1.1)
        elif not self.collisions["down"]:
            self.set_action("jump")

        self.animation.update()

    def render(
        self,
        surface: pygame.Surface,
        offset: Union[pygame.Vector2, Tuple[float, float]],
    ):
        pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        img = self.animation.get_frame()
        if self.flipped:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, pos)


class Player(PhysicsEntity):
    def __init__(
        self, game: "Game", etype: str, pos: Tuple[int, int], size: Tuple[int, int]
    ) -> None:
        super().__init__(game, etype, pos, size)
        self.air_time = 0

    def update(self, dt: float, tilemap: "Tilemap", movement: Tuple[int, int] = (0, 0)):
        super().update(dt, tilemap, movement)

        if self.collisions["down"]:
            if movement[0] != 0:
                self.set_action("run")
            else:
                self.set_action("idle")

    def jump(self, energy=0.0, debug=1):
        if self.collisions["down"] or debug:
            self.set_action("jump")
            self.velocity.y = -3 - abs(energy)
