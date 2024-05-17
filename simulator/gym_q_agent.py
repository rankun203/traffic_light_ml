from datetime import datetime
import re
import os
import glob
import pickle
from collections import defaultdict
import random
from typing import Dict
from gymnasium import Env
import numpy as np

from simulator.timer import clock


def default_q_value():
    """
    Default Q-value for a state-action pair: [0, 0]
    """
    return np.zeros(4)


class TrafficLightQAgent:
    pkl_file_suffix = "q_table.pkl"

    def __init__(
        self,
        env: Env,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
    ):
        """
        Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            env: The Gymnasium environment
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            discount_factor: The discount factor for computing the Q-value
        """
        self.env = env
        self.q_values = defaultdict(default_q_value)
        self.read_q_table()

        self.lr = learning_rate
        self.df = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs: dict) -> int:
        obs_key = self._obs_to_tuple(obs)
        if random.random() < self.epsilon:
            action = self.env.action_space.sample()
            print(f"[agent] exploring:  Chose random action {action}")
        else:
            action = int(np.argmax(self.q_values[obs_key]))
            print(f"[agent] exploiting: state", obs_key)
            print(f"[agent] exploiting: q value", self.q_values[obs_key])
            print(f"[agent] exploiting: chose {action}")
            # if action == 1:
            #     print(f"[agent] get_action=1 {obs_key}, Q {self.q_values[obs_key]}")  # noqa
        return action

    def update(
        self,
        obs: Dict,
        action: int,
        reward: float,
        terminated: bool,
        next_obs: Dict,
    ):
        obs_key = self._obs_to_tuple(obs)
        next_obs_key = self._obs_to_tuple(next_obs)

        # terminated - mute the future Q-value
        # Best future Q-value for the next state
        # prev = self.q_values[obs_key]
        # prev0 = prev[0]
        # prev1 = prev[1]
        future_q_value = (not terminated) * np.max(self.q_values[next_obs_key])
        q_sa = self.q_values[obs_key][action]

        # q-learning update rule, derived from the Bellman equation
        temporal_difference = reward + self.df * future_q_value - q_sa
        self.q_values[obs_key][action] = q_sa + self.lr * temporal_difference
        # nxt = self.q_values[obs_key]
        # nxt0 = nxt[0]
        # nxt1 = nxt[1]

        # if prev0 != nxt0 or prev1 != nxt1:
        #     print(f"[agent] update state", obs_key)
        #     print(f"[agent] update q {(prev0, prev1)} to {(nxt0, nxt1)}")  # noqa

        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        old_epsilon = self.epsilon
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)  # noqa
        print(f"[agent] epsilon decayed from {old_epsilon} to {self.epsilon}")

    def _obs_to_tuple(self, obs: dict) -> tuple:
        """Convert observation dictionary to a tuple to be used as keys in Q-value dict."""
        # This function now handles nested dictionaries
        return tuple((key, tuple(value.items()) if isinstance(value, dict) else value) for key, value in sorted(obs.items()))

    def print_q_table(self):
        print("[agent] Q-values:", '-' * 30)
        for state, actions in self.q_values.items():
            print(f"State: {state}, Actions: {actions}")
        print('-----------------', '-' * 30)

    def save_q_table(self, folder="./q_tables/"):
        if os.path.exists(folder):
            # remove the folder recursively
            for f in glob.glob(folder + "*"):
                os.remove(f)
        else:
            os.makedirs(folder)

        timestamp = re.sub(r'[^\w\._]', '-', datetime.now().isoformat())
        filename = f"{folder}{timestamp}_{self.pkl_file_suffix}"
        with open(filename, "wb") as f:
            print(f"[agent] Saving Q-table to {filename}, DO NOT INTERRUPT!")
            clock().pause_clock()
            pickle.dump(self.q_values, f)
            clock().resume_clock()

    def read_q_table(self, folder="./q_tables/"):
        # list files in folder (str) desc by updated time, get the first one
        files = glob.glob(folder + "*")
        if len(files) == 0:
            print(f"[agent] Q-table file not found, skip loading")
            return

        filename = sorted(files, key=os.path.getmtime, reverse=True)[0]

        print(f"[agent] Loading Q-table from {filename}")
        with open(filename, "rb") as f:
            clock().pause_clock()
            self.q_values = pickle.load(f)
            clock().resume_clock()
