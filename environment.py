import time
from enum import Enum, unique

from playground import features
from rules import Winter_is_coming, MAX_APPLES_PER_PLAYER, MAX_APPLES_PER_SPOT
from setup import MINI_SETUP_TWO_PLAYERS, DEFAULT_SETUP, Location_type, Action
import numpy as np
from gym import spaces, Env
from gym.utils import seeding


# setup = MINI_SETUP_TWO_PLAYERS
# setup = DEFAULT_SETUP

def feature_selection_default(setup, current_player_id, state):
    return features(setup, current_player_id, state, normalize=False)


class Thingy(Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, setup=DEFAULT_SETUP, feature_selection=feature_selection_default,
                 seed=None):
        super(Thingy, self).__init__()  # Define action and observation space
        self.feature_selection = feature_selection
        self.setup = setup
        self.game = Winter_is_coming(setup=setup, seed=seed)
        self._actor_player = self.game.current_player

        # TODO
        self.action_space = len(self.game.action_space)
        self.observation_space = len(self.state())

    # TODO implement as the wrapper thing
    def fs(self, state):
        return self.feature_selection(self.setup, self._actor_player, state)

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
        self._actor_player = self.game.current_player
        return self.state()

    def render(self, mode='human', close=False):
        print(self.game.render())

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.game.np_random = self.np_random
        return [seed]


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
