import random

import gym
import envs  # needed for TerminalEnv

import numpy as np

if __name__ == "__main__":
    num_of_episodes = 100000

    enviroment = gym.make('TerminalEnv-v0')

    alpha = 0.1
    gamma = 0.6
    epsilon = 0.1
    q_table = np.zeros([enviroment.observation_space.n, enviroment.action_space.n])

    state = None

    for episode in range(0, num_of_episodes):
        # Reset the enviroment
        state = enviroment.reset()

        # Initialize variables
        reward = 0
        terminated = False

        while not terminated:
            # Take learned path or explore new actions based on the epsilon
            print(state)
            if random.uniform(0, 1) < epsilon:
                action = enviroment.action_space.sample()
            else:
                action = np.argmax(q_table[state])

            # Take action
            next_state, reward, terminated, info = enviroment.step(action)

            # Recalculate
            q_value = q_table[state, action]
            max_value = np.max(q_table[next_state])
            new_q_value = (1 - alpha) * q_value + alpha * (reward + gamma * max_value)

            # Update Q-table
            q_table[state, action] = new_q_value
            state = next_state

        if (episode + 1) % 100 == 0:
            # clear_output(wait=True)
            print("Episode: {}".format(episode + 1))
            # enviroment.render()

    print("**********************************")
    print("Training is done!\n")
    print("**********************************")
