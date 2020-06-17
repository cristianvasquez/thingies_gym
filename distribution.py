import time

from rules import Winter_is_coming, MAX_APPLES_PER_PLAYER, MAX_APPLES_PER_TREE
from setup import MINI_SETUP_TWO_PLAYERS, DEFAULT_SETUP

setup = MINI_SETUP_TWO_PLAYERS
# setup = DEFAULT_SETUP

grid_size_x = setup['grid_size_x']
grid_size_y = setup['grid_size_y']
actions_per_turn = setup['actions_per_turn']
# turns_between_seasons = setup['turns_between_seasons']

game = Winter_is_coming(setup=setup)

def norm(value, max):
    return value / max


def dist(coord_1, coord_2):
    (x1, y1) = coord_1
    (x2, y2) = coord_2
    return (x2 - x1, y2 - y1)


def distribution_wrt_player(current_player_id, state, normalize=False):
    result = []
    players, houses, trees, current_season, turns_until_season_change = state

    (_x,_y), apples_p, actions_left_p, _ = players[current_player_id]

    # State of current player
    result.append(norm(_x, grid_size_x) if normalize else _x)
    result.append(norm(_y, grid_size_y) if normalize else _y)
    result.append(norm(apples_p, MAX_APPLES_PER_PLAYER) if normalize else apples_p)
    result.append(norm(actions_left_p, actions_per_turn) if normalize else actions_left_p)

    for _i, (_coords, apples, actions_left, active) in enumerate(players):
        if _i != current_player_id:
            (x, y) = dist((_x,_y),_coords)
            result.append(norm(x, grid_size_x) if normalize else x)
            result.append(norm(y, grid_size_y) if normalize else y)
            result.append(norm(apples, MAX_APPLES_PER_PLAYER) if normalize else apples)
            result.append(norm(actions_left, actions_per_turn) if normalize else actions_left)
            result.append(1 if active else 0)

    for i, (_coords, type) in enumerate(houses):
        (x, y) = dist((_x, _y), _coords)
        result.append(norm(x, grid_size_x) if normalize else x)
        result.append(norm(y, grid_size_y) if normalize else y)
        # result.append(type.value)

    for i, (_coords, apples) in enumerate(trees):
        (x, y) = dist((_x, _y), _coords)
        result.append(norm(x, grid_size_x) if normalize else x)
        result.append(norm(y, grid_size_y) if normalize else y)
        result.append(norm(apples, MAX_APPLES_PER_TREE) if normalize else apples)

    result.append(current_season.value)
    result.append(turns_until_season_change)
    return result


def distribution(state, normalize=False):
    result = []
    players, houses, trees, current_season, turns_until_season_change = state
    for _i, ((x, y), apples, actions_left, active) in enumerate(players):
        result.append(norm(x, grid_size_x) if normalize else x)
        result.append(norm(y, grid_size_y) if normalize else y)
        result.append(norm(apples, MAX_APPLES_PER_PLAYER) if normalize else apples)
        result.append(norm(actions_left, actions_per_turn) if normalize else actions_left)
        result.append(1 if active else 0)

    for i, ((x, y), type) in enumerate(houses):
        result.append(norm(x, grid_size_x) if normalize else x)
        result.append(norm(y, grid_size_y) if normalize else y)
        # result.append(type.value)

    for i, ((x, y), apples) in enumerate(trees):
        result.append(norm(x, grid_size_x) if normalize else x)
        result.append(norm(y, grid_size_y) if normalize else y)
        result.append(norm(apples, MAX_APPLES_PER_TREE) if normalize else apples)

    result.append(current_season.value)
    result.append(turns_until_season_change)
    return result


if __name__ == "__main__":
    current_player_id,state  = game.random_state()
    print(state)
    flatten = distribution_wrt_player(current_player_id,state, normalize=False)
    print(flatten)

# tic = time.perf_counter()
# for i in range(10000):
#     game.random_state()
# toc = time.perf_counter()
#
# print(f"done {toc - tic:0.4f} seconds")
