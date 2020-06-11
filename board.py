import random

from gym.utils import seeding, colorize
# from termcolor import colored
from tabulate import tabulate
from pandas import pandas as pd
from random_emoji import random_emoji


# The classic board game
class Board():
    def __init__(self, board_file='board.csv', number_of_players=10):

        self.board_specs = pd.read_csv(board_file).to_dict('records')

        self.number_of_locations = len(self.board_specs)
        self.number_of_players = number_of_players
        self.token_emojis = [random_emoji() for i in range(0, number_of_players + 1)]

    def location(self, index):
        return self.board_specs[index]

    def player_name(self, player):
        name = self.token_emojis[player][2]
        return colorize(name, 'crimson')

    def location_name(self, index):
        location = self.location(index)
        color_mapping = {
            'Brown': ('magenta', True, False),
            'Dark Blue': ('blue', True, False),
            'Green': ('green', True, False),
            'Light Blue': ('crimson', True, False),

            'Orange': ('cyan', True, False),
            'Pink': ('white', True, False),
            'Yellow': ('yellow', True, False),
            'Red': ('red', True, False),

            'None': ('cyan', False, True),
            'Railroad': ('yellow', False, True),
            'Utility': ('white', False, True),
        }

        color, bold, highlight = color_mapping[location['monopoly']]
        return (colorize(location['name'], color, highlight=highlight, bold=bold))

    # class ,name, position, monopoly, monopoly_size, price, build_cost, rent, rent_house_1, rent_house_2, rent_house_3, rent_house_4, rent_hotel, default_income
    def render(self, state):

        buildings_mapping = {
            0: 'N/A',
            1: '🏠',
            2: '🏠🏠',
            3: '🏠🏠🏠',
            4: '🏠🏠🏠🏠',
            5: '🏨'
        }

        headers = ["owner", "name", "tokens", "buildings", "rent"]
        table = []

        for position, row in enumerate(self.board_specs):
            tokens = ''
            (owner, buildings) = state.properties[position]

            # The owner
            owner_str = '' if owner == 0 else self.token_emojis[owner][0]

            # The tokens (players)
            for player, (player_position, money, active) in enumerate(state.players):
                if position == player_position:
                    (emoji, emoji_codepoint, emoji_name) = self.token_emojis[player]
                    tokens = tokens + '{} {}\n'.format(emoji, '(${})'.format(money) if active else 'RIP')

            # The location name
            location_name = self.location_name(position)

            # The buildings
            rent_str = '{}({})'.format(state.get_rent_amount(buildings, row),buildings_mapping[buildings]) if row['class'] == 'Street' else ''
            table.append([owner_str, location_name, tokens, rent_str ])
        return tabulate(table, headers, tablefmt="fancy_grid")