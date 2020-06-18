import time
from enum import Enum, unique

from rules import Winter_is_coming, MAX_APPLES_PER_PLAYER, MAX_APPLES_PER_SPOT
from setup import MINI_SETUP_TWO_PLAYERS, DEFAULT_SETUP, Location_type, Action
import numpy as np
from gym import spaces, Env
from gym.utils import seeding

# setup = MINI_SETUP_TWO_PLAYERS
setup = DEFAULT_SETUP

grid_size_x = setup['grid_size_x']
grid_size_y = setup['grid_size_y']
actions_per_turn = setup['actions_per_turn']
turns_between_seasons = setup['turns_between_seasons']


@unique
class Feature_selection(Enum):
    DEFAULT = 0
    DEFAULT_NORM = 1
    WRT_PLAYER = 2
    WRT_PLAYER_NORM = 3


class Thingy(Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, setup=DEFAULT_SETUP, feature_selection=Feature_selection.DEFAULT, seed=None):
        super(Thingy, self).__init__()  # Define action and observation space
        self.config = setup
        self.game = Winter_is_coming(setup=setup, seed=seed)
        self._actor_player = self.game.current_player

        self.feature_selection = feature_selection
        """
        A dictionary of simpler spaces.

        Example usage:
        self.observation_space = spaces.Dict({"position": spaces.Discrete(2), "velocity": spaces.Discrete(3)})

        Example usage [nested]:
        self.nested_observation_space = spaces.Dict({
            'sensors':  spaces.Dict({
                'position': spaces.Box(low=-100, high=100, shape=(3,)),
                'velocity': spaces.Box(low=-1, high=1, shape=(3,)),
                'front_cam': spaces.Tuple((
                    spaces.Box(low=0, high=1, shape=(10, 10, 3)),
                    spaces.Box(low=0, high=1, shape=(10, 10, 3))
                )),
                'rear_cam': spaces.Box(low=0, high=1, shape=(10, 10, 3)),
            }),
            'ext_controller': spaces.MultiDiscrete((5, 2, 2)),
            'inner_state':spaces.Dict({
                'charge': spaces.Discrete(100),
                'system_checks': spaces.MultiBinary(10),
                'job_status': spaces.Dict({
                    'task': spaces.Discrete(5),
                    'progress': spaces.Box(low=0, high=100, shape=()),
                })
            })
        })
        """
        # TODO
        self.action_space = len(self.game.action_space)
        self.observation_space = len(self.state())

    # TODO implement as the wrapper thing
    def fs(self, state):
        if self.feature_selection == Feature_selection.DEFAULT:
            return self.features(state, False)
        elif self.feature_selection == Feature_selection.DEFAULT_NORM:
            return self.features(state, True)
        elif self.feature_selection == Feature_selection.WRT_PLAYER:
            return self.features_wrt_player(self._actor_player, state, False)
        elif self.feature_selection == Feature_selection.WRT_PLAYER_NORM:
            return self.features_wrt_player(self._actor_player, state, True)
        return state

    def step(self, action: int):
        state, reward, terminal, (player_died) = self.game.do_action(action)
        result = self.fs(state), reward, terminal, (player_died)
        self._actor_player = self.game.current_player
        # Execute one time step within the environment
        return result

    def state(self):
        return self.fs(self.game.state())

    def reset(self):
        self.game.reset()
        return self.state()

    def render(self, mode='human', close=False):
        print(self.game.render())

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.game.np_random = self.np_random
        return [seed]

    @staticmethod
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

    @staticmethod
    def features(state, normalize=False):
        _grid, _players, _variant_info = state

        players = []
        for _i, ((x, y), apples, actions_left, active) in enumerate(_players):
            players.append(n(x, grid_size_x, normalize))
            players.append(n(y, grid_size_y, normalize))
            players.append(n(apples, MAX_APPLES_PER_PLAYER, normalize))
            players.append(n(actions_left, actions_per_turn, normalize))
            players.append(1 if active else 0)

        np_variant_info = Thingy.distribution_variant_info(_variant_info, normalize=normalize)
        return np.concatenate(
            (np.array(players), _grid.flatten(), np_variant_info))

    @staticmethod
    def features_wrt_player(current_player_id, state, normalize=False):
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

        np_variant_info = Thingy.distribution_variant_info(_variant_info, normalize=normalize)

        return np.concatenate(
            (np.array(players), np.array(objects), np_variant_info))


def n(value, max, normalize):
    return value / max if normalize else value


def dist(coord_1, coord_2):
    (x1, y1) = coord_1
    (x2, y2) = coord_2
    return (x2 - x1, y2 - y1)


if __name__ == "__main__":
    thingy = Thingy(setup=MINI_SETUP_TWO_PLAYERS, feature_selection=Feature_selection.WRT_PLAYER_NORM)
    print(thingy.observation_space)
    print(thingy.action_space)

    state, reward, terminal, (player_died) = thingy.step(Action.MOVE_DOWN.value)

    print(state)

    # tic = time.perf_counter()
    # for i in range(10000):
    #     current_player_id, state = game.random_state()
    #     flatten = distribution(state, normalize=True)
    # toc = time.perf_counter()
    #
    # print(f"done {toc - tic:0.4f} seconds")
