from collections import defaultdict
from typing import Dict, Tuple
from gymnasium import Env
import numpy as np


class TrafficLightAgent:
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
        self.q_values = defaultdict(lambda: np.zeros(self.env.action_space.n))

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs: dict) -> int:
        obs_key = self._obs_to_tuple(obs)
        if np.random.random() < self.epsilon:
            action = self.env.action_space.sample()
            print(f"[agent] exploring: Chose random action {action}")
        else:
            action = int(np.argmax(self.q_values[obs_key]))
            print(f"[agent] exploiting: Chose best known action {action}")
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

        future_q_value = (not terminated) * np.max(self.q_values[next_obs_key])
        temporal_difference = (
            reward + self.discount_factor * future_q_value -
            self.q_values[obs_key][action]
        )

        self.q_values[obs_key][action] += self.lr * temporal_difference
        print(
            f"[agent] updated Q-value for state {obs_key}, action {action}: New Q-value = {self.q_values[obs_key][action]}")

        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        old_epsilon = self.epsilon
        self.epsilon = max(self.final_epsilon,
                           self.epsilon - self.epsilon_decay)
        print(f"[agent] epsilon decayed from {old_epsilon} to {self.epsilon}")

    def _obs_to_tuple(self, obs: dict) -> tuple:
        """Convert observation dictionary to a tuple to be used as keys in Q-value dict."""
        # This function now handles nested dictionaries
        return tuple((key, tuple(value.items()) if isinstance(value, dict) else value) for key, value in sorted(obs.items()))
