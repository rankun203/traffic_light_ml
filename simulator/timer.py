from typing import Optional
from pygame import time


class CustomClock:
    def __init__(self, speed=1):
        self.world_start = time.get_ticks()
        self.speed = speed
        self.paused_at_raw: Optional[float] = None

    def get_ticks(self):
        """
        Return current time in milliseconds
        With the speed factor applied
        """
        now = time.get_ticks()
        return (now - self.world_start) * self.speed

    def pause_clock(self):
        self.paused_at_raw = time.get_ticks()

    def resume_clock(self):
        """
        Make up for the lost time
        """
        if self.paused_at_raw is not None:
            since_pause_raw = time.get_ticks() - self.paused_at_raw
            self.world_start += since_pause_raw
            self.paused_at_raw = None


CustomClock_INSTANCE = CustomClock(speed=1)


def set_clock(speed=1):
    global CustomClock_INSTANCE
    CustomClock_INSTANCE = CustomClock(speed)


def clock():
    if not CustomClock_INSTANCE:
        raise ValueError("Clock not set, use set_clock() first")
    return CustomClock_INSTANCE
