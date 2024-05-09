import gymnasium as gym
from gymnasium.envs.registration import register


register(id="traffic_light", entry_point="simulator.gym_env:TrafficSimulatorEnv")
env = gym.make("traffic_light", render_mode="human")

seed = 41
def next_seed(): return seed + 1


observation, info = env.reset(seed=next_seed())
for _ in range(1000):
    env.render()
    # action = env.action_space.sample()
    action = 0
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset(seed=next_seed())
        print('reset', observation, info)
env.close()
