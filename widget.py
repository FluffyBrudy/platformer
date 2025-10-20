import pygame
from pygame import Surface, Rect
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, Color


class ToggleSlider:
    def __init__(
        self,
        pos: tuple[int, int],
        size: tuple[int, int],
        states: list[str],
        font: pygame.font.Font,
        callback=lambda: print("toggle"),
    ) -> None:
        self.pos = pos
        self.size = size
        self.states = states
        self.index = 0
        self.hovered = False
        self.transition = 0.0
        self.target = 0.0

        self.callback = callback

        self.font = font
        self.surface = Surface(size, pygame.SRCALPHA)

        self.bg_off = pygame.Color(220, 230, 255)
        self.bg_on = pygame.Color(70, 130, 255)
        self.knob_color = pygame.Color(255, 255, 255)

    def toggle(self):
        self.index = (self.index + 1) % len(self.states)
        self.target = 1.0 if self.index else 0.0

    def is_hovered(self):
        return self.hovered

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = Rect(*self.pos, *self.size).collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.index = (self.index + 1) % len(self.states)
                self.target = 1.0 if self.index else 0.0
                self.callback()

    def update(self) -> None:
        self.transition += (self.target - self.transition) * 0.1
        self.transition = max(0.0, min(1.0, self.transition))

    def draw(self, screen: Surface) -> None:
        w, h = self.size
        r = h // 2

        bg = self.bg_off.lerp(self.bg_on, self.transition)
        opacity = 255 if self.hovered else int(180 + 75 * self.transition)

        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surface, bg, (0, 0, w, h), border_radius=r)
        self.surface.set_alpha(opacity)

        knob_x = int(r + (w - 2 * r) * self.transition)
        pygame.draw.circle(self.surface, self.knob_color, (knob_x, r), r - 3)

        label = self.font.render(self.states[self.index], True, (0, 0, 0))
        label_rect = label.get_rect(center=(w // 2, h // 2))
        self.surface.blit(label, label_rect)

        screen.blit(self.surface, self.pos)


class NotificationBar:
    def __init__(
        self, screen: Surface, font_size=28, height=50, fade_ms=1000, slide_ms=300
    ):
        self.screen = screen
        self.width = screen.get_width()
        self.height = height
        self.font = pygame.font.SysFont(None, font_size)
        self.fade_ms = fade_ms
        self.slide_ms = slide_ms

        self.message = ""
        self.active = False
        self.alpha = 0
        self.start_time = 0
        self.fade_start = 0
        self.y_offset = -self.height

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def display_start(self, message: str):
        self.message = message
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.fade_start = 0
        self.alpha = 255
        self.y_offset = -self.height

    def display_end(self, msg=""):
        self.message = msg
        self.fade_start = pygame.time.get_ticks()

    def ease_out_cubic(self, t: float):
        return 1 - pow(1 - t, 3)

    def draw(self):
        if not self.active:
            return

        now = pygame.time.get_ticks()

        elapsed = now - self.start_time
        t = min(elapsed / self.slide_ms, 1)
        self.y_offset = -self.height + self.ease_out_cubic(t) * self.height

        if self.fade_start > 0:
            fade_elapsed = now - self.fade_start
            if fade_elapsed >= self.fade_ms:
                self.active = False
                return
            self.alpha = int(255 * (1 - fade_elapsed / self.fade_ms))

        self.surface.fill((30, 30, 30, self.alpha))
        glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        glow.fill((255, 200, 50, int(self.alpha * 0.2)))
        self.surface.blit(glow, (0, 0))

        text_surf = self.font.render(self.message, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.surface.blit(text_surf, text_rect)

        self.screen.blit(self.surface, (0, int(self.y_offset)))


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
