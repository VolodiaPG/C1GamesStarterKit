from gym.envs.registration import register

register(id='TerminalEnv-v0',
         entry_point='terminal_gym.envs.terminal_env:TerminalEnv'
         )
