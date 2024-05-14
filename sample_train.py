import numpy as np

class TrafficLightEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        # 4个方向，每个方向2条车道(直行，右拐) （4，2 ）数组 随机0-10车辆。 
        self.traffic = np.random.randint(0, 10, size=(4, 2))  
        # 0-3 分别表示东西直行，东西右拐，南北直行，南北右拐
        self.current_light = 0  
        # 计数器当前 phase时间
        self.time_in_current_phase = 0
        # 当前phase 随机时间10-30秒。
        # self.phase_duration = np.random.randint(10, 31)
        # 当前phase 固定时间 10秒
        self.phase_duration = 10
        return self.get_state()
    
    def encode_state(self):
        # 将信号灯状态和车辆数编码成一个唯一的整数
        light_code = self.current_light * (10 ** 9)  # 给信号灯状态一个很大的权重
        traffic_code = 0
        for i in range(4):  # 4个方向
            for j in range(2):  # 每个方向有两条车道
                traffic_code *= 10
                traffic_code += self.traffic[i, j]
        
        return light_code + traffic_code

    def get_state(self):
        # .concatenate() 用于将两个数组连接成一个数组。。
        # .flatten() 方法将这个多维数组转换成一个一维数组。
        # return np.concatenate((self.traffic.flatten(), [self.current_light, self.time_in_current_phase]))
        return self.encode_state()
    
    def step(self, action):
        if action:
            # 切换下一个信号灯
            self.current_light = (self.current_light + 1) % 4
            # 下一个信号灯的随机时间
            # self.phase_duration = np.random.randint(10, 31)
            self.phase_duration = 10
            # 重置新的信号灯的时间 为0
            self.time_in_current_phase = 0
        else:
            self.time_in_current_phase += 1

        # 通过的车辆
        traffic_passed = min(self.traffic[self.current_light // 2, self.current_light % 2], np.random.randint(1, 6))
        
        # 更新traffic数组。
        self.traffic[self.current_light // 2, self.current_light % 2] -= traffic_passed

        # 确定当前信号阶段车道上剩余的车辆数
        traffic_remaining = self.traffic[self.current_light // 2, self.current_light % 2]

        # 简单设计奖励函数，就是为通过的车辆 
        reward = self.compute_reward(traffic_passed,traffic_remaining)
        # 如果 当前时间 大于设计的持续时间则结束
        done = self.time_in_current_phase >= self.phase_duration
        return self.get_state(), reward, done
    
    def compute_reward(self, traffic_passed, traffic_remaining):
        efficiency = traffic_passed / (traffic_passed + traffic_remaining + 1)  # 避免除以零
        penalty = -np.sum(traffic_remaining)
        return 10 * efficiency + penalty
    
    def update_traffic(self):
        # 增加traffic道路的车辆 
        self.traffic += np.random.randint(0, 3, size=(4, 2))

class QLearningAgent:
    def __init__(self, state_size, action_size):
        # 初始化 q table state 和 action 决定。
        self.q_table = np.zeros((state_size, action_size))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        # 10% 几率选择一个随机动作。
        self.epsilon = 0.1

    def choose_action(self, state):
        # 如果随机数小于 epsilon 随机探索 否则选择Q table最大值
        if np.random.rand() < self.epsilon:
            return np.random.choice([0, 1])  # 0: hold, 1: switch
        else:
            return np.argmax(self.q_table[state])

    def update(self, state, action, reward, next_state):
        # 确定下一个状态的最高Q值的action
        best_next_action = np.argmax(self.q_table[next_state])
        # 计算目标（TD） Q值，
        td_target = reward + self.discount_factor * self.q_table[next_state, best_next_action]
        # 计算 时差（TD），目标Q值和当前Q值的差
        td_error = td_target - self.q_table[state, action]
        # 更新Q table
        self.q_table[state, action] += self.learning_rate * td_error

# 初始化环境和智能体
env = TrafficLightEnv()
# 保持或切换信号
action_size = 2  
# 乘以4是因为信号灯的4种状态
state_size = 4 * 10 ** 8

agent = QLearningAgent(state_size, action_size)

# 训练参数
episodes = 10000  # 训练回合数
learning_steps_per_episode = 1800  # 每个回合的最大步数（模拟30分钟，每秒一个时间步）

# 训练循环
for e in range(episodes):
    state = env.reset()
    total_reward = 0

    for step in range(learning_steps_per_episode):
        state_index = np.dot(state, range(state.size))  # 简单的状态编码为整数索引
        action = agent.choose_action(state_index)
        next_state, reward, done = env.step(action)

        next_state_index = np.dot(next_state, range(next_state.size))  # 下一个状态的索引
        agent.update(state_index, action, reward, next_state_index)

        state = next_state
        total_reward += reward

        if done:
            break

    if e % 100 == 0 and agent.epsilon > 0.01:
        agent.epsilon *= 0.99
        print(f"Episode {e+1}/{episodes}, Total reward: {total_reward}")

# np.save('q_table.npy', agent.q_table)