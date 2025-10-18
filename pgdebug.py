from typing import Any
import pygame
from pygame.typing import RectLike
from constants import Color

if not pygame.get_init():
    pygame.init()

font = pygame.font.SysFont(None, 25)

# global debug reference storage
_DEBUG_REFS = []


class Debug:
    """Global debug manager handling registered elements."""

    @staticmethod
    def add(rect: pygame.Rect, draw_fn, priority: int):
        _DEBUG_REFS.append({"rect": rect, "draw": draw_fn, "priority": priority})

    @staticmethod
    def clear():
        _DEBUG_REFS.clear()

    @staticmethod
    def draw_all(surface: pygame.Surface):
        """Draws all registered debug visuals with collision and priority logic."""
        if not _DEBUG_REFS:
            return

        # High priority first
        _DEBUG_REFS.sort(key=lambda d: d["priority"], reverse=True)
        drawn_rects = []

        for d in _DEBUG_REFS:
            rect = d["rect"]
            # Skip if it collides with already drawn higher-priority elements
            if not any(rect.colliderect(r) for r in drawn_rects):
                d["draw"](surface)
                drawn_rects.append(rect)

        # one-frame lifetime
        _DEBUG_REFS.clear()


def pgdebug(surface: pygame.Surface, text: Any, shift=0, priority=0):
    """Draw centered debug text (priority + collision aware)."""
    textsurf = font.render(f"{text}", True, (255, 255, 255))
    w, h = surface.get_width(), surface.get_height()

    x = int((w - (1 + shift) * textsurf.get_width()) / 2)
    y = int((h - (1 + shift) * textsurf.get_height()) / 2)
    rect = pygame.Rect(x, y, textsurf.get_width(), textsurf.get_height())

    def draw_fn(surf: pygame.Surface):
        surf.blit(textsurf, rect.topleft)

    Debug.add(rect, draw_fn, priority)


def pgdebug_rect(surface: pygame.Surface, rect_like: RectLike, w=1, priority=0):
    """
    Draw or register debug rectangles.
    - If w == 0 → filled rect, uses priority + collision system.
    - If 0 < w < 10 → always drawn immediately (ignores collisions & priority).
    """
    rect = pygame.Rect(rect_like)

    if 0 < w < 10:
        # Draw immediately, no registration
        pygame.draw.rect(surface, Color.RED, rect, w)
        return

    if w == 0:
        # Register filled rectangle for managed draw
        def draw_fn(surf: pygame.Surface):
            pygame.draw.rect(surf, Color.RED, rect, w)

        Debug.add(rect, draw_fn, priority)
