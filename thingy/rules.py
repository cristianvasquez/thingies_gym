from typing import Any, List, Tuple

from gym.utils import seeding, colorize
from enum import Enum, unique

# Actions
from tabulate import tabulate

from util.random_emoji import random_emoji


@unique
class Actions(Enum):
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    COLLECT_CREDITS = 4
    BUY_HOUSE = 5
    DO_NOTHING = 6


@unique
class Seasons(Enum):
    SUMMER = 0
    WINTER = 1


class House_spec(Enum):
    BUY_PRICE_LB = 100
    BUY_PRICE_UB = 200
    RENT_PRICE_LB = 10
    RENT_PRICE_UB = 20


DEFAULT_SETUP = {
    'grid_size_x': 10,
    'grid_size_y': 10,
    'number_of_players': 6,
    'number_of_houses': 10,
    'initial_credits': 1000,
    'actions_per_turn': 5,
    'default_cost': 1,
    'winter_cost': 1,
    'move_cost': 1,
    'ticks_between_seasons': 5,
}


class Winter_is_coming():
    def __init__(self, setup=None, seed=None):
        if setup is None:
            setup = DEFAULT_SETUP
        self.np_random, seed = seeding.np_random(seed)

        self.grid_size_x = setup['grid_size_x']
        self.grid_size_y = setup['grid_size_y']
        self.actions_per_turn = setup['actions_per_turn']
        self.default_cost = setup['default_cost']
        self.winter_cost = setup['winter_cost']
        self.move_cost = setup['move_cost']
        self.ticks_between_seasons = setup['ticks_between_seasons']
        self.current_season = Seasons.SUMMER

        spots = [(x, y) for x in list(range(self.grid_size_x)) for y in list(range(self.grid_size_y))]

        # Allocate players
        player_positions = self.np_random.choice(len(spots), setup['number_of_players'], replace=False)
        # coordinates, credits, actions_left, active_player
        self.players = [(spots[i], setup['initial_credits'], self.actions_per_turn, True) for i in player_positions]

        # Allocate houses
        houses_positions = self.np_random.choice(len(spots), setup['number_of_houses'], replace=False)
        # coordinates, owner, buy_price, rent_price
        self.houses = [
            (spots[i], None, self.np_random.randint(House_spec.BUY_PRICE_LB.value, House_spec.BUY_PRICE_UB.value + 1),
             self.np_random.randint(House_spec.RENT_PRICE_LB.value, House_spec.RENT_PRICE_UB.value + 1)) for i in
            houses_positions]

        self.renderer = Winter_is_coming_renderer(len(self.players))
        self.current_turn = 0
        self.current_player = self._select_current_player()

    def _select_current_player(self):
        available = []
        for i, (_, _, actions_left, active) in enumerate(self.players):
            if active and actions_left > 0:
                available.append(i)
        return self.np_random.choice(available, 1, replace=False) if len(available) > 0 else None

    def possible_actions(self):
        return list(map(lambda x: x.value, list(Actions)))

    def step(self, action):
        return None

    def render(self):
        print(self.renderer.render(self.grid_size_x, self.grid_size_y, self.players, self.houses))


class Winter_is_coming_renderer:
    def __init__(self, number_of_players):
        # Select player emoticons and names
        self.token_emojis = [random_emoji() for i in range(number_of_players)]

    def render(self, grid_size_x, grid_size_y, players, houses):
        # build the grid and show it
        headers = [x for x in list(range(grid_size_x))]
        table = []

        def render_coord(x, y):
            spot = ' '
            for i, ((_x, _y), owner, buy_price, rent_price) in enumerate(houses):
                if x == _x and y == _y:
                    spot += '\n{}[{}]'.format('House', i)

            for i, ((_x, _y), credits, actions_left, active_player) in enumerate(players):
                if x == _x and y == _y:
                    player_name = self.token_emojis[i][2]
                    spot += '\n{}[{}]'.format('Thingy', i)

            return spot

        for y in list(range(grid_size_y)):
            table.append([render_coord(x, y) for x in list(range(grid_size_x))])

        return tabulate(table, headers, tablefmt="fancy_grid")


game = Winter_is_coming()

game.render()
