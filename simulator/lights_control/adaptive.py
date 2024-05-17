import random
from typing import Optional
from simulator.timer import clock
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
        self.phase_start_ms = clock().get_ticks()
        self.phase_min_s: int = timings["phase_min_s"]
        self.phase_max_s: int = timings["phase_max_s"]
        self.phase_yellow_s: int = timings["phase_yellow_s"]
        self.current_phase_i = 0  # defaults to 0, but will be overridden by reset()
        self.next_phase_started_ms: Optional[float] = None

    def reset(self, seed: Optional[int] = None):
        """
        Reset the lights control to a random phase
        """
        random.seed(seed)
        self.current_phase_i = random.randint(0, len(self.phases) - 1)
        self.phase_start_ms = clock().get_ticks()

    def next_phase(self):
        if self.next_phase_started_ms is not None:
            # already in the middle of a phase change
            return

        clock_ms = clock().get_ticks()
        self.next_phase_started_ms = clock_ms

        # self.current_phase_i = (self.current_phase_i + 1) % len(self.phases)

        # undertime = clock_ms - self.phase_start_ms < self.phase_min_s * 1000
        # self.phase_start_ms = clock_ms
        # return undertime

    def switch_to_next_phase(self):
        self.current_phase_i = (self.current_phase_i + 1) % len(self.phases)
        self.phase_start_ms = clock().get_ticks()

    def next_tick(self):
        if self.next_phase_started_ms is not None:
            clock_ms = clock().get_ticks()
            if clock_ms - self.next_phase_started_ms >= self.phase_yellow_s * 1000:
                self.switch_to_next_phase()
                self.next_phase_started_ms = None

        # set current phase lights to green, all others to red
        current_phase = self.phases[self.current_phase_i]
        for light in current_phase.lights:
            if self.next_phase_started_ms is not None:
                light.set_yellow()
            else:
                light.set_green()
        for phase in self.phases:
            if phase != current_phase:
                for light in phase.lights:
                    light.set_red()

        overtime = clock().get_ticks() - self.phase_start_ms > self.phase_max_s * 1000
        return overtime

    def get_phase_time(self):
        if self.next_phase_started_ms is not None:
            # print('[get_phase_time] yellow', self.next_phase_started_ms, self.phase_start_ms)  # noqa
            return self.next_phase_started_ms - self.phase_start_ms
        else:
            # print('[get_phase_time] green', clock().get_ticks(), self.phase_start_ms)  # noqa
            return clock().get_ticks() - self.phase_start_ms
