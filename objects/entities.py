from math import cos, pi, sin
from random import choice, randint, random
import pygame
from typing import TYPE_CHECKING, List, Literal, Tuple, Union

from constants import (
    BASE_DECAY_FACTOR,
    BASE_SPEED,
    DASH_DECAY_THRESHOLD,
    DASH_POWER,
    DASH_SPEED_MULT,
    JUMP_BASE,
)
from objects.particles import Particle
from objects.projectile import Projectile
from pgdebug import pgdebug
from utils.math_utils import sign
from utils.timer import Timer

if TYPE_CHECKING:
    from game import Game
    from tilemap import Tilemap
    from utils.animation import Animation

TActions = Literal["idle", "jump", "slide", "run", "wallslide", ""]


class PhysicsEntity:
    def __init__(
        self,
        game: "Game",
        etype: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        hitbox_offset: Tuple[int, int] = (0, 0),
    ) -> None:
        self.game = game
        self.type = etype
        self.pos = list(pos)
        self.size = size
        self.velocity = pygame.Vector2(0, 0)
        self.collisions = {"up": False, "down": False, "left": False, "right": False}
        self.probe_offsets = {"down": (0, 1), "left": (-1, 0), "right": (1, 0)}

        self.action: TActions = ""
        self.flipped = False
        self.set_action("idle")

        self.hitbox_offset = hitbox_offset
        self.hitbox_size = (self.size[0] - 2 * self.hitbox_offset[0], self.size[1])

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    @property
    def collision_rect(self):
        return pygame.Rect(
            self.pos[0] + self.hitbox_offset[0],
            self.pos[1] + self.hitbox_offset[1],
            self.hitbox_size[0],
            self.hitbox_size[1],
        )

    def set_action(self, action: TActions):
        if self.action != action:
            self.action = action
            self.animation: "Animation" = self.game.assets[
                f"{self.type}/{action}"
            ].copy()
            self.size = self.animation.get_frame().size

    def handle_flipping(self, movement: Tuple[float, float]):
        if movement[0] < 0:
            self.flipped = True
        elif movement[0] > 0:
            self.flipped = False

    def probe(self, tiles_around: List[pygame.Rect]):
        for side, offset in self.probe_offsets.items():
            probe_rect = self.collision_rect.move(offset)
            for rect in tiles_around:
                if probe_rect.colliderect(rect):
                    self.collisions[side] = True
                    break

    def update(
        self, dt: float, tilemap: "Tilemap", movement: Tuple[float, float] = (0, 0)
    ):
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        frame_movement_x = round(
            (movement[0] + (self.velocity.x)) * (dt * BASE_SPEED * 1.5), 2
        )
        frame_movement_y = round(
            (movement[1] + (self.velocity.y)) * (dt * BASE_SPEED), 2
        )

        self.pos[0] += frame_movement_x  # type:ignore
        entity_rect = self.collision_rect
        delta = 0
        for rect in tilemap.physics_rects_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if frame_movement_x > 0:
                    delta = rect.left - entity_rect.right
                    self.collisions["right"] = True
                    self.pos[0] += delta  # type: ignore
                    break
                elif frame_movement_x < 0:
                    delta = rect.right - entity_rect.left
                    self.collisions["left"] = True
                    self.pos[0] += delta  # type: ignore
                    break

        self.pos[1] += frame_movement_y  # type: ignore

        entity_rect = self.collision_rect
        for rect in tilemap.physics_rects_around(self.pos):  # type: ignore
            if entity_rect.colliderect(rect):
                if frame_movement_y < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                if frame_movement_y > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                self.pos[1] = entity_rect.y

        self.velocity.y = min(10, (self.velocity.y + 0.1))
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity.y = 0

        self.handle_flipping(movement)

        tiles_around = tilemap.physics_rects_around(self.pos)  # type: ignore
        self.probe(tiles_around)

        self.animation.update()

    def render(
        self,
        surface: pygame.Surface,
        offset: Union[pygame.Vector2, Tuple[float, float]],
    ):
        pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        img = self.animation.get_frame()
        if self.flipped:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, pos)


class Enemy(PhysicsEntity):
    def __init__(
        self, game: "Game", pos: Tuple[int, int], size: Tuple[int, int]
    ) -> None:
        super().__init__(game, "enemy", pos, size)
        self.walking = 0
        self.flipped = choice((True, False))
        self.projectile_timer = Timer(200)

    def update(
        self, dt: float, tilemap: "Tilemap", movement: Tuple[float, float] = (0, 0)
    ):
        if self.collisions["down"]:
            movement = self.movement(tilemap, movement)
        super().update(dt, tilemap, movement=movement)

    def can_shoot(self):
        shootable = self.projectile_timer.has_reach_interval()
        if shootable:
            self.projectile_timer.reset_to_now()
        return shootable

    def shoot_projectile(self, velocity: Tuple[int, int]):
        gun_pos = (self.rect.centerx, self.rect.centery)
        gun_surf = self.game.assets["gun"]
        if self.flipped:
            gun_surf = pygame.transform.flip(gun_surf, True, False)
            gun_pos = (gun_pos[0] - gun_surf.width, gun_pos[1])

        projectile = Projectile(self.game, gun_pos, velocity)
        projectile.add_sparks(scaler_change=(2, 0.5), count=4)

    def movement(self, tilemap: "Tilemap", movement: Tuple[float, float]):
        w = self.animation.get_frame().width
        flip_dir = -1 if self.flipped else 1
        front_x = self.rect.centerx + flip_dir * w // 2
        feet_y = self.rect.bottom
        front_ground = (front_x, feet_y)

        if self.collisions["left"] or self.collisions["right"]:
            self.flipped = not self.flipped
        elif not tilemap.solid_tile_check(front_ground):
            self.flipped = not self.flipped

        movement_x_dir = -1 if self.flipped else 1

        if self.walking:
            movement = (movement[0] + movement_x_dir * 0.5, movement[1])
            self.set_action("run")
        elif random() < 0.01:
            self.walking = randint(int(BASE_SPEED * 0.3), BASE_SPEED)
        else:
            self.set_action("idle")

        self.walking = max(0, self.walking - 1)
        return movement

    def render(
        self,
        surface: pygame.Surface,
        offset: Union[pygame.Vector2, Tuple[float, float]],
    ):
        if self.action != "run":
            gun_pos = (self.rect.centerx - offset[0], self.rect.centery - offset[1])
            gun_surf = self.game.assets["gun"]
            if self.flipped:
                gun_surf = pygame.transform.flip(gun_surf, True, False)
                gun_pos = (gun_pos[0] - gun_surf.width, gun_pos[1])
            surface.blit(gun_surf, gun_pos)
        super().render(surface, offset)


