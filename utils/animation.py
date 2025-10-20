from typing import Sequence
from pygame import Surface
from copy import deepcopy


class Animation:
    def __init__(self, frames: Sequence[Surface], animation_speed=0.2, loop=False):
        assert len(frames) > 0
        self.frames = deepcopy(frames)
        self.loop = loop
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frameslen = len(self.frames)

    def update(self):
        self.frame_index += self.animation_speed
        if self.has_animation_end():
            if not self.loop:
                self.reset_animation(-1)
                return
            self.reset_animation()

    def get_frame(self):
        frame_index = int(self.frame_index) % self.frameslen
        return self.frames[frame_index]

    def has_animation_end(self):
        return self.frame_index >= self.frameslen

    def reset_animation(self, step_back=0):
        self.frame_index = step_back
