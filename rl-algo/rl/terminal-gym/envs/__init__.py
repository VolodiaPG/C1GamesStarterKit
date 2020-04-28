from gym.envs.registration import register

register(id='TerminalEnv-v0',
    entry_point='envs.terminal_env_v0:TerminalEnv'
)