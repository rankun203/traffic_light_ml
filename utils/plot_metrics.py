import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_metrics(rewards: list[float], errors: list[float], key: str, show=False):
    df = pd.DataFrame({'Rewards': rewards, 'Errors': errors})

    # Create a plot with two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 5))  # Create a figure and an axes.

    # Plot left rewards
    color = 'tab:blue'
    ax1.set_xlabel('Episodes')  # X-axis label
    ax1.set_ylabel('Rewards', color=color)  # Left y-axis label
    ax1.plot(df.index, df['Rewards'], color=color)  # Plot the rewards
    # Set the color of the y-axis labels to match the plot
    ax1.tick_params(axis='y', labelcolor=color)

    # Creating a second y-axis for Errors
    ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
    color = 'tab:red'
    ax2.set_ylabel('Errors', color=color)  # Right y-axis label
    # Plot the errors with a dashed line
    ax2.plot(df.index, df['Errors'], color=color, linestyle='--')
    # Set the color of the y-axis labels to match the plot
    ax2.tick_params(axis='y', labelcolor=color)

    # Additional plot settings
    plt.title('Rewards and Errors Over Episodes')  # Title of the plot
    ax1.grid(True)  # Enable grid on the primary y-axis

    # Save and show the plot
    if not os.path.exists('training_logs/'):
        os.makedirs('training_logs/')
    plt.savefig(f'training_logs/{key}.pdf')
    if show:
        plt.show()
