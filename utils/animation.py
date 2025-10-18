from typing import Sequence
from pygame import Surface


class Animation:
    def __init__(self, frames: Sequence[Surface], image_duration: int, loop=False):
        self.frames = frames
        self.loop = loop
