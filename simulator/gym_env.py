import os
from typing import Any, Optional
from gymnasium import Env, spaces
import numpy as np
import pygame
from pygame.time import Clock

from simulator.environment import Environment
from simulator.lights_control.adaptive import AdaptiveLightsControl, Phase
from simulator.lights_control.light import lit_north_left, lit_north_through, lit_north_right, lit_south_left, lit_south_through, lit_south_right, lit_west_left, lit_west_through, lit_west_right, lit_east_left, lit_east_through, lit_east_right
from simulator.config import streets, cars_config, game_config
from simulator.traffic import Traffic


class TrafficSimulatorEnv(Env):
    """
    Custom Gym environment for the traffic simulator

    Action space: {0, 1}
    - 0: Do nothing
    - 1: Change the traffic lights
    """
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 60,
        "render_width": game_config['screen_width'],
        "render_height": game_config['screen_height'],
        "traffic_light_timings": {
            "phase_min_s": 10,  # green
            "phase_max_s": 300,  # green
            "phase_yellow_s": 3,  # yellow light duration
        },
        "max_queue_length": 8,
        "max_cars_in_lane": 8,
        "max_waiting_time": 100  # 100s
    }

    def __init__(self, render_mode=None):
        super(TrafficSimulatorEnv, self).__init__()

        # Force render mode to human.
        render_mode = "human"

        # Initialize your game components here
        self.lights_phases_config = [
            Phase([lit_north_right, lit_south_right]),
            Phase([lit_north_through, lit_north_left,
                   lit_south_through, lit_south_left]),
            Phase([lit_west_right, lit_east_right]),
            Phase([lit_west_through, lit_west_left,
                  lit_east_through, lit_east_left]),
        ]

        self.render_mode = render_mode
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[Clock] = None
        self.environment: Optional[Environment] = None
        self.lights_control = AdaptiveLightsControl(self.lights_phases_config, self.metadata["traffic_light_timings"])  # noqa
        self.traffic = Traffic(1, streets, cars_config, game_config)

        if render_mode is not None and render_mode not in self.metadata["render_modes"]:
            raise ValueError(f"Invalid render_mode. Expected one of {self.metadata['render_modes']}, got {render_mode}")  # noqa

        # Render 1 frame to initialize necessary state (like lane length)
        if render_mode == "human":
            self._render_frame()

        # State and action
        self.observation_space = spaces.Dict({
            # Assuming a maximum of 100 finished cars
            "p": spaces.Discrete(start=0, n=len(self.lights_phases_config)),
            "ps": spaces.Discrete(start=0, n=self.metadata["traffic_light_timings"]["phase_max_s"]),
            **self._define_lanes_space(),
        })
        self.action_space = spaces.Discrete(start=0, n=4)  # phases

    def _define_lanes_space(self):
        """
        We define 2 state spaces for each lane!
        1. queue length
        2. number of cars in the lane
        """
        lanes_space = {}
        for s in streets:
            for al in s.approach_lanes:
                lanes_space[f"{s.approach_direction}_{al.to_direction}_q"] = spaces.Discrete(start=0, n=al.get_state_space())  # noqa
                # lanes_space[f"{s.approach_direction}_{al.to_direction}_aw"] = spaces.Discrete(start=0, n=self.metadata["traffic_light_timings"]["phase_max_s"])  # noqa

        return spaces.Dict(lanes_space)

    def _render_frame(self):
        """
        Private method to render the current frame / tick of the environment
        """
        screen_width = self.metadata["render_width"]
        screen_height = self.metadata["render_height"]

        if self.screen is None and self.render_mode == "human":
            # Initialize the pygame environment
            pygame.init()
            # put the window in the top left corner
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
            pygame.display.set_caption('Traffic Intersection Simulation')
            self.screen = pygame.display.set_mode(
                (screen_width, screen_height))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        if self.environment is None and self.render_mode == "human" and self.screen:
            self.canvas = pygame.Surface((screen_width, screen_height))
            self.environment = Environment(self.canvas, streets)

        if self.render_mode == "human" and self.screen and self.clock and self.environment:
            temporal_ms = self.clock.get_rawtime()
            self.environment.draw_text(f"Frame: {temporal_ms}ms", 10, 30, 0)  # noqa

            # The following line copies our drawings from `canvas` to the visible window
            self.screen.blit(self.canvas, self.canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # tick the clock to control the frame rate
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(np.array(pygame.surfarray.pixels3d(self.canvas)), axes=(1, 0, 2))

    def _get_obs(self):
        """
        Private method to capture the current state space variables
        """
        lanes = {}
        for s in streets:
            for al in s.approach_lanes:
                queue_length = al.get_state()
                lanes[f"{s.approach_direction}_{al.to_direction}_q"] = queue_length  # noqa
                # lanes[f"{s.approach_direction}_{al.to_direction}_aw"] = avg_waiting  # noqa

        return {
            "p": self.lights_control.current_phase_i,
            "ps": int(self.lights_control.get_phase_time()/1000),
            **lanes
        }

    def _obs_to_tuple(self, obs):
        """
        Convert the observation dictionary to a tuple for the Q-table
        """
        return tuple(obs.values())

    def _get_info(self):
        return {
            "debug": 0
        }

    def _check_if_done(self):
        finished_cars = len(self.traffic.finished_cars)
        all_cars = len(self.traffic.all_cars)
        is_done = finished_cars > 0 and all_cars <= 0  # Termination condition

        # TODO: add another time out termination

        if not is_done:
            for s in streets:
                for al in s.approach_lanes:
                    if al.get_queue_length() > self.metadata["max_queue_length"]:
                        return True

        return is_done

    def _calculate_reward(self):
        """
        Reward for every car passing, penalty for every step the cars waiting
        """
        phase_stay_ms = self.lights_control.get_phase_time()
        total_queue_length = self.traffic.calc_total_queue_length()
        total_waiting_ms = self.traffic.calc_waiting_time()

        # cars passed since last switch
        total_cars_passed = self.traffic.calc_passed_cars()
        last_cars_passed = self.last_switch_total_cars_passed if 'last_switch_total_cars_passed' in self.__dict__ else 0
        cars_since_switch = total_cars_passed - last_cars_passed

        reward = -total_queue_length + \
            -(total_waiting_ms / 1000 / 8) + \
            10 * cars_since_switch + \
            10 * (phase_stay_ms / 1000)  # reward for staying in the same phase # noqa

        current_p = self.lights_control.current_phase_i
        print(f"[env] reward={reward:.3f}, total_queue_length={int(total_queue_length):3d}, total_waiting={total_waiting_ms/1000/8:.0f}, cars_since_switch={int(cars_since_switch):3d}, p{current_p}={int(phase_stay_ms/1000):3d}s")  # noqa
        return reward, total_cars_passed

    def reset(self, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[dict, dict]:
        """
        The environment can start at a seeded random(R) time: R lights phase, R traffic
        """
        self.lights_control.reset(seed=seed)
        self.traffic.reset(seed=seed)
        self.last_switch_total_cars_passed = 0

        if self.render_mode == "human":
            self._render_frame()
        return self._get_obs(), self._get_info()

    def step(self, action):
        """
        action: next phase
        """
        # phase_stay_s = self.lights_control.get_phase_time() / 1000
        penalty_reward = 0
        # if phase_stay_s < self.metadata["traffic_light_timings"]["phase_min_s"]:
        #     print(f"[env] penalty: phase stay time {phase_stay_s:.3f} < {self.metadata['traffic_light_timings']['phase_min_s']}s, reset action to 0")  # noqa
        #     penalty_reward = -10
        #     action = 0

        # switch lights to the next phase
        # undertime = False
        # yellow light, then next phase
        do_switch = action == self.lights_control.current_phase_i
        self.lights_control.to_phase(action)

        # Perform one step of the environment
        overtime = self.lights_control.next_tick()
        self.traffic.next_tick()
        if self.environment is not None:
            self.environment.next_tick()

        # Capture the new state of the environment
        observation = self._get_obs()
        reward, total_cars_passed = self._calculate_reward()
        terminated = self._check_if_done()
        # truncated = overtime or undertime
        truncated = False
        info = self._get_info()  # Additional info for debugging or complex environments

        # keep record of total_cars_passed after action=1
        if do_switch:
            self.last_switch_total_cars_passed = total_cars_passed

        if self.render_mode == "human":
            self._render_frame()

        reward += penalty_reward

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array" or self.render_mode == "human":
            return self._render_frame()

    def close(self):
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()
