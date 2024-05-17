from collections import defaultdict
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


n_action = 2
q_values = defaultdict(lambda: np.zeros(n_action))

rewards_over_episodes = [0.1, 2, 3, 4, 5, 6, 7, -1, -5, 10]
title = "Test plot"
plt.plot(rewards_over_episodes)
plt.title(title)
plt.xlabel('Episode')
plt.ylabel('Reward')
plt.grid()
plt.show()
