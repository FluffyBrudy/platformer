from typing import Any
from pygame import Surface
import pygame


if not pygame.get_init():
    pygame.init()

font = pygame.font.SysFont(None, 50)


def pgdebug(surface: Surface, text: Any):
    textsurf = font.render(f"{text}", True, (255, 255, 255))
    position_x = int((surface.width - textsurf.width) / 2)
    position_y = int((surface.height - textsurf.height) / 2)
    surface.blit(textsurf, (position_x, position_y))
