import gymnasium as gym
env = gym.make("CartPole-v1", render_mode="human")

observation, info = env.reset(seed=42)
for _ in range(1000):
    env.render()
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)

    print('terminated:', terminated, 'truncated:', truncated, 'reward:', reward)  # noqa
    if terminated or truncated:
        observation, info = env.reset()
        print('reset', observation, info)
env.close()
