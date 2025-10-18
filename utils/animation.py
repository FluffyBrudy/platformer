from typing import Sequence
from pygame import Surface


class Animation:
    def __init__(self, frames: Sequence[Surface], animation_speed=0.1, loop=False):
        self.frames = frames
        self.loop = loop
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frameslen = len(self.frames)

    def update(self):
        self.frame_index += self.animation_speed
        if self.has_animation_end():
            if not self.loop:
                self.reset_animation()
                return
            self.reset_animation()

    def get_frame(self):
        return int(self.frame_index)

    def has_animation_end(self):
        return self.frame_index >= self.frameslen

    def reset_animation(self):
        self.frame_index = 0
