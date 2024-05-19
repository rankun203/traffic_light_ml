import numpy as np

class TrafficLightEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        # 4 directions, 2 lanes in each direction (straight ahead, right turn) (4, 2 ) array Random 0-10 vehicles。 
        self.traffic = np.random.randint(0, 10, size=(4, 2))  
        # 0-3 indicates east-west straight ahead, east-west right turn, north-south straight ahead, north-south right turn respectively
        self.current_light = 0  
        # Counter current phase time
        self.time_in_current_phase = 0
        # Currentphase Random time 10-30 seconds.
        # self.phase_duration = np.random.randint(10, 31)
        # Current phase Fixed time 10 seconds
        self.phase_duration = 10
        return self.get_state()
    
    def encode_state(self):
        # Encoding the signal status and the number of vehicles into a unique integer
        light_code = self.current_light * (10 ** 9)  # Give a lot of weight to the signal status
        traffic_code = 0
        for i in range(4):  # 4 directions
            for j in range(2):  # Two lanes in each direction.
                traffic_code *= 10
                traffic_code += self.traffic[i, j]
        
        return light_code + traffic_code

    def get_state(self):
        # .concatenate() Used to concatenate two arrays into a single array
        # .flatten() method converts this multidimensional array into a one-dimensional array.
        # return np.concatenate((self.traffic.flatten(), [self.current_light, self.time_in_current_phase]))
        return self.encode_state()
    
    def step(self, action):
        if action:
            # Switch to the next signal
            self.current_light = (self.current_light + 1) % 4
            # Random time of the next signal
            # self.phase_duration = np.random.randint(10, 31)
            self.phase_duration = 10
            # Time to reset the new signal 0
            self.time_in_current_phase = 0
        else:
            self.time_in_current_phase += 1

        # Vehicles passing through
        traffic_passed = min(self.traffic[self.current_light // 2, self.current_light % 2], np.random.randint(1, 6))
        
        # Update the traffic array.
        self.traffic[self.current_light // 2, self.current_light % 2] -= traffic_passed

        # Determine the number of vehicles remaining in the lane at the current signal phase
        traffic_remaining = self.traffic[self.current_light // 2, self.current_light % 2]

        # A simple design of the reward function is for vehicles that pass 
        reward = self.compute_reward(traffic_passed,traffic_remaining)
        # If the current time is greater than the designed duration, it ends.
        done = self.time_in_current_phase >= self.phase_duration
        return self.get_state(), reward, done
    
    def compute_reward(self, traffic_passed, traffic_remaining):
        efficiency = traffic_passed / (traffic_passed + traffic_remaining + 1)  # 避免除以零
        penalty = -np.sum(traffic_remaining)
        return 10 * efficiency + penalty
    
    def update_traffic(self):
        # Increase vehicles on traffic roads
        self.traffic += np.random.randint(0, 3, size=(4, 2))

class QLearningAgent:
    def __init__(self, state_size, action_size):
        # Initialize q table state and action decisions.
        self.q_table = np.zeros((state_size, action_size))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        # 10% Chance to choose a random action.
        self.epsilon = 0.1

    def choose_action(self, state):
        # If random number is less than epsilon random quest Otherwise choose Q table max.
        if np.random.rand() < self.epsilon:
            return np.random.choice([0, 1])  # 0: hold, 1: switch
        else:
            return np.argmax(self.q_table[state])

    def update(self, state, action, reward, next_state):
        # Determine the highest Q-value action for the next state
        best_next_action = np.argmax(self.q_table[next_state])
        # Calculate the target (TD) Q-value.
        td_target = reward + self.discount_factor * self.q_table[next_state, best_next_action]
        # Calculation Time Difference (TD), the difference between the target Q value and the current Q value
        td_error = td_target - self.q_table[state, action]
        # Update Q table
        self.q_table[state, action] += self.learning_rate * td_error

# Initialize the environment and intelligences
env = TrafficLightEnv()
# Holding or switching signals
action_size = 2  
# Multiply by 4 because of the 4 states of the signals
state_size = 4 * 10 ** 8

agent = QLearningAgent(state_size, action_size)

# training parameter
episodes = 10000  # Number of training rounds
learning_steps_per_episode = 1800  #Maximum number of steps per turn (simulated for 30 minutes, one time step per second) 

# training cycle
for e in range(episodes):
    state = env.reset()
    total_reward = 0

    for step in range(learning_steps_per_episode):
        state_index = np.dot(state, range(state.size))  
        action = agent.choose_action(state_index)
        next_state, reward, done = env.step(action)

        next_state_index = np.dot(next_state, range(next_state.size)) 
        agent.update(state_index, action, reward, next_state_index)

        state = next_state
        total_reward += reward

        if done:
            break

    if e % 100 == 0 and agent.epsilon > 0.01:
        agent.epsilon *= 0.99
        print(f"Episode {e+1}/{episodes}, Total reward: {total_reward}")

