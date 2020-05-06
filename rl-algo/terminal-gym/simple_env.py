import gym
import terminal_gym

if __name__ == "__main__":
    env = gym.make('TerminalEnv-v0')
    env.set_log_level_by(3)
    env.reset()
    for _ in range(100):
        env.step(env.action_space.sample())
    env.close()
