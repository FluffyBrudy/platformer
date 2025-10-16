import pygame
from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from pgdebug import pgdebug


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.Clock()

        self.sprite = Sprite(50, 50)

        self.running = True

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float):
        self.sprite.update(dt)

    def draw(self):
        self.sprite.draw(self.screen)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.screen.fill((0, 0, 0))
            self.handle_event()
            self.update(dt)
            self.draw()
            pgdebug(self.screen, f"dt={dt} speed={dt*500}")
            pygame.display.flip()
        pygame.quit()


class Sprite:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, 50, 50)

    def update(self, dt: float):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= int(dt * 500)
        elif keys[pygame.K_RIGHT]:
            self.rect.x += int(dt * 500)
        if keys[pygame.K_UP]:
            self.rect.y -= int(dt * 500)
        elif keys[pygame.K_DOWN]:
            self.rect.y += int(dt * 500)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, "red", self.rect)


if __name__ == "__main__":
    game = Game()
    game.run()
