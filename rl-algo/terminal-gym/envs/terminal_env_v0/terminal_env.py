import logging
import gym

LOG_FMT = logging.Formatter('%(levelname)s '
                            '[%(filename)s:%(lineno)d] %(message)s',
                            '%Y-%m-%d %H:%M:%S')

ALGO_PORT = 4242 # port to communicate with the game playing throught the java program
IP_ALGO = "127.0.0.1"

ALGO1 = "./run.sh"
ALGO2 = "../../../../python-algo/run.sh"
ENGINE = "../../../../engine.jar"
COMMAND_SINGLE_GAME = f'java -jar  {ENGINE} work {ALGO1} {ALGO2}'

def run_single_game(callback_when_finished):
    logging.info("Start run a match")
    
    p = subprocess.Popen(
        COMMAND_SINGLE_GAME,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr
        )
    # daemon necessary so game shuts down if this script is shut down by user
    p.daemon = 1
    p.wait()

    logging.info("Finished running match")
    callback_when_finished()


class TerminalEnv(gym.env):

    def __init__(self):
        self.seed()
        logging.info(‘Environment initialized’)
    def step(self, action):
        logging.info(‘Step successful!’)
    def reset(self):
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