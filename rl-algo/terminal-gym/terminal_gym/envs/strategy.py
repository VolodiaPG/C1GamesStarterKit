import gamelib
import random
import math
import warnings
from sys import maxsize
import json
import rpyc

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""


class AlgoStrategy(gamelib.AlgoCore, rpyc.Service):
    def __init__(self):
        super().__init__()

        self.playing_flag = True

        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

        self.conn = rpyc.connect('localhost', 4243)

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        gamelib.debug_write(config)
        # global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, BITS, CORES

        for k in range(6):
            type = config["unitInformation"][k]["shorthand"]
            self.ITOU[k] = type
            self.UTOI[type] = k

        # FILTER = config["unitInformation"][0]["shorthand"]
        # ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        # DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        # PING = config["unitInformation"][3]["shorthand"]
        # EMP = config["unitInformation"][4]["shorthand"]
        # SCRAMBLER = config["unitInformation"][5]["shorthand"]
        # BITS = 1
        # CORES = 0
        # This is a good place to do initial setup
        # self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        # game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.playing_flag = True
        

        # self.strategy(game_state)

        # game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def strategy(self, game_state):
        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)

    # def build_defences(self, game_state):
    #     """
    #     Build basic defenses using hardcoded locations.
    #     Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
    #     """
    #     # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
    #     # More community tools available at: https://terminal.c1games.com/rules#Download
    #
    #     # Place filters in front of destructors to soak up damage for them
    #     filter_locations = [[x,13] for x in range(0,28)]
    #     game_state.attempt_spawn(FILTER, filter_locations)
    #     # upgrade filters so they soak more damage
    #     game_state.attempt_upgrade(filter_locations)

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        self.conn.close()

    def exposed_perform_action(self, location, move_id):
        """
        Perform an action
        location : tuple
        move_id : the id of what should be spawned
        Returns wether or not the action has been performed
        """
        return self.game_state.attempt_spawn(self.moves[move_id], [location]) == 1

    def exposed_wrap_up_turn(self):
        self.playing_flag = False
        self.game_state.submit_turn()

    def exposed_get_map(self):
        """
        Gets the map of the game (simplified)
        :return: a simplified game map (all int, negative for the ennemy)
        """
        map = []
        ii = 0
        # TODO not taking into accound the fact that units can get stacked on one other
        for units in self.game_state.game_map:
            if units:
                unit = units[0]
                map[ii] = self.UTOI[unit.unit_type] * (1 if unit.player_index == 1 else -1)
            ii += 1

        return map

    def exposed_get_detail(self):
        """
        Gives the details about bits & cores of each players
        :return: a tuple of the 1st player bits & cores followed by the second's
        """
        return (gamelib.GameState.get_resources(ii)[jj] for jj in range(0, 2) for ii in range(1, 3))


if __name__ == "__main__":
    # algo = AlgoStrategy()
    # algo.start()
    from rpyc.utils.server import OneShotServer

    t = OneShotServer(AlgoStrategy(), port=4242)
    t.start()
