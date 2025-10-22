from typing import Sequence
from pygame import Surface


class Animation:
    def __init__(self, frames: Sequence[Surface], animation_speed=0.2, loop=True):
        assert len(frames) > 0
        self.frames = frames
        self.loop = loop
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frameslen = len(self.frames)

    def copy(self):
        return Animation(self.frames, self.animation_speed, self.loop)

    def change_frame(self, frame: int):
        self.frame_index = int(frame) % self.frameslen

    def update(self):
        self.frame_index += self.animation_speed
        if self.has_animation_end():
            if self.loop:
                self.reset_animation()
            else:
                self.frame_index = self.frameslen

    def get_frame(self):
        frame_index = int(self.frame_index) % self.frameslen
        return self.frames[frame_index]

    def has_animation_end(self):
        return self.frame_index >= self.frameslen

    def reset_animation(self):
        self.frame_index = 0
