import logging
import gym
from gym import spaces
import subprocess
# import threading
import os
import signal
import sys
import time
import rpyc

LOG_FMT = logging.Formatter('%(levelname)s '
                            '[%(filename)s:%(lineno)d] %(message)s',
                            '%Y-%m-%d %H:%M:%S')

PORT = 4242  # port to communicate with the game playing throught the java program
HOSTNAME = "localhost"

is_windows = sys.platform.startswith('win')
# Get location of this run file
file_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.join(file_dir, os.pardir)
parent_dir = os.path.join(parent_dir, os.pardir)
parent_dir = os.path.join(parent_dir, os.pardir)
parent_dir = os.path.join(parent_dir, os.pardir)
parent_dir = os.path.abspath(parent_dir)
file_dir = os.path.abspath(file_dir)

ALGO1 = file_dir + ("\\run.ps1" if is_windows else "/run.sh")
ALGO2 = parent_dir + ("\\python-algo\\run.ps1" if is_windows else '/python-algo/run.sh')
ENGINE = parent_dir + ("\\engine.jar" if is_windows else "/engine.jar")
print(ENGINE)
COMMAND_SINGLE_GAME = f'java -jar {ENGINE} work {ALGO1} {ALGO2}'

MAP_SIZE: int = 27 * 14

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
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        preexec_fn=os.setsid
    )
    pro.daemon = 1  # daemon necessary so game shuts down if this script is shut down by user
    # thread = threading.Thread(target=run_in_thread, args=(on_exit_fn, pro))
    # thread.start()
    return pro


def terminate_single_game(process):
    logging.info('manually killing a subprocess')
    os.kill(os.getpgid(process.pid), signal.SIGTERM)  # send the signal to all the process in the group


class TerminalEnv(gym.Env, rpyc.Service):

    def __init__(self):
        super(TerminalEnv, self).__init__()
        self.process = None
        self.conn = None

        # define the obersvation space, ie the whole board + extra :
        # credits ; score
        self.observation_space = spaces.Discrete(MAP_SIZE + 2 * 2)
        # we assume the actions available are placing something on the board in 1 step
        # then there is still the option of being able to stop the turn and go on to the next
        self.action_space = spaces.Discrete(int(MAP_SIZE / 2) * 8)

        # self.seed()
        logging.info('Environment initialized')

    def step(self, action):
        assert self.action_space.contains(action)

        reward = NO_REWARD

        move_id = (action - action % MAP_SIZE) / MAP_SIZE
        if (move_id < 8):
            location_id = action % MAP_SIZE
            x = location_id % MAP_SIZE
            y = location_id / MAP_SIZE

            assert self.conn.root.perform_action((x, y), move_id) == True
        else:
            self.conn.root.wrap_up_turn()
            reward = WIN_REWARD

        logging.info('Step successful!')

        return self._get_obs(), reward, self.done, None

    def reset(self):
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
            time.sleep(0.500)
            attempts += 1

        if (self.conn):
            logging.info(f'Connection successful to game engine after {attempts} attempts')
        else:
            raise
        logging.info('Environment reset')
        return self._get_obs()

    def _get_obs(self):
        map = tuple(self.conn.root.get_map())
        details = tuple(self.conn.root.get_details())
        return map, details

    def on_connect(self, conn):
        # connect back to the source, ie the script we just started
        # self.conn = rpyc.connect(HOSTNAME, PORT)
        self.conn = conn
        pass

    def on_disconnect(self, conn):
        pass

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
