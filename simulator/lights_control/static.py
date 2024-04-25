from pygame import time


class Phase:
    def __init__(self, lights: list, duration_s: int):
        self.lights = lights
        self.duration_s = duration_s


class StaticLightsControl:
    def __init__(self, lights_phases_config: list[Phase]):
        self.phases = lights_phases_config

    def next_tick(self):
        clock_ms = time.get_ticks()
        total_duration_s = sum([phase.duration_s for phase in self.phases])
        phase_ms = clock_ms % (total_duration_s * 1000)

        current_phase = self.phases[0]
        for phase in self.phases:
            if phase_ms < phase.duration_s * 1000:
                current_phase = phase
                break
            phase_ms -= phase.duration_s * 1000

        # set current phase lights to green, all others to red
        for light in current_phase.lights:
            light.set_green()
        for phase in self.phases:
            if phase != current_phase:
                for light in phase.lights:
                    light.set_red()
