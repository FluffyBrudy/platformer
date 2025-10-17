import pygame
from typing import TYPE_CHECKING, List, Tuple
from constants import BASE_SPEED

if TYPE_CHECKING:
    from game import Game
    from tilemap import Tilemap


class PhysicsEntites:
    def __init__(
        self, game: "Game", etype: str, pos: List[int], size: Tuple[int, int]
    ) -> None:
        self.game = game
        self.type = etype
        self.pos = list(pos)
        self.size = size
        self.velocity = pygame.Vector2(0, 0)

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def update(self, dt: float, tilemap: "Tilemap", movement: Tuple[int, int] = (0, 0)):
        frame_movement_x = (movement[0] + (self.velocity.x)) * (dt * BASE_SPEED)
        frame_movement_y = (movement[1] + (self.velocity.y)) * (dt * BASE_SPEED)

        self.pos[0] += frame_movement_x
        entity_rect = self.rect
        for rect in tilemap.physics_rect_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if frame_movement_x > 0:
                    entity_rect.right = rect.left
                if frame_movement_x < 0:
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement_y
        entity_rect = self.rect
        for rect in tilemap.physics_rect_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if frame_movement_y < 0:
                    entity_rect.top = rect.bottom
                if frame_movement_y > 0:
                    entity_rect.bottom = rect.top
                self.pos[1] = entity_rect.y

        self.velocity.y = min(
            5 * BASE_SPEED * dt, BASE_SPEED * dt * (self.velocity.y + 0.1)
        )

    def render(self, surface: pygame.Surface):
        surface.blit(self.game.assets["player"], self.pos)
