from gym import spaces, Env
from gym.utils import seeding

from monopoly.board import Board
from monopoly.rules import ClassicMonopolyRules

DEFAULT_SETUP = {
    'board_file': 'monopoly/boards/default.csv',
    'number_of_players': 6,
    'max_money': 100000,
    'max_turns': 5000
}

SMALL_BOARD = {
    'board_file': 'monopoly/boards/board_small.csv',
    'number_of_players': 6,
    'max_money': 100000,
    'max_turns': 5000
}

class Monopoly(Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, config=DEFAULT_SETUP):
        super(Monopoly, self).__init__()  # Define action and observation space
        self.config = config
        self.board = Board(number_of_players=self.config['number_of_players'], board_file=self.config['board_file'])
        self.game = ClassicMonopolyRules(board=self.board, max_turns=self.config['max_turns'],
                                         max_money=self.config['max_money'])
        self.action_space = spaces.Discrete(len(self.game.actions))
        """
        A tuple (i.e., product) of simpler spaces

        Example usage:
        self.observation_space = spaces.Tuple((spaces.Discrete(2), spaces.Discrete(3)))
        """
        # TODO
        self.observation_space = spaces.Tuple((spaces.Discrete(2), spaces.Discrete(3)))

    def step(self, action):
        # Execute one time step within the environment
        return self.game.step(action)

    def state(self):
        return self.game.state()

    @staticmethod
    def flatten_state(state):
        players, properties, current_player, player_can_roll_dice, current_turn, max_turns = state
        res = []
        for position, money, active in players:
            res.append(position)
            res.append(money)
            res.append(1 if active else 0)
        for owner, houses in properties:
            res.append(owner if owner != None else len(players) + 1)  # an arbitrary non-existent player
            res.append(houses)
        res.append(current_player)
        res.append(1 if player_can_roll_dice else 0)
        res.append(current_turn)
        res.append(max_turns)
        return res

    def possible_actions(self):
        return self.game.possible_actions()

    def reset(self):
        self.game = ClassicMonopolyRules(board=self.board, max_turns=self.config['max_turns'],
                                         max_money=self.config['max_money'])
        return self.game.state()

    def render(self, mode='human', close=False):
        print(self.board.render(self.game))

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.game.np_random = self.np_random
        return [seed]
