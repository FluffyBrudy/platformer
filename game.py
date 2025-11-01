import math
from random import choice, random
from typing import List
import pygame
from objects.cloud import CloudGroup
from objects.particles import Particle
from objects.entities import Enemy, Player
from objects.projectile import Projectile
from objects.sparks import Spark
from objects.tilemap import Tilemap
from pgdebug import Debug
from utils.animation import Animation
from utils.image_utils import load_image, load_images, load_key_images
from constants import (
    ASSETS_PATH,
    SCREEN_CENTER,
    SCREEN_SHAKE,
    Color,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from constants import TILE_SIZE
from utils.math_utils import sign


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.Clock()
        self.dt = 0

        self.running = True
        self.movement = [False, False]

        # screenshake effect
        self.screenshake = 0

        # loading transition
        self.transition_radius = 0
        self.transition_speed = 15

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
            "particles/leaf": Animation(
                load_images(ASSETS_PATH / "particles" / "leaf", 2.5), 0.05, False
            ),
            "particles/particle": Animation(
                load_images(ASSETS_PATH / "particles" / "particle", 1), 0.05, False
            ),
            "background": load_image(
                ASSETS_PATH / "background.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
            ),
            "gun": load_image(ASSETS_PATH / "gun.png", (20, 10)),
            "projectile": load_image(ASSETS_PATH / "projectile.png", 1.5),
            # player
            "player/idle": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "idle",
                    scale=1.5,
                ),
            ),
            "player/run": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "run",
                    scale=1.5,
                )
            ),
            "player/jump": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "jump",
                    scale=1.5,
                )
            ),
            "player/slide": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "slide",
                    scale=1.5,
                )
            ),
            "player/wallslide": Animation(
                load_images(
                    ASSETS_PATH / "entities" / "player" / "wall_slide",
                    scale=1.5,
                )
            ),
            # enemy
            "enemy/idle": Animation(
                load_images(ASSETS_PATH / "entities" / "enemy" / "idle", scale=1.5),
            ),
            "enemy/run": Animation(
                load_images(ASSETS_PATH / "entities" / "enemy" / "run", scale=1.5),
            ),
        }

        # tilemap
        self.level = 0
        self.tilemap = Tilemap(self, TILE_SIZE[0])

        self.load_level(0)
        Debug.change_font(25)

    def load_level(self, level: int):
        # reset level data
        self.tilemap.load_level(level)

        # safe resets
        self.screenshake = 0
        self.transition_radius = 0

        self.dead = 0
        self.scroll = pygame.math.Vector2(0, 0)
        self.movement = [False, False]
        self.dt = 0

        self.enemies = []
        self.projectiles = []
        self.clouds = CloudGroup(self.assets["clouds"])

        self.player = Player(self, (150, 50), self.assets["player"].size)

        self.spawn_leafs_rects()
        self.spawn_enemies()

    def spawn_enemies(self):
        for enemy in self.tilemap.extract([("enemy", 1)], False):
            enemy = Enemy(self, enemy.pos, self.assets["player"].size)
            self.enemies.append(enemy)

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

    def tilex_range_check(self, a: float, b: float, common_y: float):
        tile_size = self.tilemap.tile_size[0]
        start_x = int(min(a, b) // tile_size) * tile_size
        tile_count = math.ceil(abs(a - b) / tile_size)

        for i in range(tile_count + 1):
            x = start_x + i * tile_size
            if self.tilemap.solid_tile_check((x, common_y)):
                return False
        return True

    def update_enemy(self):
        player_pos = self.player.pos
        dashing = self.player.dashing
        for enemy in self.enemies.copy():
            enemy.update(self.dt, self.tilemap, (0, 0))
            dist = player_pos[0] - enemy.pos[0]

            if (
                abs(dist) <= 200
                and abs(enemy.pos[1] - self.player.pos[1]) <= TILE_SIZE[1] // 2
                and self.tilex_range_check(
                    self.player.rect.right, enemy.pos[0], enemy.pos[1]
                )
            ):
                enemy.walking = 0
                enemy.flipped = dist < 0
                if enemy.can_shoot() and not dashing:
                    proj_dir = (sign(dist) * 2, 0)
                    enemy.shoot_projectile(proj_dir)  # type:ignore
            if dashing and enemy.collision_rect.colliderect(self.player.rect):
                self.screenshake = SCREEN_SHAKE
                self.enemies.remove(enemy)
                Spark(self.player.rect.center, 0, 10, (2, 0.5))
                Spark(self.player.rect.center, math.pi, 10, (2, 0.5))
                for _ in range(200):
                    angle = random() * 2 * math.pi
                    speed = 2 * random()
                    Particle.add_particles(
                        Particle(
                            self,
                            "dash",
                            self.player.rect.center,
                            (
                                math.cos(angle + math.pi) * speed * 0.5,
                                math.sin(angle + math.pi) * speed * 0.5,
                            ),
                        )
                    )

    def handle_project_player_collision(self):
        for projectile in Projectile.get_projectiles():
            if projectile.entity_collision(self.player) and not self.player.dashing:
                self.screenshake = SCREEN_SHAKE * 0.4
                self.dead += 1
        if self.dead:
            self.dead += 1
            if self.dead >= 40:
                self.load_level(self.level)

    def camera_movement(self):
        target_scroll_x = self.player.rect.centerx - self.screen.width / 2
        target_scroll_y = self.player.rect.centery - self.screen.height / 2
        self.scroll.x = round(
            self.scroll.x + (target_scroll_x - self.scroll.x) * 0.1, 2
        )
        self.scroll.y = round(
            self.scroll.y + int((target_scroll_y - self.scroll.y) * 0.05), 2
        )

    def render(self):
        dt = self.dt

        movement = (self.movement[1] - self.movement[0], 0)

        if len(self.enemies) == 0:
            self.level += 1
            self.load_level(self.level)
        self.clouds.update(dt)
        self.player.update(dt, self.tilemap, movement)
        Particle.spawn_leafs(self, self.leaf_spawners)
        self.handle_project_player_collision()
        Particle.update_particles(dt)
        self.update_enemy()
        self.camera_movement()

        sx = choice([1, -1])
        shake = random() * self.screenshake - self.screenshake / 2
        scroll = self.scroll + (shake * sx, shake * sx)

        self.clouds.render(self.screen, offset=scroll)  # type:ignore
        self.tilemap.render(self.screen, offset=scroll)  # type: ignore
        self.player.render(self.screen, offset=scroll)  # type: ignore
        [enemy.render(self.screen, scroll) for enemy in self.enemies]  # type: ignore
        Projectile.render_projectiles(self.screen, dt, scroll)  # type: ignore
        Spark.render_sparks(self.screen, dt, scroll)  # type: ignore
        Particle.draw_particles(self.screen, scroll)  # type:ignore
        Debug.draw_all(self.screen)

    def run(self):
        while self.running:
            shake = 0
            self.dt = self.clock.tick(FPS) / 1000.0
            if self.screenshake != 0:
                shake = random() * self.screenshake - self.screenshake / 2
                self.screenshake = max(0, self.screenshake - 1)
            self.screen.blit(self.assets["background"], (shake, shake))
            self.handle_event()
            self.render()
            self.circular_transition()
            pygame.display.flip()
        pygame.quit()

    def circular_transition(self):
        if self.transition_radius <= SCREEN_HEIGHT:
            mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 255))
            pygame.draw.circle(
                mask, (0, 0, 0, 0), SCREEN_CENTER, self.transition_radius
            )
            self.screen.blit(mask, (0, 0))
            self.transition_radius += (
                max(SCREEN_WIDTH, SCREEN_HEIGHT) - self.transition_radius
            ) * 0.05


if __name__ == "__main__":
    game = Game()
    game.run()
