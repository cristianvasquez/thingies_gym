import time

from rules import Winter_is_coming, MAX_APPLES_PER_PLAYER, MAX_APPLES_PER_SPOT
from setup import MINI_SETUP_TWO_PLAYERS, DEFAULT_SETUP, Location_type
import numpy as np

# setup = MINI_SETUP_TWO_PLAYERS
setup = DEFAULT_SETUP

grid_size_x = setup['grid_size_x']
grid_size_y = setup['grid_size_y']
actions_per_turn = setup['actions_per_turn']
turns_between_seasons = setup['turns_between_seasons']

def n(value, max, normalize):
    return value / max if normalize else value


def dist(coord_1, coord_2):
    (x1, y1) = coord_1
    (x2, y2) = coord_2
    return (x2 - x1, y2 - y1)


def distribution_variant_info(variant_info, normalize=False):
    result = []
    v = {
        'Summer': 0,
        'Winter': 1
    }
    for variant, value in variant_info:
        result.append(v[variant])
        result.append(n(value, turns_between_seasons, normalize))
    return np.array(result)


def distribution_wrt_player(current_player_id, state, normalize=False):
    _grid, _players, _variant_info = state
    (_x, _y), apples_p, actions_left_p, _ = _players[current_player_id]

    # State of current player
    players = []
    players.append(n(_x, grid_size_x, normalize))
    players.append(n(_y, grid_size_y, normalize))
    players.append(n(apples_p, MAX_APPLES_PER_PLAYER, normalize))
    players.append(n(actions_left_p, actions_per_turn, normalize))

    for _i, (_coords, apples, actions_left, active) in enumerate(_players):
        if _i != current_player_id:
            (x, y) = dist((_x, _y), _coords)
            players.append(n(x, grid_size_x, normalize))
            players.append(n(y, grid_size_y, normalize))
            players.append(n(apples, MAX_APPLES_PER_PLAYER, normalize))
            players.append(n(actions_left, actions_per_turn, normalize))
            players.append(1 if active else 0)

    objects = []
    for __x, _a in enumerate(_grid):
        for __y, (type, apples) in enumerate(_a):
            if type != Location_type.EMPTY_WILDERNESS.value:
                (x, y) = dist((_x, _y), (__x, __y))
                # Add flattened types
                f_type = [1 if i.value == type else 0 for i in Location_type]
                objects += f_type
                objects.append(n(x, grid_size_x, normalize))
                objects.append(n(y, grid_size_y, normalize))
                objects.append(n(apples, MAX_APPLES_PER_SPOT, normalize))

    np_variant_info = distribution_variant_info(_variant_info, normalize=normalize)

    return np.concatenate(
        (np.array(players), np.array(objects), np_variant_info))


def distribution(state, normalize=False):
    _grid, _players, _variant_info = state

    players = []
    for _i, ((x, y), apples, actions_left, active) in enumerate(_players):
        players.append(n(x, grid_size_x, normalize))
        players.append(n(y, grid_size_y, normalize))
        players.append(n(apples, MAX_APPLES_PER_PLAYER, normalize))
        players.append(n(actions_left, actions_per_turn, normalize))
        players.append(1 if active else 0)

    np_variant_info = distribution_variant_info(_variant_info, normalize=normalize)
    return np.concatenate(
        (np.array(players), _grid.flatten(), np_variant_info))


if __name__ == "__main__":
    game = Winter_is_coming(setup=setup)

    current_player_id, state = game.random_state()
    flatten = distribution_wrt_player(current_player_id, state, normalize=True)
    print(flatten)

    # tic = time.perf_counter()
    # for i in range(10000):
    #     current_player_id, state = game.random_state()
    #     flatten = distribution(state, normalize=True)
    # toc = time.perf_counter()
    #
    # print(f"done {toc - tic:0.4f} seconds")