class Player(PhysicsEntity):
    def __init__(
        self, game: "Game", pos: Tuple[int, int], size: Tuple[int, int]
    ) -> None:
        super().__init__(game, "player", pos, size, (7, 0))
        self.wallslide = False
        self.prev_movement = 1
        self.dashing = 0

    def update(
        self, dt: float, tilemap: "Tilemap", movement: Tuple[float, float] = (0, 0)
    ):
        super().update(dt, tilemap, movement)
        mx = movement[0]
        pgdebug(f"frame={self.prev_movement}")

        if (
            not self.collisions["down"]
            and (self.collisions["left"] and self.flipped)
            or (self.collisions["right"] and not self.flipped)
        ):
            self.set_action("wallslide")
            self.wallslide = True
            self.dashing = 0
            self.velocity.x = 0

        if self.wallslide:
            self.velocity.y = min(self.velocity.y, 1.1)
            if (self.prev_movement, mx) in ((-1, 1), (1, -1)):
                self._wall_jump(dt)

        if mx and self.prev_movement != mx:
            self.prev_movement = mx

        self._handle_motion_state()
        self._handle_velocity_resistance()
        self._handle_dash_friction()
        self._handle_dash(dt)

        # just for correction
        if self.collisions["down"]:
            self.wallslide = False
            if not self.dash:
                self.velocity.x = 0
            self.velocity.y = 0
            self.set_action("run" if mx else "idle")

    def _handle_motion_state(self):
        if self.collisions["down"]:
            self.velocity.x = 0
            self.velocity.y = 0
        elif not (self.collisions["left"] or self.collisions["right"]):
            self.set_action("jump")
            self.wallslide = False

    def _handle_velocity_resistance(self):
        if self.velocity.x < 0:
            self.velocity.x = min(self.velocity.x + BASE_DECAY_FACTOR, 0)
        elif self.velocity.x > 0:
            self.velocity.x = max(self.velocity.x - BASE_DECAY_FACTOR, 0)

    def _handle_dash(self, dt: float):
        abs_dash = abs(self.dashing)
        if not abs(self.dashing):
            return
        particle = Particle(
            self.game,
            "dash",
            self.collision_rect.midbottom,
            (self.velocity.x / 8, self.velocity.y / 2),
        )
        particle.animation.change_frame(randint(0, 7))
        Particle.add_particles(particle)
        if abs_dash > DASH_DECAY_THRESHOLD:
            self.velocity[0] = sign(self.dashing) * 5
            if abs_dash == DASH_DECAY_THRESHOLD + 1:
                self.velocity.x *= BASE_DECAY_FACTOR
        if (abs_dash - DASH_DECAY_THRESHOLD) <= -2:
            angle = random() * 2 * pi
            speed = random() * 0.5 + 0.5
            particle_vel = (cos(angle) * speed, sin(angle) * speed)
            particle = Particle(
                self.game, "dash", self.collision_rect.midbottom, particle_vel
            )
            particle.animation.change_frame(randint(0, 7))
            Particle.add_particles(particle)
        pgdebug(f"self.velocity.x={self.velocity.x}")

    def _handle_dash_friction(self):
        if self.dashing > 0:
            self.dashing = max(self.dashing - 1, 0)
        elif self.dashing < 0:
            self.dashing = min(self.dashing + 1, 0)
        if self.collisions["left"] or self.collisions["right"]:
            self.dashing = 0

    def _wall_jump(self, dt: float, speed_scale: float = 1.0):
        self.velocity.x = -self.prev_movement * BASE_SPEED * dt * speed_scale
        self.wallslide = False
        self.velocity.y = -3

    def jump(
        self, dt: float, energy=0.0, force_jump=True
    ):  # TODO: remove force jump or set to false
        if self.collisions["down"] or force_jump:
            self.set_action("jump")
            self.velocity.y = JUMP_BASE - abs(energy)  # type: ignore
        if self.wallslide:
            self._wall_jump(dt, 2.0)

    def dash(self):
        if self.dashing > 1 or (self.collisions["left"] or self.collisions["right"]):
            return
        dash_dir = -1 if self.flipped else 1
        self.dashing = dash_dir * DASH_POWER

    def render(
        self,
        surface: pygame.Surface,
        offset: Union[pygame.Vector2, Tuple[float, float]],
    ):
        if abs(self.dashing) <= DASH_DECAY_THRESHOLD:
            super().render(surface, offset)
