import gymnasium as gym
from gymnasium.envs.registration import register
from tqdm import tqdm
import numpy as np
import datetime

from simulator.gym_q_agent import TrafficLightQAgent


register(id="traffic_light", entry_point="simulator.gym_env:TrafficSimulatorEnv")
env = gym.make("traffic_light", render_mode="human")

# hyperparameters
learning_rate = 0.1
n_episodes = 10
start_epsilon = 1.0
# start_epsilon = 0.5
# reduce the exploration over time
epsilon_decay = start_epsilon / (n_episodes / 2)
final_epsilon = 0.01

agent = TrafficLightQAgent(
    env=env,
    learning_rate=learning_rate,
    initial_epsilon=start_epsilon,
    epsilon_decay=epsilon_decay,
    final_epsilon=final_epsilon,
)

for seed in range(100):
    print(f"[train] {datetime.datetime.now().isoformat()} Training with seed {seed}")  # noqa
    for episode in tqdm(range(n_episodes)):
        obs, info = env.reset(seed=seed)
        done = False

        total_reward = 0

        # play one episode
        while not done:
            action = agent.get_action(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)

            # update the agent
            agent.update(obs, action, float(reward), terminated, next_obs)

            # update if the environment is done and the current obs
            done = terminated or truncated
            # done = terminated
            obs = next_obs
            total_reward += float(reward)

            if done:
                print(f'resetting (action={action}, reward={reward})', next_obs, info)  # noqa
                observation, info = env.reset()
                # print(f'[train] {datetime.datetime.now().isoformat()} Resetting (action={action}, reward={reward})', obs, info)  # noqa

        agent.decay_epsilon()
        # Average training error over the last 100 episodes
        avg_error = np.mean(agent.training_error[-100:])
        # add time to print
        print(f"[train] {datetime.datetime.now().isoformat()} Episode {episode}: Total Reward = {total_reward}, Average Training Error = {avg_error}")  # noqa
        agent.print_q_table()


env.close()
