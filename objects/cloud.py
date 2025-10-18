from pygame import Surface, Vector2, image
from random import choice, random
from typing import Callable, List, Sequence, Tuple, Union

from constants import BASE_SPEED, SCREEN_HEIGHT, SCREEN_WIDTH


class Cloud:
    def __init__(
        self, pos: Tuple[int, int], image: Surface, speed: float, depth: float
    ) -> None:
        self.pos = list(pos)
        self.image = image
        self.speed = speed
        self.depth = depth

    def update(self, dt: float):
        self.pos[0] += self.speed * BASE_SPEED * dt  # type: ignore

    def render(
        self, surface: Surface, offset: Union[Vector2, Tuple[int, int]] = (0, 0)
    ):
        pos_x = (self.pos[0] - offset[0] * self.depth) % (
            SCREEN_WIDTH + self.image.width
        ) - self.image.width
        pos_y = (self.pos[1] - offset[1] * self.depth) % (
            SCREEN_HEIGHT + self.image.height
        ) - self.image.height
        pos = (pos_x, pos_y)
        surface.blit(self.image, pos)


class CloudGroup:
    def __init__(self, cloud_images: Sequence[Surface], count=15) -> None:
        self.clouds: List[Cloud] = []

        for _ in range(count):
            cloud_image = choice(cloud_images)
            pos = (
                int(random() * 99999),
                int(random() * 99999) - cloud_image.get_height(),
            )
            speed = 0.05 + random() * (0.2)
            depth = 0.5 + random() * (0.5)
            self.clouds.append(Cloud(pos, cloud_image, speed, depth))

        cloud_sort_key: Callable[[Cloud], float] = lambda cloud: cloud.depth
        self.clouds.sort(key=cloud_sort_key)

    def update(self, dt: float):
        for cloud in self.clouds:
            cloud.update(dt)

    def render(
        self, surface: Surface, offset: Union[Vector2, Tuple[int, int]] = (0, 0)
    ):
        for cloud in self.clouds:
            cloud.render(surface, offset)
