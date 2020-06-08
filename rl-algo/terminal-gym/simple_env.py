import gym
import terminal_gym

if __name__ == "__main__":
    env = gym.make('TerminalEnv-v0')
    env.set_log_level_by(3)
    print("Starting")
    for _ in range(2):
        env.reset()
        for _ in range(100):
            _, _, done, _ = env.step(env.action_space.sample())
            if done:
                print("Hey, I'm done, quitting")
                break
    env.close()
