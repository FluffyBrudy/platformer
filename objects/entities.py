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

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def set_action(self, action: TActions):
        if self.action != action:
            self.action = action
            self.animation: "Animation" = self.game.assets[f"player/{action}"]
            self.size = self.animation.get_frame().size

    def update(self, dt: float, tilemap: "Tilemap", movement: Tuple[int, int] = (0, 0)):
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        frame_movement_x = (movement[0] + (self.velocity.x)) * (dt * BASE_SPEED)
        frame_movement_y = (movement[1] + (self.velocity.y)) * (dt * BASE_SPEED)

        self.pos[0] += frame_movement_x  # type:ignore
        entity_rect = self.rect

        for rect in tilemap.physics_rects_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if frame_movement_x > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement_x < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement_y  # type: ignore
        entity_rect = self.rect
        for rect in tilemap.physics_rects_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if frame_movement_y < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                if frame_movement_y > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                self.pos[1] = entity_rect.y
        self.velocity.y = min(5, (self.velocity.y + 0.1))
        if self.collisions["down"]:
            self.velocity.y = 0

        probe_rect = self.rect.move(0, 1)

        for rect in tilemap.physics_rects_around(self.pos):  # type: ignore
            if probe_rect.colliderect(rect):
                self.collisions["down"] = True
                break

        if movement[0] < 0:
            self.flipped = True
        elif movement[0] > 0:
            self.flipped = False

        self.animation.update()

    def render(
        self,
        surface: pygame.Surface,
        offset: Union[pygame.Vector2, Tuple[float, float]],
    ):
        pgdebug(surface, f"entity.py: {self.collisions}", 1)
        pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        img = self.animation.get_frame()
        if self.flipped:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, pos)
        pgdebug_rect(surface, (*pos, *self.size))


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

    def jump(self, energy=0.0, debug=True):
        if self.collisions["down"] or debug:
            self.set_action("jump")
            self.velocity.y = -3 - abs(energy)
