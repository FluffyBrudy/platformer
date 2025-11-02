import pygame
from pygame import Surface
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, Color


import pygame
from pygame import Surface

import pygame
from pygame import Surface


class Notification:
    def __init__(
        self, message, alive=False, font=None, fade_ms=1000, slide_ms=300, hold_ms=1500
    ):
        self.message = message
        self.alive = alive
        self.font = font or pygame.font.SysFont(None, 28)
        self.fade_ms = fade_ms
        self.slide_ms = slide_ms
        self.hold_ms = hold_ms
        self.alpha = 255
        self.y_offset = -60
        self.phase = "slide"
        self.start_time = pygame.time.get_ticks()
        self.surface = None
        self.render_surface()

    def render_surface(self):
        text_surf = self.font.render(self.message, True, (255, 255, 255))
        text_rect = text_surf.get_rect()
        width, height = text_rect.width + 40, text_rect.height + 20

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        bar_color = (30, 30, 30, self.alpha)
        glow_color = (255, 200, 50, int(self.alpha * 0.2))
        pygame.draw.rect(surf, bar_color, (0, 0, width, height), border_radius=8)
        glow = pygame.Surface((width, height), pygame.SRCALPHA)
        glow.fill(glow_color)
        surf.blit(glow, (0, 0))
        text_rect.center = (width // 2, height // 2)
        surf.blit(text_surf, text_rect)
        self.surface = surf

    def ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time

        if self.phase == "slide":
            t = min(elapsed / self.slide_ms, 1)
            self.y_offset = -60 + self.ease_out_cubic(t) * 60
            if t >= 1:
                self.phase = "hold"
                self.start_time = now

        elif self.phase == "hold":
            self.y_offset = 0
            if not self.alive and elapsed >= self.hold_ms:
                self.phase = "fade"
                self.start_time = now

        elif self.phase == "fade":
            fade_elapsed = min(elapsed / self.fade_ms, 1)
            self.alpha = int(255 * (1 - fade_elapsed))
            if fade_elapsed >= 1:
                return False

        self.render_surface()
        return True

    def draw(self, screen, pos):
        if not self.surface:
            return
        surf = self.surface.copy()
        surf.set_alpha(self.alpha)
        screen.blit(surf, (pos[0], pos[1] + int(self.y_offset)))


class NotificationBar:
    def __init__(self, screen: Surface):
        self.screen = screen
        self.notifications = []
        self.max_notifications = 4

    def notify(self, message: str, alive=False):
        note = Notification(message, alive=alive)
        self.notifications.append(note)

        non_alive = [n for n in self.notifications if not n.alive]
        alive_notes = [n for n in self.notifications if n.alive]

        if len(non_alive) > self.max_notifications:
            non_alive = non_alive[-self.max_notifications :]

        self.notifications = alive_notes + non_alive

    def remove(self, message: str):
        self.notifications = [
            n for n in self.notifications if not (n.message == message and n.alive)
        ]

    def draw(self):
        alive_notes = []
        y = 10
        for n in self.notifications:
            still_alive = n.update()
            n.draw(self.screen, (10, y))
            y += n.surface.get_height() + 10
            if still_alive or n.alive:
                alive_notes.append(n)
        self.notifications = alive_notes


class KeyboardHelp:
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.visible = False

        self.width = SCREEN_WIDTH * 0.5
        self.height = SCREEN_HEIGHT * 0.6
        self.padding = 20
        self.corner_radius = 12

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.help_text = [
            "Keyboard Shortcuts",
            "-" * 25,
            "Arrow Keys: Move camera",
            "Left Click: Place tile",
            "Right Click: Remove tile",
            "Mouse Wheel: Change tile group",
            "Shift + Wheel: Change tile variant",
            "G: Toggle on-grid/off-grid mode",
            "R: Rotate tile",
            "CTRL + S: Save map",
            "H: Toggle this help",
        ]

    def toggle(self):
        self.visible = not self.visible

    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.surface,
            (40, 40, 40, 230),
            (0, 0, self.width, self.height),
            border_radius=self.corner_radius,
        )

        shadow = pygame.Surface((self.width + 6, self.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow,
            (0, 0, 0, 100),
            (3, 3, self.width, self.height),
            border_radius=self.corner_radius,
        )
        screen.blit(
            shadow,
            ((SCREEN_WIDTH - self.width) // 2, (SCREEN_HEIGHT - self.height) // 2),
        )

        y = self.padding
        title_rendered = self.font.render(self.help_text[0], True, Color.WHITE)
        self.surface.blit(title_rendered, (self.padding, y))
        y += title_rendered.get_height() + 10

        for line in self.help_text[1:]:
            rendered_text = self.font.render(line, True, Color.LIGHT_GRAY)
            self.surface.blit(rendered_text, (self.padding, y))
            y += rendered_text.get_height() + 5

        screen.blit(
            self.surface,
            ((SCREEN_WIDTH - self.width) // 2, (SCREEN_HEIGHT - self.height) // 2),
        )
