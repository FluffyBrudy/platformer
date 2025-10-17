from typing import Any
from pygame import Surface
import pygame


if not pygame.get_init():
    pygame.init()

font = pygame.font.SysFont(None, 25)

prev_x, prev_y = 0, 0


def pgdebug(surface: Surface, text: Any, shift=0):
    textsurf = font.render(f"{text}", True, (255, 255, 255))
    position_x = int((surface.width - (1 + shift) * textsurf.width) / 2)
    position_y = int((surface.height - (1 + shift) * textsurf.height) / 2)
    surface.blit(textsurf, (position_x, position_y))
