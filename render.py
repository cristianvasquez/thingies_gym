from gym.utils import colorize
from tabulate import tabulate

from lib.random_emoji import random_emoji


class Winter_is_coming_renderer:
    def __init__(self, number_of_players):
        # Select player emoticons and names
        self.token_emojis = [random_emoji() for i in range(number_of_players)]

    def render(self, state=None, current_turn=None, current_player_id=None, playing_queue=None, is_terminal=False,
               ):
        grid, players, variant_state_info = state


        # build the grid and show it
        _grid_size_x, _grid_size_y, _ = grid.shape

        headers = [x for x in list(range(_grid_size_x))]
        table = []

        def render_coord(x, y):

            # Render Players
            spot = ''
            for i, ((_x, _y), apples, actions_left, active) in enumerate(players):
                if x == _x and y == _y:
                    if not active:
                        spot += f'thingy_{i} RIP\n'
                    else:
                        spot += f'-->THINGY_{i}<-- ({apples})\n' if i == current_player_id else f'thingy_{i} ({apples})\n'

            location_type = grid[x, y][0]
            apples = grid[x, y][1]

            l = {
                0: '',
                1: 'Tree',
                2: 'House',
                3: 'O_House',
                4: 'F_House'
            }
            if apples > 0:
                spot += f'{l[location_type]}({apples})\n'
            else:
                spot += f'{l[location_type]}\n'

            return spot

        for y in list(range(_grid_size_y)):
            table.append([render_coord(x, y) for x in list(range(_grid_size_x))])

        # coordinates, credits, actions_left, active_player = current_player
        status = f'current_turn:{current_turn}, variant_state_info:{variant_state_info}, playing_queue:{playing_queue}'

        if not is_terminal:
            ((_x, _y), apples, actions_left, active_player) = players[current_player_id]
            status += f'\ncurrent_player[{current_player_id}], coords: ({_x},{_y}), apples:({apples}), Actions left: {actions_left} '
        else:
            status += f'\nTerminal state'

        return '{}\n{}'.format(tabulate(table, headers, tablefmt="fancy_grid"), status)
