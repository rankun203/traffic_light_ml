import random
import gymnasium as gym
from gymnasium.envs.registration import register


register(id="traffic_light", entry_point="simulator.gym_env:TrafficSimulatorEnv")
env = gym.make("traffic_light", render_mode="human")

seed = 41


def next_seed():
    global seed
    seed += 1
    return seed


observation, info = env.reset(seed=next_seed())
for _ in range(10000):
    env.render()
    # action = env.action_space.sample()
    random.seed(next_seed())
    rand_num = random.random()
    action = 0 if rand_num > 0.01 else 1
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset(seed=next_seed())
        print(f'reset (action={action})', observation, info)
env.close()
