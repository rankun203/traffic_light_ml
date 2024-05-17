# run last saved q_table
from simulator import config
from simulator.timer import set_clock, clock
import gymnasium as gym
from gymnasium.envs.registration import register
from simulator.gym_q_agent import TrafficLightQAgent

set_clock(speed=1)  # initialize it
config.game_config["FPS"] = 60

register(id="traffic_light", entry_point="simulator.gym_env:TrafficSimulatorEnv")
env = gym.make("traffic_light", render_mode="human")

# hyperparameters
learning_rate = 0.1
n_episodes = 10
# to run the last saved q_table
start_epsilon = 0
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

obs, info = env.reset(seed=42)
done = False

total_reward = 0

while not done:
    action = agent.get_action(obs)
    next_obs, reward, terminated, truncated, info = env.step(action)
    print(reward)

    done = terminated or truncated
    obs = next_obs
    total_reward += float(reward)


print("Total Reward:", total_reward)
print("Simulation lasted:", int(clock().get_ticks()/1000), "seconds")


env.close()
