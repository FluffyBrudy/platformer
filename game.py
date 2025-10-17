import pygame
from constants import ASSETS_PATH, Color, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from objects.entities import PhysicsEntity
from objects.tilemap import Tilemap
from utils.image_utils import load_image, load_key_images

# from pprint import pprint


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.Clock()

        self.running = True
        self.movement = [False, False]

        # game assets
        TILE_SIZE = (32, 32)
        self.tilesize = TILE_SIZE
        self.assets = {
            "player": load_image(ASSETS_PATH / "entities" / "player.png", 2),
            "grass": load_key_images(ASSETS_PATH / "tiles" / "grass", TILE_SIZE),
            "stone": load_key_images(ASSETS_PATH / "tiles" / "stone", TILE_SIZE),
            "decor": load_key_images(ASSETS_PATH / "tiles" / "decor", TILE_SIZE),
            "largedecor": load_key_images(
                ASSETS_PATH / "tiles" / "large_decor", TILE_SIZE
            ),
            "spawners": load_key_images(ASSETS_PATH / "tiles" / "spawners"),
            "background": load_image(ASSETS_PATH / "background.png"),
            "gun": load_image(ASSETS_PATH / "gun.png"),
            "projectile": load_image(ASSETS_PATH / "projectile.png"),
        }

        # player
        self.player = PhysicsEntity(
            self, "player", [150, 50], self.assets["player"].size
        )

        # tilemap
        self.tilemap = Tilemap(self, TILE_SIZE[0])
        self.tilemap.render(self.screen)

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = True
                elif event.key == pygame.K_RIGHT:
                    self.movement[1] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = False
                elif event.key == pygame.K_RIGHT:
                    self.movement[1] = False
                if event.key == pygame.K_SPACE:
                    self.player.velocity.y -= 3

    def update(self, dt: float):
        movement = (self.movement[1] - self.movement[0], 0)
        self.player.update(dt, self.tilemap, movement)

    def draw(self):
        self.tilemap.render(self.screen)
        self.player.render(self.screen)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.screen.fill(Color.BG_COLOR)
            self.handle_event()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
