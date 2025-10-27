from typing import List
import pygame
from objects.cloud import CloudGroup
from objects.particles import Particle
from objects.entities import Player
from objects.tilemap import Tilemap
from pgdebug import Debug
from utils.animation import Animation
from utils.image_utils import load_image, load_images, load_key_images
from constants import ASSETS_PATH, BASE_PATH, Color, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from constants import TILE_SIZE


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.Clock()
        self.dt = 0

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
            "grass": load_key_images(ASSETS_PATH / "tiles" / "grass", TILE_SIZE),
            "stone": load_key_images(ASSETS_PATH / "tiles" / "stone", TILE_SIZE),
            "decor": load_key_images(ASSETS_PATH / "tiles" / "decor", 2),
            "largedecor": load_key_images(ASSETS_PATH / "tiles" / "large_decor", 2),
            "spawners": load_key_images(ASSETS_PATH / "tiles" / "spawners"),
            "particles/leaf": Animation(
                load_images(ASSETS_PATH / "particles" / "leaf", 2), 0.05, False
            ),
            "particles/particle": Animation(
                load_images(ASSETS_PATH / "particles" / "particle"), 0.1, False
            ),
            "background": load_image(
                ASSETS_PATH / "background.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
            ),
            "gun": load_image(ASSETS_PATH / "gun.png"),
            "projectile": load_image(ASSETS_PATH / "projectile.png"),
            "player/idle": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "idle",
                    scale=1.8,
                ),
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

        # camera
        self.scroll = pygame.math.Vector2(0, 0)

        # cloud groups
        self.clouds = CloudGroup(self.assets["clouds"])

        # spawns
        self.spawn_leafs_rects()

        Debug.change_font(25)

    def spawn_leafs_rects(self):
        self.leaf_spawners: List[pygame.Rect] = []

        for tree in self.tilemap.extract([("largedecor", 2)], keep=True):
            self.leaf_spawners.append(
                pygame.Rect(
                    tree.pos[0], tree.pos[1], TILE_SIZE[0] // 2, TILE_SIZE[1] // 2
                )
            )

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = True
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = False
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = False
                if event.key == pygame.K_UP:
                    self.player.jump(self.dt, energy=0)
                if event.key == pygame.K_SPACE:
                    self.player.dash()

    def update(self, dt: float):
        movement = (self.movement[1] - self.movement[0], 0)
        self.clouds.update(dt)
        self.player.update(dt, self.tilemap, movement)
        Particle.spawn_leafs(self, self.leaf_spawners)
        Particle.update_particles(dt)
        self.camera_movement()

    def camera_movement(self):
        target_scroll_x = self.player.rect.centerx - self.screen.width / 2
        target_scroll_y = self.player.rect.centery - self.screen.height / 2
        self.scroll.x = round(
            self.scroll.x + (target_scroll_x - self.scroll.x) * 0.1, 2
        )
        self.scroll.y = round(
            self.scroll.y + int((target_scroll_y - self.scroll.y) * 0.05), 2
        )

    def draw(self):
        self.clouds.render(self.screen, offset=self.scroll)
        self.tilemap.render(self.screen, offset=self.scroll)
        self.player.render(self.screen, offset=self.scroll)
        Particle.draw_particles(self.screen, self.scroll)  # type:ignore
        Debug.draw_all(self.screen)

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.screen.blit(self.assets["background"], (0, 0))
            self.handle_event()
            self.update(self.dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
