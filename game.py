import pygame
from constants import ASSETS_PATH, BASE_PATH, Color, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from objects.cloud import CloudGroup
from objects.entities import Player
from objects.tilemap import Tilemap
from pgdebug import Debug, pgdebug
from utils.animation import Animation
from utils.image_utils import load_image, load_images, load_key_images
from constants import TILE_SIZE

# from pprint import pprint


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.Clock()

        self.running = True
        self.movement = [False, False]

        # game assets
        self.assets = {
            "player": load_image(
                ASSETS_PATH / "entities" / "player.png",
                2,
                Color.BLACK,
            ),
            "clouds": load_images(ASSETS_PATH / "clouds"),
            "grass": load_key_images(ASSETS_PATH / "tiles" / "grass", 2),
            "stone": load_key_images(ASSETS_PATH / "tiles" / "stone", 2),
            "decor": load_key_images(ASSETS_PATH / "tiles" / "decor", 2),
            "largedecor": load_key_images(ASSETS_PATH / "tiles" / "large_decor", 2),
            "spawners": load_key_images(ASSETS_PATH / "tiles" / "spawners"),
            "background": load_image(
                ASSETS_PATH / "background.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
            ),
            "gun": load_image(ASSETS_PATH / "gun.png"),
            "projectile": load_image(ASSETS_PATH / "projectile.png"),
            "player/idle": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "idle",
                    scale=1.8,
                )
            ),
            "player/run": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "run",
                    scale=1.8,
                )
            ),
            "player/jump": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "jump",
                    scale=1.8,
                )
            ),
            "player/slide": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "slide",
                    scale=1.8,
                )
            ),
            "player/wallslide": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "wall_slide",
                    scale=1.8,
                )
            ),
        }

        # player
        self.player = Player(self, "player", (150, 50), self.assets["player"].size)

        # tilemap
        self.tilemap = Tilemap(self, TILE_SIZE[0])
        self.tilemap.load_tilemap_data(BASE_PATH / "mapdata.json")
        print(self.tilemap.tilemap)
        # camera
        self.scroll = pygame.math.Vector2(0, 0)

        # cloud groups
        self.clouds = CloudGroup(self.assets["clouds"])

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = True
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = False
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = False
                if event.key == pygame.K_UP:
                    self.player.jump(energy=0.5)

    def update(self, dt: float):
        movement = (self.movement[1] - self.movement[0], 0)
        self.player.update(dt, self.tilemap, movement)
        self.clouds.update(dt)
        self.camera_movement()

    def camera_movement(self):
        target_scroll_x = self.player.rect.centerx - self.screen.width / 2
        target_scroll_y = self.player.rect.centery - self.screen.height / 2
        self.scroll.x = round(
            self.scroll.x + (target_scroll_x - self.scroll.x) * 0.1, 2
        )
        self.scroll.y = round(
            self.scroll.y + (target_scroll_y - self.scroll.y) * 0.5, 2
        )

    def draw(self):
        self.clouds.render(self.screen, offset=self.scroll)
        self.tilemap.render(self.screen, offset=self.scroll)
        self.player.render(self.screen, offset=self.scroll)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.screen.blit(self.assets["background"], (0, 0))
            self.handle_event()
            self.update(dt)
            self.draw()
            # Debug.draw_all(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
