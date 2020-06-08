import rpyc
import logging

LOG_FMT = logging.Formatter('%(levelname)s '
                            '[%(filename)s:%(lineno)d] %(message)s',
                            '%Y-%m-%d %H:%M:%S')


class Memory:
    def __init__(self):
        self.ask_move = False
        self.movement = None
        self.obs = None
        self.done = False

    def set_asking_move(self, value):
        self.ask_move = value
        logging.debug(f"ask_move: {self.ask_move}")

    def add_move(self, move):
        assert move is not None
        assert self.ask_move is True
        self.set_asking_move(False)
        self.movement = move

    def pop_move(self):
        movement = self.movement
        self.movement = None
        self.set_asking_move(False)
        return movement

    def is_move_available(self):
        return self.movement is not None

    def is_obs_available(self):
        return self.obs is not None

    def add_obs(self, obs):
        assert obs is not None
        self.obs = obs

    def pop_obs(self):
        ret = self.obs
        self.obs = None
        return ret

    def set_done(self, value: bool):
        self.done = value

    def is_done(self):
        return self.done


# not much to say ...
MEMORY = Memory()


class Middleware(rpyc.Service):
    def __init__(self):
        self.set_log_level_by(3, "middleware.log")

    def on_connect(self, conn):
        """
        Handle the connection from the terminal_env
        Connect back to transmit the events
        :return: void
        """
        logging.warning("Connected")

    def on_disconnect(self, _):
        logging.warning("Disconnected")
        MEMORY.set_done(True)

    def exposed_add_movement(self, movement):
        assert movement is not None
        logging.info(f"Added movement {movement}")
        MEMORY.add_move(movement)

    def exposed_is_available_to_add(self):
        return MEMORY.ask_move

    def exposed_is_move_available(self):
        return MEMORY.is_move_available()

    def exposed_ask_next_step(self):
        logging.debug("Asked next step")
        MEMORY.set_asking_move(True)
        assert MEMORY.ask_move is True

    def exposed_pop_movement(self):
        logging.info("Popped movement")
        return MEMORY.pop_move()

    def exposed_is_available_pop_obs(self):
        return MEMORY.is_obs_available()

    def exposed_add_obs(self, obs):
        assert obs is not None
        logging.info(f"Added observation: {obs}")
        MEMORY.add_obs(obs)

    def exposed_pop_obs(self):
        logging.info("Popped observation")
        return MEMORY.pop_obs()

    def exposed_is_done(self):
        ret = MEMORY.is_done()
        MEMORY.set_done(False)
        return ret

    def set_log_level_by(self, verbosity, filename):
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
            fh = logger.handlers[1]
        else:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            fh = logging.FileHandler(filename)
            logger.addHandler(fh)

        handler.setLevel(level)
        handler.setFormatter(LOG_FMT)
        fh.setLevel(level)
        fh.setFormatter(LOG_FMT)
        return level
