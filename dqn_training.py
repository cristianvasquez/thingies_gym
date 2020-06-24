import neptune
from absl.testing import absltest
import numpy as np

import acme
from acme import specs

from acme import wrappers

import sonnet as snt
from acme.utils import loggers

from agent import DQN
from neptune_logger import NeptuneLogger
from rules import Winter_is_coming
from setup import DEFAULT_REWARD_FUNCTION

import pathlib
import os
from absl import logging



neptune_enabled = True
num_episodes= 10

SETUP = {
    'grid_size_x': 4,
    'grid_size_y': 4,
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
        'in_the_wild_cost': 4,
        'in_a_house_cost': 0,
        'apples_growth': (3, 10)
        # number of apples that grow in the season `low` (inclusive) to `high` (exclusive).
    },
    'reward_function': DEFAULT_REWARD_FUNCTION
}

PARAMS = {
    'num_episodes': num_episodes,
    'setup': SETUP,

    # Epsilon greedy
    'epsilon': 0.05,

    # the number of observations to make before running a learner step.
    'samples_per_insert': 32.0,

    # Reverb table
    'priority_exponent': 0.6,
    'max_replay_size': 1000000,
    'min_replay_size': 1000,

    # replay client
    'batch_size': 256,
    'prefetch_size': 4,

    # adder (used to insert observations into replay)
    'n_step': 5,

    # DQNLearner params
    'importance_sampling_exponent': 0.2,
    'target_update_period': 100,
    'learning_rate': 1e-3,
    'discount': 0.99,

}



def do_example_run(game, agent, number_of_runs=3):
    for i in range(number_of_runs):
        timestep = game.reset()
        while not timestep.last():
            # Simple environment loop.
            action = agent.select_action(timestep.observation)
            timestep = game.step(action)
            print(game.render())


def run_dqn(experiment_name):
    checkpoint_dirs = (f'{current_dir}/data', experiment_name)

    game = Winter_is_coming(setup=PARAMS['setup'])
    environment = wrappers.SinglePrecisionWrapper(game)
    spec = specs.make_environment_spec(environment)
    # Construct the agent.

    def _make_network(action_spec: specs.DiscreteArray) -> snt.Module:
        return snt.Sequential([
            snt.Flatten(),
            snt.nets.MLP([50, 50, action_spec.num_values]),
        ])
    network = _make_network(spec.actions)

    if neptune_enabled:
        agent_logger = NeptuneLogger(label='DQN agent', time_delta=0.1)
        loop_logger = NeptuneLogger(label='Environment loop', time_delta=0.1)
        PARAMS['network']=f'{network}'
        neptune.init('cvasquez/sandbox')
        neptune.create_experiment(name='neptune_test', params=PARAMS)
    else:
        agent_logger = loggers.TerminalLogger('DQN agent', time_delta=1.)
        loop_logger = loggers.TerminalLogger('Environment loop', time_delta=1.)

    agent = DQN(
        environment_spec=spec,
        network=network,
        params = PARAMS,
        checkpoint=True,
        checkpoint_data=checkpoint_dirs,
        logger=agent_logger
    )
    # Try running the environment loop. We have no assertions here because all
    # we care about is that the agent runs without raising any errors.
    loop = acme.EnvironmentLoop(environment, agent, logger=loop_logger)
    loop.run(num_episodes=PARAMS['num_episodes'])

    if neptune_enabled:
        neptune.stop()

    do_example_run(game, agent)


current_dir = pathlib.Path().absolute()

if __name__ == '__main__':

    np.save('my_file.npy', SETUP)
    experiment_name = 'dqn_thingy_3'
    print(f'Experiment [{experiment_name}] started')
    run_dqn(experiment_name)
    print(f'Experiment [{experiment_name}] ended')



