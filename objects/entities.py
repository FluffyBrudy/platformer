import pygame
from typing import TYPE_CHECKING, List, Tuple, Union
from constants import BASE_SPEED
from pgdebug import pgdebug, pgdebug_rect

if TYPE_CHECKING:
    from game import Game
    from tilemap import Tilemap


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

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

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

    def jump(self, energy=0.0, debug=True):
        if self.collisions["down"] or debug:
            self.velocity.y = -3 - abs(energy)

    def render(
        self,
        surface: pygame.Surface,
        offset: Union[pygame.Vector2, Tuple[float, float]],
    ):
        pgdebug(surface, f"entity.py: {self.collisions}", 1)
        pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        surface.blit(self.game.assets["player"], pos)
        pgdebug_rect(surface, (*pos, *self.size))
