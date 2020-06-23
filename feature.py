import numpy as np
from functools import partial

from setup import MAX_APPLES_PER_USER, Location_type, MAX_APPLES_PER_SPOT


def n(value, max, normalize):
    return value / max if normalize else value


def dist(coord_1, coord_2):
    (x1, y1) = coord_1
    (x2, y2) = coord_2
    return (x2 - x1, y2 - y1)


def distribution_variant_info(setup, variant_info, normalize=False):
    turns_between_seasons = setup['turns_between_seasons']

    variant_info = []
    for variant, value in variant_info:
        variant_info.append(variant)
        variant_info.append(n(value, turns_between_seasons, normalize))
    return np.array(variant_info, dtype=np.float32)


def features_n(setup, current_player_id, state):
    return features(setup, current_player_id, state, normalize=True)


def features(setup, current_player_id, state, normalize=False):
    _grid, _players, _variant_info = state
    grid_size_x = setup['grid_size_x']
    grid_size_y = setup['grid_size_y']
    actions_per_turn = setup['actions_per_turn']

    players = []
    for _i, ((x, y), apples, actions_left, active) in enumerate(_players):
        players.append(n(x, grid_size_x, normalize))
        players.append(n(y, grid_size_y, normalize))
        players.append(n(apples, MAX_APPLES_PER_USER, normalize))
        players.append(n(actions_left, actions_per_turn, normalize))
        players.append(1 if active else 0)

    np_variant_info = distribution_variant_info(setup, _variant_info, normalize=normalize)
    return np.concatenate(
        (np.array(players, dtype=np.float32), _grid.flatten(), np_variant_info))


def features_wrt_player_n(setup, current_player_id, state):
    return features_wrt_player(setup, current_player_id, state, normalize=True)


def features_wrt_player(setup, current_player_id, state, normalize=False):
    grid_size_x = setup['grid_size_x']
    grid_size_y = setup['grid_size_y']
    actions_per_turn = setup['actions_per_turn']
    _grid, _players, _variant_info = state
    (_x, _y), apples_p, actions_left_p, _ = _players[current_player_id]

    # State of current player
    players = []
    players.append(n(_x, grid_size_x, normalize))
    players.append(n(_y, grid_size_y, normalize))
    players.append(n(apples_p, MAX_APPLES_PER_USER, normalize))
    players.append(n(actions_left_p, actions_per_turn, normalize))

    for _i, (_coords, apples, actions_left, active) in enumerate(_players):
        if _i != current_player_id:
            (x, y) = dist((_x, _y), _coords)
            players.append(n(x, grid_size_x, normalize))
            players.append(n(y, grid_size_y, normalize))
            players.append(n(apples, MAX_APPLES_PER_USER, normalize))
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

    np_variant_info = distribution_variant_info(setup, _variant_info, normalize=normalize)

    return np.concatenate(
        (np.array(players), np.array(objects), np_variant_info))
