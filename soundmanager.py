from typing import Dict, Literal, Optional
import pygame
from constants import BASE_PATH


TSfxType = Literal["dash", "hit", "jump", "shoot"]


class SoundManager:
    _instance: Optional["SoundManager"] = None

    def __init__(self) -> None:
        sfx_path = BASE_PATH / "assets" / "sfx"
        self.sounds: Dict[TSfxType, pygame.Sound] = {
            "dash": pygame.mixer.Sound(sfx_path / "dash.wav"),
            "shoot": pygame.mixer.Sound(sfx_path / "shoot.wav"),
            "jump": pygame.mixer.Sound(sfx_path / "jump.wav"),
            "hit": pygame.mixer.Sound(sfx_path / "hit.wav"),
        }
        self.channels = [pygame.Channel(i) for i in range(5)]
        for channel in self.channels:
            channel.set_volume(1)

        self.next_channel = 1

    def play_sfx(self, sfx_type: TSfxType):
        try:
            free_channel = next(
                (ch for ch in self.channels[1:] if not ch.get_busy()), None
            )
            if free_channel is None:
                free_channel = self.channels[self.next_channel]
                free_channel.stop()
            free_channel.play(self.sounds[sfx_type])
            self.next_channel = max(1, (self.next_channel + 1) % len(self.channels))
        except pygame.error as e:
            print(e)
