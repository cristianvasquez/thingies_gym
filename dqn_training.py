# python3
# Copyright 2018 DeepMind Technologies Limited. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for DQN agent."""

from absl.testing import absltest

import acme
from acme import specs
from acme.agents.tf import dqn
from acme.testing import fakes

from acme import wrappers
from acme.wrappers import SinglePrecisionWrapper
import numpy as np
import sonnet as snt

from rules import Winter_is_coming
from setup import DEFAULT_REWARD_FUNCTION


def _make_network(action_spec: specs.DiscreteArray) -> snt.Module:
    return snt.Sequential([
        snt.Flatten(),
        snt.nets.MLP([50, 50, action_spec.num_values]),
    ])


SETUP = {
    'grid_size_x': 3,
    'grid_size_y': 3,
    'number_of_players': 1,
    'number_of_houses': 2,
    'number_of_trees': 1,
    'initial_player_apples': 15,
    'apple_gathering_capacity': 5,
    'initial_apples_per_tree': 10,
    'actions_per_turn': 1,
    'turns_between_seasons': 10,
    'move_cost': 1,
    'death_zone': False,
    'summer': {
        'in_the_wild_cost': 1,
        'in_a_house_cost': 1,
        'apples_growth': (3, 10)
        # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'winter': {
        'in_the_wild_cost': 3,
        'in_a_house_cost': 0,
        'apples_growth': (3, 10)
        # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'reward_function': DEFAULT_REWARD_FUNCTION
}


class DQNTest(absltest.TestCase):

    def test_dqn(self):

        game = Winter_is_coming(setup=SETUP)
        environment = wrappers.SinglePrecisionWrapper(game)
        spec = specs.make_environment_spec(environment)

        # Construct the agent.
        agent = dqn.DQN(
            environment_spec=spec,
            network=_make_network(spec.actions),
            batch_size=10,
            samples_per_insert=2,
            min_replay_size=10,
            checkpoint=True
        )
        # Try running the environment loop. We have no assertions here because all
        # we care about is that the agent runs without raising any errors.
        loop = acme.EnvironmentLoop(environment, agent)
        loop.run(num_episodes=50000)

        # 20.000, 7 mins

        print("Done")
        for i in range(4):
            # play one cachero's episode
            timestep = game.reset()

            while not timestep.last():
                # Simple environment loop.
                action = agent.select_action(timestep.observation)
                timestep = game.step(action)
                print(timestep.observation)
                print(game.render())


if __name__ == '__main__':
    absltest.main()
