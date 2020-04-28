import logging
import gym
import subprocess
import threading
import os
import signal

LOG_FMT = logging.Formatter('%(levelname)s '
                            '[%(filename)s:%(lineno)d] %(message)s',
                            '%Y-%m-%d %H:%M:%S')

ALGO_PORT = 4242 # port to communicate with the game playing throught the java program
IP_ALGO = "127.0.0.1"

ALGO1 = "./run.sh"
ALGO2 = "../../../../python-algo/run.sh"
ENGINE = "../../../../engine.jar"
COMMAND_SINGLE_GAME = f'java -jar  {ENGINE} work {ALGO1} {ALGO2}'

def run_single_game(on_exit_fn):
    """
    Runs the game in a thread thanks to a subprocess.Popen
    on_exit when the instance finishes
    returns the subprocess process
    """
    logging.info("Start run a match")
    
    def run_in_thread(on_exit_fn):
        pro = subprocess.Popen(
            COMMAND_SINGLE_GAME,
            shell=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            preexec_fn=os.setsid
            )
        # daemon necessary so game shuts down if this script is shut down by user
        pro.daemon = 1
        pro.wait()
        logging.info(f'Game finished, {'calling callback' if on_exit_fn else 'no callback set, finished'}')
        on_exit_fn()
    thread = threading.Thread(target=run_in_thread, args=(on_exit))
    thread.start()
    return pro

def terminate_single_game(process):
    loggin.info('manually killing a subprocess')
    os.kill(os.getpgid(process.pid), signal.SIGTERM) # send the signal to all the process in the group

class TerminalEnv(gym.env):

    def __init__(self):
        self.process = None

        self.seed()
        logging.info(‘Environment initialized’)
        
    def step(self, action):
        logging.info(‘Step successful!’)

    def reset(self):
        if self.process:
            terminate_single_game(self.process)
        run_single_game()

        logging.info(‘Environment reset’)
    
    def set_log_level_by(verbosity):
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