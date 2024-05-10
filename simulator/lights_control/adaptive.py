import random
from typing import Optional
from pygame import time
from .light import Light


class Phase:
    def __init__(self, lights: list[Light]):
        self.lights = lights


class AdaptiveLightsControl:
    """
    Adaptive, meaning no fixed time, it doesn't change light unless #next_phase() is called
    """

    def __init__(self, lights_phases_config: list[Phase], timings: dict):
        self.phases = lights_phases_config
        self.phase_start_ms = time.get_ticks()
        self.phase_min_s: int = timings["phase_min_s"]
        self.phase_max_s: int = timings["phase_max_s"]
        self.current_phase_i = 0  # defaults to 0, but will be overridden by reset()

    def reset(self, seed: Optional[int] = None):
        """
        Reset the lights control to a random phase
        """
        random.seed(seed)
        self.current_phase_i = random.randint(0, len(self.phases) - 1)
        self.phase_start_ms = time.get_ticks()

    def next_phase(self):
        clock_ms = time.get_ticks()
        self.current_phase_i = (self.current_phase_i + 1) % len(self.phases)

        undertime = clock_ms - self.phase_start_ms < self.phase_min_s * 1000
        self.phase_start_ms = clock_ms
        return undertime

    def next_tick(self):
        # set current phase lights to green, all others to red
        current_phase = self.phases[self.current_phase_i]
        for light in current_phase.lights:
            light.set_green()
        for phase in self.phases:
            if phase != current_phase:
                for light in phase.lights:
                    light.set_red()

        overtime = time.get_ticks() - self.phase_start_ms > self.phase_max_s * 1000
        return overtime

    def get_phase_time(self):
        return time.get_ticks() - self.phase_start_ms
