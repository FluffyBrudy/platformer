from typing import Union

import pygame


class Timer:
    """
    Args:
            interval (float): milisecond time interval
    """

    __slots__ = ("interval", "start_timer")

    def __init__(self, interval: Union[float, int]) -> None:
        self.start_timer = pygame.time.get_ticks()
        self.interval = interval

    def reset_to_now(self):
        self.start_timer = pygame.time.get_ticks()

    def has_reach_interval(self):
        return (pygame.time.get_ticks() - self.start_timer) >= self.interval

    def update(self) -> bool:
        """rely on return type and not on manuall access of start_timer. start_timer will be out of sync before accessed"""
        if self.has_reach_interval():
            self.reset_to_now()
            return True
        return False
