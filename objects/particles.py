from random import choice, random
from typing import TYPE_CHECKING, List, Literal, Sequence, Tuple
from pygame import Rect, Surface, Vector2
from constants import BASE_SPEED, TILE_SIZE
from utils.math_utils import natural_x

if TYPE_CHECKING:
    from game import Game
    from utils.animation import Animation

particle_map = {"leaf": "leaf", "dash": "particle"}


class Particle:
    leaf_group = []
    other_particle_group: List["Particle"] = []
    game_instance: "Game" = None  # type: ignore

    def __init__(
        self,
        game: "Game",
        ptype: Literal["dash", "leaf"],
        pos: Tuple[int, int],
        velocity: Tuple[float, float] | Vector2 = (0, 0),
    ):
        offset_dir = choice((0, 0.5, 1))
        if not Particle.game_instance:
            Particle.game_instance = game
        self.type = ptype
        self.velocity = velocity
        self.animation: "Animation" = Particle.game_instance.assets[
            "particles/" + particle_map[ptype]
        ].copy()
        self.pos: List[float] = [
            pos[0] + offset_dir * TILE_SIZE[0],
            pos[1],
        ]

    def update(self, dt: float):
        kill = False
        if self.animation.has_animation_end():
            kill = True
        self.pos[0] += dt * BASE_SPEED * self.velocity[0]
        self.pos[1] += dt * BASE_SPEED * self.velocity[1]
        self.animation.update()
        return kill

    def render(self, surface: Surface, offset=(0, 0)):
        frame = self.animation.get_frame()
        pos_x = self.pos[0] - offset[0] - frame.height // 2
        pos_y = self.pos[1] - offset[1] - frame.width // 2
        surface.blit(frame, (pos_x, pos_y))

    @classmethod
    def add_particles(cls, particle: "Particle"):
        cls.other_particle_group.append(particle)

    @classmethod
    def spawn_leafs(cls, game: "Game", rects: Sequence[Rect]):
        for rect in rects:
            if random() * 49999 < rect.width * rect.height:
                pos = (
                    int(rect.x + random() * rect.width),
                    int(rect.y + random() * rect.height),
                )
                leaf = cls(game, "leaf", pos, (0, 0.3))
                cls.leaf_group.append(leaf)

    @classmethod
    def update_leafs(cls, dt: float):
        if not cls.leaf_group:
            return

        cls.leaf_group = [leaf for leaf in cls.leaf_group if not leaf.update(dt)]

        if not cls.leaf_group:
            return

        arb_leafanim = cls.leaf_group[0].animation
        noise = natural_x(arb_leafanim.frame_index, arb_leafanim.frameslen, 1)

        for leaf in cls.leaf_group:
            leaf.pos[0] += noise  # type: ignore

    @classmethod
    def update_particles(cls, dt: float):
        Particle.update_leafs(dt)
        cls.other_particle_group = [
            particle for particle in cls.other_particle_group if not particle.update(dt)
        ]

    @classmethod
    def draw_particles(cls, surf: Surface, scroll: Tuple[int, int]):
        for particle in cls.leaf_group + cls.other_particle_group:
            particle.render(surf, scroll)
