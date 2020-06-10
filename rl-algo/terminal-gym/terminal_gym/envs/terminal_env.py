import logging
import gym
from gym import spaces
import subprocess
import threading
import os
import signal
import sys
import time
import rpyc
from terminal_gym.envs.middleware import Middleware

LOG_FMT = logging.Formatter('%(levelname)s '
                            '[%(filename)s:%(lineno)d] %(message)s',
                            '%Y-%m-%d %H:%M:%S')

PORT = 42224  # port to communicate with the game playing throught the java program
HOSTNAME = "127.0.0.1"
DELAY = 0.05  # seconds

is_windows = sys.platform.startswith('win')
# Get location of this run file
file_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(file_dir, os.pardir)
parent_dir = os.path.join(parent_dir, os.pardir)
parent_dir = os.path.join(parent_dir, os.pardir)
parent_dir = os.path.join(parent_dir, os.pardir)
parent_dir = os.path.abspath(parent_dir)
file_dir = os.path.abspath(file_dir)

ALGO1 = file_dir
ALGO2 = parent_dir + ("\\simple-algo" if is_windows else '/simple-algo')

COMMAND_SINGLE_GAME = f'cd {parent_dir} && .\\scripts\\run_match.ps1 {ALGO1} {ALGO2}' if is_windows else f'cd {parent_dir} && ./scripts/run_match.sh {ALGO1} {ALGO2}'
print(COMMAND_SINGLE_GAME)

LINE_SIZE: int = 14
MAP_SIZE: int = 27 * LINE_SIZE
NUM_DIFFERENT_UNIT_TYPES: int = 6

NO_REWARD = 0
WIN_REWARD = 1
LOSS_REWARD = -1



def run_single_game():
    """
    Runs the game in a thread thanks to a subprocess.Popen
    on_exit when the instance finishes
    returns the subprocess process
    """
    logging.info("Start run a match")

    # def run_in_thread(on_exit_fn, pro):
    #     # daemon necessary so game shuts down if this script is shut down by user
    #     pro.daemon = 1
    #     pro.wait()
    #     logging.info(f'Game finished, {"calling callback" if on_exit_fn else "no callback set, finished"}')
    #     on_exit_fn()

    pro = subprocess.Popen(
        COMMAND_SINGLE_GAME,
        # shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        # preexec_fn=os.setsid
    )
    pro.daemon = 1  # daemon necessary so game shuts down if this script is shut down by user
    # thread = threading.Thread(target=run_in_thread, args=(on_exit_fn, pro))
    # thread.start()
    return pro


def terminate_single_game(process):
    logging.info('manually killing a subprocess')
    process.kill()
    # os.kill(os.getpgid(process.pid), signal.SIGTERM)  # send the signal to all the process in the group


class TerminalEnv(gym.Env, rpyc.Service):

    def __init__(self):
        super(TerminalEnv, self).__init__()
        self.process = None

        self.server = threading.Thread(target=lambda: rpyc.ThreadedServer(Middleware(), port=PORT).start(), daemon=True)
        self.server.start()
        self.conn = None

        # define the obersvation space, ie the whole board + extra :
        # credits ; score
        self.observation_space = spaces.Discrete(MAP_SIZE + 2 * 2)
        # we assume the actions available are placing something on the board in 1 step
        # then there is still the option of being able to stop the turn and go on to the next
        self.action_space = spaces.Discrete(int(MAP_SIZE / 2) * NUM_DIFFERENT_UNIT_TYPES + 1)

        # self.seed()
        logging.info('Environment initialized')

    def step(self, action: int):
        # self.conn.root.add_movement(action)
        # return None, None, None, None
        assert self.action_space.contains(action)

        logging.info(f"Waiting for step with action {action}...")

        while not self.conn.root.is_available_to_add():
            time.sleep(DELAY)

        logging.info("Done waiting, stepping.")

        reward = NO_REWARD

        move_id = int(action / int(MAP_SIZE / 2))
        if move_id == 0:
            logging.warning("Wrapping up our turn")
            self.conn.root.add_movement(-1)
            # wrap up turn
            pass
        else:
            action -= 1  # 0 is the wrap up turn
            location_id = action % int(MAP_SIZE / 2)
            x = location_id % LINE_SIZE
            y = int(location_id / LINE_SIZE)

            logging.warning(f"Making move: unit #{move_id} to ({x}, {y})")

            self.conn.root.add_movement(((x, y), move_id))
            # assert self.conn.root.perform_action((x, y), move_id) == True
        # else:
        #     self.conn.root.wrap_up_turn()
        # reward = WIN_REWARD

        logging.info('Step successful!')

        done = self.conn.root.is_done()
        # if done:
        #     self.conn.close()

        return self._get_obs(), reward, done, None

    def reset(self):
        # if self.conn:
        #     self.conn.close()
        #     self.conn = None

        if self.process:
            terminate_single_game(self.process)
            self.process = None
        self.process = run_single_game()

        attempts = 0
        for _ in range(20):
            try:
                self.conn = rpyc.connect(HOSTNAME, PORT)
                break
            except:
                pass
            time.sleep(DELAY)
            attempts += 1

        logging.debug(attempts)

        if self.conn:
            logging.info(f'Connection successful to game engine after {attempts} attempts')
        else:
            raise
        logging.warning('Connected to middleware!')
        logging.info('Environment reset')
        return self._get_obs()

    def _get_obs(self):
        while not self.conn.root.is_available_pop_obs():
            time.sleep(DELAY)
        return self.conn.root.pop_obs()

    def set_log_level_by(self, verbosity):
        """Set log level by verbosity level.
        verbosity vs log level:
            0 -> logging.ERROR
            1 -> logging.WARNING
            2 -> logging.INFO
            3 -> logging.DEBUG
        Args:
            verbosity (int): Verbosity level given by CLI option.
        Returns:
            (int): Matching log level.
        """
        level = 0
        if verbosity == 0:
            level = 40
        elif verbosity == 1:
            level = 30
        elif verbosity == 2:
            level = 20
        elif verbosity >= 3:
            level = 10

        logger = logging.getLogger()
        logger.setLevel(level)
        if len(logger.handlers):
            handler = logger.handlers[0]
        else:
            handler = logging.StreamHandler()
            logger.addHandler(handler)

        handler.setLevel(level)
        handler.setFormatter(LOG_FMT)
        return level